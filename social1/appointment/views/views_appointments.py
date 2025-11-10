from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import TestForm
from django.contrib import messages
from datetime import datetime, time, timedelta
from ..models import Usluge, Frizer, Termin, Notification, Review
from django.core.serializers import serialize
import json
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Avg, Count


def get_next_free_slot(frizer_id, days_ahead=7):
    """
    Calculate next available time slot for a barber
    Looking ahead for the specified number of days
    """
    today = datetime.now().date()
    
    # Working hours: 10:00 - 19:00 (Monday to Saturday, Friday is off - from JS validation)
    working_start = time(10, 0)
    working_end = time(19, 0)
    slot_duration = timedelta(minutes=30)  # Default appointment duration

    for day_offset in range(days_ahead):
        check_date = today + timedelta(days=day_offset)
        
        # Skip Fridays (day 4 in weekday(), 0=Monday)
        if check_date.weekday() == 4:  # Friday
            continue

        
        # Get existing appointments for this barber on this date
        existing_appointments = Termin.objects.filter(
            frizer_id=frizer_id, 
            datum=check_date
        ).order_by('vreme')
        
        # Generate time slots for the day
        current_time = datetime.combine(check_date, working_start)
        end_time = datetime.combine(check_date, working_end)
        
        while current_time < end_time:
            current_time_only = current_time.time()
            
            # Check if this slot is free
            is_free = True
            for appointment in existing_appointments:
                appointment_start = datetime.combine(check_date, appointment.vreme)
                appointment_duration = appointment.usluga.duzina if appointment.usluga else timedelta(minutes=30)
                appointment_end = appointment_start + appointment_duration
                
                # Check for overlap
                slot_end = current_time + slot_duration
                if (current_time < appointment_end and slot_end > appointment_start):
                    is_free = False
                    break
            
            if is_free:
                if check_date == today:
                    # For today, only show slots that are at least 1 hour from now
                    now = datetime.now()
                    if current_time > now + timedelta(hours=1):
                        return {
                            'date': check_date,
                            'time': current_time_only,
                            'formatted': f"{'Danas' if check_date == today else check_date.strftime('%d.%m')} {current_time_only.strftime('%H:%M')}"
                        }
                else:
                    return {
                        'date': check_date,
                        'time': current_time_only,
                        'formatted': f"{check_date.strftime('%d.%m')} {current_time_only.strftime('%H:%M')}"
                    }
            
            current_time += slot_duration
    
    # If no free slots found in the next week
    return {
        'date': None,
        'time': None,
        'formatted': "Nema slobodnih termina"
    }


