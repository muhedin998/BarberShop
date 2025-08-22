from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from ..forms import TestForm
from datetime import datetime, timedelta
from ..models import Korisnik, Usluge, Frizer, Termin, Duznik, Notification
from django.db.models import Sum, Q
from django.db import models


def opcije_termini(request):
    frizer = []
    if request.user.username == "hasko123":
        frizer = Frizer.objects.get(name="Hasredin Bećirović")
    if request.user.username == "Muvehid":
        frizer = Frizer.objects.get(name="Muvehid Bećirović")
    if request.user.username == "admin":
        frizer = Frizer.objects.get(name="(bez imena)")

    za_otkazivanje = Usluge.objects.get(pk=15)
    if request.method =='POST':
        form_type = request.POST.get('form_type')
        if form_type == 'form1':
            form = TestForm()
            name = "OTKAZAN DAN"
            broj_telefona = ""
            params = {
                'user': request.user,
                'usluga': za_otkazivanje,
                'frizer':frizer,
                'datum':request.POST['datum'],
                'name':name,
                'poruka': request.POST['poruka'],
                'vreme':'09:00:00',
                'broj_telefona':broj_telefona
                }
            form = TestForm(params)
            if form.is_valid():
                form.save()
        elif form_type == 'form2':
            try:
                user = Korisnik.objects.get(id = request.POST['user_id'])
            except Exception as e:
                print(e)
                user = None
            if user:
                debt_amount = int(request.POST['duguje'])
                if user.dugovanje is not None:
                    user.dugovanje += debt_amount
                    user.save()
                    user.refresh_from_db()  # Reload from DB
                else:
                    user.dugovanje = debt_amount
                    user.save()
                    user.refresh_from_db()  # Reload from DB
                
                # Create notification for the user about the new debt
                Notification.objects.create(
                    user=user,
                    title="Novo dugovanje dodano",
                    message=f"Dodano je novo dugovanje u iznosu od {debt_amount} RSD. Ukupno dugovanje: {user.dugovanje} RSD."
                )
            else:
                duznik, created = Duznik.objects.get_or_create(
                name=request.POST['ime_prezime'],
                broj_telefona=request.POST['broj_telefona'],
                defaults={"duguje": request.POST['duguje']}
            )

                if created:
                    print("Sačuvano!")  # New record created
                else:
                    duznik.duguje += int(request.POST['duguje'])  # Convert to int before adding
                    duznik.save()

                    print("Dužnik već postoji! Povećano duguje!")
                
                # Note: For guest users (Duznik), we cannot create notifications
                # since they don't have user accounts. The notification will be
                # created when/if they register and their debt is transferred.

    if request.user.is_authenticated:
        if request.user.is_superuser:
            termini = Termin.objects.all().order_by('datum','vreme').exclude(datum__lt=datetime.now().date()).filter(frizer=frizer)

        else:
            # Check if user is a frizer (specific usernames)
            frizer_object = None
            if request.user.username == "hasko123":
                frizer_object = Frizer.objects.get(name="Hasredin Bećirović")
            elif request.user.username == "Muvehid":
                frizer_object = Frizer.objects.get(name="Muvehid Bećirović")
            elif request.user.username == "admin":
                frizer_object = Frizer.objects.get(name="(bez imena)")
            
            if frizer_object:
                # Frizer view - show appointments assigned to them
                termini = Termin.objects.all().order_by('datum','vreme').exclude(datum__lt=datetime.now().date()).filter(frizer=frizer_object)
            else:
                # Regular customer view - show their own appointments
                termini = Termin.objects.filter(user=request.user).order_by('datum','vreme').exclude(datum__lt=datetime.now().date())
    else:
        return redirect('zakazi')
    
    # Dodaj dodatne usluge objekti za svaki termin
    for termin in termini:
        if termin.dodatne_usluge:
            termin.dodatne_usluge_objekti = Usluge.objects.filter(id__in=termin.dodatne_usluge)
        else:
            termin.dodatne_usluge_objekti = []
    
    context = {'termini':termini}

    return render(request, 'appointment/opcije/termini.html', context)