@login_required(redirect_field_name='user_login/')
def potvrdi(request):
    sada = datetime.now()
    viewname = "potvrdi"
    form = TestForm()
    usluga = request.session.get('usluga')
    frizer = request.session.get('frizer')
    datum = request.session.get('datum')
    dodatne_usluge = request.session.get('dodatne_usluge', [])
    duration = Usluge.objects.get(pk=usluga).duzina.total_seconds()
    termini = Termin.objects.filter(frizer=frizer,datum=datum)
    termini_2 = []
    
    # Calculate loyalty message for second step
    try:
        current_appointments = Termin.objects.filter(user=request.user).count()
        next_appointment_number = current_appointments + 1
        
        # Calculate appointments remaining until next free appointment
        # Free appointments are: 15th, 30th, 45th, etc.
        if next_appointment_number % 15 == 0 and next_appointment_number > 0:
            # Next appointment is free
            loyalty_message = f"🎁 Čestitamo! Vaš sledeći termin (#{next_appointment_number}) je BESPLATAN!"
        else:
            # Calculate how many more appointments needed
            appointments_until_free = 15 - (current_appointments % 15)
            if appointments_until_free == 1:
                loyalty_message = f"⭐ Još samo 1 termin do besplatnog! (trenutno imate {current_appointments} termina)"
            else:
                loyalty_message = f"📊 Još {appointments_until_free} termina do besplatnog! (trenutno imate {current_appointments} termina)"
    except Exception as e:
        loyalty_message = "Prijavite se da vidite informacije o besplatnim terminima"

    try:
        ter = f"{termini[0].vreme}".split(":")

        for ter in termini:
            pocetak = datetime.strptime(f"{ter.datum} {ter.vreme}", '%Y-%m-%d %H:%M:%S')
            kraj = pocetak + ter.usluga.duzina

            termini_2.append({
                "pocetak": f"{pocetak.strftime('%H:%M:%S')}",
                "kraj": f"{kraj.strftime('%H:%M:%S')}"
            })
    except  Exception as e: print(e)

    if request.method == 'POST':
        if 'zakazi_termin' in request.POST:
            # Validate booking date is within 30 days
            try:
                booking_date = datetime.strptime(datum, '%Y-%m-%d').date()
                today = sada.date()
                max_booking_date = today + timezone.timedelta(days=30)
                
                if booking_date < today:
                    messages.error(request, "Ne možete zakazati termin u prošlosti", extra_tags='danger')
                    return redirect('potvrdi')
                elif booking_date > max_booking_date:
                    messages.error(request, "Možete zakazati termin maksimalno 30 dana unapred", extra_tags='danger')
                    return redirect('potvrdi')
            except ValueError:
                messages.error(request, "Neispravno unet datum", extra_tags='danger')
                return redirect('potvrdi')
            
            name = ""
            broj_telefona = ""
            if request.user.is_superuser:
                name = request.POST['name']
                broj_telefona = request.POST['broj_telefona']
            else:
                name = request.user.ime_prezime
                broj_telefona = request.user.broj_telefona
            params = {
                'user': request.user,
                'usluga': usluga,
                'frizer':frizer,
                'datum':datum,
                'name':name,
                'vreme':request.POST['vreme'],
                'poruka': request.POST['poruka'],
                'godina': sada.year,
                'mesec': format(sada.month, "02d"),
                'dan': format(sada.day, "02d"),                
                'broj_telefona':broj_telefona,
                'dodatne_usluge': dodatne_usluge
            }
            data = TestForm(params)
            if data.is_valid():              
                saved_appointment = data.save()
                vreme_za_poruku = datetime.strptime(request.POST['vreme'][:5],"%H:%M")
                za_disp = f"{vreme_za_poruku.hour}:{vreme_za_poruku.minute}"
                messages.success(request,f"Uspešno ste zakazali termin {datum} u {za_disp}")
                
                # Create notification
                Notification.objects.create(
                    user=request.user,
                    title="Novi termin",
                    message=f"Uspešno ste zakazali termin {datum} u {za_disp} sa frizerom {Frizer.objects.get(pk=frizer).name} za uslugu {Usluge.objects.get(pk=usluga).name}.",
                )
                
                # Send confirmation email
                if request.user.email and request.user.is_email_verified:
                    try:
                        dodatne_usluge_objects = []
                        if dodatne_usluge:
                            dodatne_usluge_objects = Usluge.objects.filter(id__in=dodatne_usluge)
                        
                        # Prepare email context
                        email_context = {
                            'user': request.user,
                            'appointment': saved_appointment,
                            'dodatne_usluge_objects': dodatne_usluge_objects,
                            'loyalty_message': loyalty_message,
                        }
                        
                        # Render HTML email template
                        html_message = render_to_string('appointment/emails/appointment_confirmation.html', email_context)
                        
                        # Create and send email
                        email = EmailMessage(
                            subject=f'Potvrda termina - {saved_appointment.datum.strftime("%d.%m.%Y")} u {saved_appointment.vreme.strftime("%H:%M")}',
                            body=html_message,
                            from_email=settings.EMAIL_HOST_USER,
                            to=[request.user.email],
                        )
                        email.content_subtype = "html"  # Set content type to HTML
                        email.send()
                        
                        import logging
                        logger = logging.getLogger('appointment.email')
                        logger.info(f"Confirmation email sent successfully to {request.user.email} for appointment {saved_appointment.id}")
                        
                    except Exception as e:
                        import logging
                        logger = logging.getLogger('appointment.email')
                        logger.error(f"Failed to send confirmation email to {request.user.email}: {str(e)}", exc_info=True)
                        # Don't show error to user as appointment was still created successfully
                
                return redirect('termin')
            else:
                messages.error(request, "Greska na serveru, pokusajte ponovo", extra_tags='danger')

    # Create a temporary Termin instance to calculate pricing
    temp_termin = Termin(
        usluga_id=usluga,
        dodatne_usluge=dodatne_usluge or []
    )
    
    # Get service information using the new model methods
    all_services = temp_termin.all_services
    ukupna_cena = temp_termin.calculate_total_price()
    
    # Prepare data for template compatibility
    dodatne_usluge_nazivi = []
    dodatne_usluge_info = []
    glavna_usluga_info = None
    
    for service in all_services:
        if service['is_main']:
            glavna_usluga_info = {'name': service['name'], 'cena': service['price']}
        else:
            dodatne_usluge_nazivi.append(service['name'])
            dodatne_usluge_info.append({'name': service['name'], 'cena': service['price']})

    context = {
        'filtered_list': json.dumps(list(termini_2)),
        'viewname': viewname,
        'form':form,
        'duration':duration,
        'dodatne_usluge_nazivi': dodatne_usluge_nazivi,
        'dodatne_usluge_info': dodatne_usluge_info,
        'glavna_usluga_info': glavna_usluga_info,
        'ukupna_cena': ukupna_cena,
        'has_multiple_services': temp_termin.has_multiple_services,
        'all_services': all_services,
        'termin_counter': loyalty_message

    }
    return render(request, 'appointment/zakazivanje.html',context)


@login_required(redirect_field_name='user_login/')
def termin(request):
    
    viewname = "termin"
    sada = datetime.now()
    termini = []
    form_filter = TestForm()

    is_next_free = False

    try:
        current_appointments = Termin.objects.filter(user=request.user).count()
        next_appointment_number = current_appointments + 1
        
        # Calculate appointments remaining until next free appointment
        # Free appointments are: 15th, 30th, 45th, etc.
        if next_appointment_number % 15 == 0 and next_appointment_number > 0:
            # Next appointment is free
            is_next_free = f"🎁 Čestitamo! Vaš sledeći termin (#{next_appointment_number}) je BESPLATAN!"
        else:
            # Calculate how many more appointments needed
            appointments_until_free = 15 - (current_appointments % 15)
            if appointments_until_free == 1:
                is_next_free = f"⭐ Još samo 1 termin do besplatnog! (trenutno imate {current_appointments} termina)"
            else:
                is_next_free = f"📊 Još {appointments_until_free} termina do besplatnog! (trenutno imate {current_appointments} termina)"
            
        termin_counter = next_appointment_number
    except Exception as e:
        termin_counter = 0
        is_next_free = "Prijavite se da vidite informacije o besplatnim terminima"
        print("User not logged in")

    print(termin_counter)

    # Get next free slot for each barber
    frizeri_with_slots = []
    all_frizeri = Frizer.objects.all()
    for frizer in all_frizeri:
        next_slot = get_next_free_slot(frizer.id)
        frizeri_with_slots.append({
            'frizer': frizer,
            'next_free_slot': next_slot['formatted']
        })

    if request.method == 'POST':
        #check if first form button is clicked
        if 'form_filter_button' in request.POST:
            # Sharing parameters between  views
            request.session['frizer'] = request.POST['frizer']
            request.session['datum'] = request.POST['datum']
            request.session['usluga'] = request.POST['usluga']
            
            # Prikupi dodatne usluge
            dodatne_usluge = []
            for key, value in request.POST.items():
                if key.startswith('dodatna_usluga_') and value:
                    dodatne_usluge.append(int(value))
            
            # Ograniči na maksimalno 3 dodatne usluge
            if len(dodatne_usluge) > 3:
                dodatne_usluge = dodatne_usluge[:3]
                
            request.session['dodatne_usluge'] = dodatne_usluge
            # - Sortiranje zauzetih termina -
            return redirect(potvrdi)

    context = {
        'viewname': viewname,
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'form': form_filter,
        "termin_counter": is_next_free,
        'frizeri_with_slots': frizeri_with_slots,
    }
    return render(request, 'appointment/zakazivanje.html', context)