def opcije_klijenti(request):
    user_id = request.GET.get('user_id')

    users = Korisnik.objects.all()
    count = Korisnik.objects.count()

    if (user_id):
        usr = Korisnik.objects.filter(id=user_id).first()
        usr = Korisnik.objects.get(id=usr.id)  # Forces re-fetch
        broj_termina = Termin.objects.filter(user=usr)
        ukupno = 0
        for termin in broj_termina:
            ukupno += termin.effective_price
        usr.refresh_from_db()
        context = {
            'users': users,
            'count': count,
            'user_view': usr,
            'broj_termina': broj_termina.count(),
            'ukupno': ukupno }
        return render(request, 'appointment/opcije/klijenti.html',context)

    return render(request, 'appointment/opcije/klijenti.html',{'users': users, 'count': count})


@user_passes_test(lambda u: u.is_superuser)
def opcije_izvestaj(request):
    today = datetime.now().date()
    
    # Get period from request, default to 30 days
    period = request.GET.get('period', '30')
    view_type = request.GET.get('view', 'earnings')
    selected_barber = request.GET.get('barber', 'all')
    
    # Determine user role and permissions
    # Staff users who can choose between all barbers
    staff_usernames = ["admin", "hasko123", "Muvehid", "Elvedin", "Edo", "ElvedinAlic", "elvedin7", "elvedin2", "elvedin8", "Hodzic"]  # Add other staff usernames as needed
    is_staff = request.user.username in staff_usernames
    is_hasredin = request.user.username == "hasko123"
    is_muvehid = request.user.username == "Muvehid"
    
    # Get all barbers/staff for staff dropdown
    all_barbers = []
    if is_staff:
        # Get all staff and superuser accounts for selection
        staff_and_superusers = Korisnik.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        ).distinct()
        
        for user in staff_and_superusers:
            # Map usernames to readable names and IDs for URL parameters
            if user.username == 'hasko123':
                all_barbers.append({'id': 'hasredin', 'name': 'Hasredin Bećirović'})
            elif user.username == 'Muvehid':
                all_barbers.append({'id': 'muvehid', 'name': 'Muvehid Bećirović'})
            elif user.username == 'admin':
                all_barbers.append({'id': 'admin', 'name': 'Admin'})
            # Emil removed - no longer superuser
        
        # Add option to view all together
        all_barbers.append({'id': 'all', 'name': 'Svi zajedno'})
    
    # Both main barbers (Hasredin and Muvehid) are now staff and can choose between all barbers
    # No restrictions needed - all staff can choose any barber
    
    context = {
        'current_period': period,
        'current_view': view_type,
        'today': today,
        'selected_barber': selected_barber,
        'all_barbers': all_barbers,
        'is_staff': is_staff,
        'is_hasredin': is_hasredin,
        'is_muvehid': is_muvehid,
    }
    
    if view_type == 'debtors':
        # Handle debtors view
        duznici = Duznik.objects.all()
        duznici_kor = Korisnik.objects.filter(dugovanje__gt=0)
        total_debt = sum(d.duguje for d in duznici) + sum(d.dugovanje for d in duznici_kor)
        
        context.update({
            'duznici': duznici,
            'duznici_kor': duznici_kor,
            'total_debt': total_debt,
            'total_debtors': len(duznici) + len(duznici_kor)
        })
    else:
        # Handle earnings view
        days = int(period)
        start_date = today - timedelta(days=days)
        
        # Get base queryset for appointments in date range
        termini_queryset = Termin.objects.filter(datum__range=[start_date, today])
        
        # Apply barber filter based on selection
        if selected_barber == 'hasredin':
            hasredin_frizer = Frizer.objects.get(name="Hasredin Bećirović")
            termini_queryset = termini_queryset.filter(frizer=hasredin_frizer)
        elif selected_barber == 'muvehid':
            muvehid_frizer = Frizer.objects.get(name="Muvehid Bećirović")
            termini_queryset = termini_queryset.filter(frizer=muvehid_frizer)
        elif selected_barber == 'admin':
            # Admin doesn't have a Frizer record, filter by user appointments
            admin_user = Korisnik.objects.get(username="admin")
            termini_queryset = termini_queryset.filter(user=admin_user)
        # If 'all' or staff viewing all, don't filter by barber
        
        # Get all termini in the period for manual calculation
        termini_list = list(termini_queryset.select_related('usluga', 'frizer'))
        
        # Calculate earnings per day manually using effective_price
        earnings_by_date = {}
        total_earnings = 0
        
        for termin in termini_list:
            date_key = termin.datum
            price = termin.effective_price
            
            if date_key not in earnings_by_date:
                earnings_by_date[date_key] = {
                    'datum': date_key,
                    'total_earnings': 0,
                    'barber_breakdown': {}
                }
            
            earnings_by_date[date_key]['total_earnings'] += price
            total_earnings += price
            
            # Track earnings by barber for detailed view
            barber_name = termin.frizer.name if termin.frizer else "Nepoznato"
            if barber_name not in earnings_by_date[date_key]['barber_breakdown']:
                earnings_by_date[date_key]['barber_breakdown'][barber_name] = 0
            earnings_by_date[date_key]['barber_breakdown'][barber_name] += price
        
        # Convert to list and sort by date descending
        earnings_per_day = sorted(earnings_by_date.values(), key=lambda x: x['datum'], reverse=True)
        
        avg_daily = total_earnings / days if days > 0 else 0
        
        context.update({
            'earnings_data': earnings_per_day,
            'total_earnings': total_earnings,
            'avg_daily_earnings': avg_daily,
            'period_days': days
        })
    
    return render(request, 'appointment/opcije/izvestaj.html', context)