def zakazi(request):
    viewname = "zakazi"
    sada = datetime.now()

    usluge = Usluge.objects.all()
    
    # Organize services by category
    usluge_sisanje = usluge.filter(kategorija='sisanje')
    usluge_brada = usluge.filter(kategorija='brada')
    usluge_ostale = usluge.filter(kategorija='ostale_usluge')
    usluge_vip = usluge.filter(kategorija='vip_usluge')

    frizeri = Frizer.objects.all()
    interval = 30

    if request.method == 'POST':
        if 'kontakt_mail' in request.POST:
            # Render professional email template
            email_body = render_to_string('appointment/emails/contact_email.html', {
                'name': request.POST.get('Name', ''),
                'email': request.POST.get('Email', ''),
                'subject': request.POST.get('Subject', ''),
                'message': request.POST.get('Message', ''),
                'timestamp': timezone.now()
            })
            
            poruka = EmailMessage(
                subject=f"Nova poruka sa sajta: {request.POST.get('Subject', 'Bez teme')}",
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=['hasko83@gmail.com']
            )
            poruka.content_subtype = 'html'  # Enable HTML content
            poruka.send()

    # Calculate max booking date (30 days from today)
    max_date = (sada + timezone.timedelta(days=30)).strftime('%Y-%m-%d')
    min_date = sada.strftime('%Y-%m-%d')
    
    # Get review data for landing page section
    reviews = Review.objects.filter(is_approved=True).select_related('user')[:6]  # Show latest 6 reviews
    review_stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    if review_stats['average_rating']:
        review_stats['average_rating'] = round(review_stats['average_rating'], 1)
    else:
        review_stats['average_rating'] = 0
    
    context = {
        'viewname': viewname,
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'usluge': usluge,
        'frizeri': frizeri,
        'usluge_sisanje': usluge_sisanje,
        'usluge_brada': usluge_brada,
        'usluge_ostale': usluge_ostale,
        'usluge_vip': usluge_vip,
        'max_date': max_date,
        'min_date': min_date,
        'reviews': reviews,
        'review_stats': review_stats,
    }
    return render(request, 'appointment/jqr.html', context)


def otkazivanje(request, termin_id):
    termin = Termin.objects.get(pk=termin_id)
    termin.delete()
    return redirect('zafrizera')


@login_required(redirect_field_name='user_login/')
def zafrizera(request):
    return redirect('opcije_termini')

def help_page(request):
    if request.method == 'POST':
        if 'kontakt_mail' in request.POST:
            # Render professional email template
            email_body = render_to_string('appointment/emails/contact_email.html', {
                'name': request.POST.get('Name', ''),
                'email': request.POST.get('Email', ''),
                'subject': request.POST.get('Subject', ''),
                'message': request.POST.get('Message', ''),
                'timestamp': timezone.now()
            })
            
            poruka = EmailMessage(
                subject=f"Nova poruka sa sajta: {request.POST.get('Subject', 'Bez teme')}",
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=['hasko83@gmail.com']
            )
            poruka.content_subtype = 'html'  # Enable HTML content
            poruka.send()
            messages.success(request, "Poruka je uspešno poslata!")
            return redirect('help_page')
    return render(request, 'appointment/help_page.html')