@login_required
def opcije_istorija(request):
    termini_list = Termin.objects.filter(user=request.user).order_by('-datum', '-vreme')
    paginator = Paginator(termini_list, 50)  # Show 10 images per page

    page_number = request.GET.get('page')
    termini = paginator.get_page(page_number)
    
    # Dodaj dodatne usluge objekti za svaki termin
    for termin in termini:
        if termin.dodatne_usluge:
            termin.dodatne_usluge_objekti = Usluge.objects.filter(id__in=termin.dodatne_usluge)
        else:
            termin.dodatne_usluge_objekti = []

    return render(request, 'appointment/opcije/istorija.html', {'termini': termini})


@user_passes_test(lambda u: u.is_superuser)
def manage_appointment(request, termin_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            termin = Termin.objects.get(id=termin_id)
            
            if action == 'delete':
                # Delete appointment (customer didn't show up)
                termin.delete()
                return redirect('opcije_istorija')
            elif action == 'mark_completed':
                # Mark as completed - appointment was successfully done
                return redirect('opcije_istorija')
                
        except Termin.DoesNotExist:
            pass
    
    return redirect('opcije_istorija')


def obrisi_duznika(request, duznik_id):
    try:
        duznik = Duznik.objects.get(pk=duznik_id)
        if duznik.duguje:
            duznik.delete()
        else:
            kor = Korisnik.objects.get(pk=duznik.user.id)
            kor.dugovanje = 0
            kor.save()
            duznik.delete()
    except Duznik.DoesNotExist:
        try:
            kor = Korisnik.objects.get(pk=duznik_id)
            kor.dugovanje = 0
            kor.save()
        except Korisnik.DoesNotExist:
            print(f"No Duznik or Korisnik found with id {duznik_id}")
    except Exception as e:
        print(e)
    return redirect('opcije_izvestaj')