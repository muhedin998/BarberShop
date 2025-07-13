from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import KorisnikForm
from django.contrib import messages
from ..models import Korisnik, Duznik, Notification
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from ..utils import generate_token
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver


def check_and_notify_existing_debt(user):
    """
    Check if there are existing debt records for this user and create notifications.
    This function looks for debt records that match the user's phone number or name.
    """
    try:
        # Look for existing debt records by phone number
        existing_debts = Duznik.objects.filter(broj_telefona=user.broj_telefona)
        
        if existing_debts.exists():
            total_debt = 0
            debt_records_count = existing_debts.count()
            
            # Calculate total debt and optionally link records to user
            for debt in existing_debts:
                total_debt += debt.duguje or 0
                # Link the debt record to the newly registered user
                debt.user = user
                debt.save()
            
            # Add debt to user's profile if they have existing debt
            if total_debt > 0:
                if user.dugovanje:
                    user.dugovanje += total_debt
                else:
                    user.dugovanje = total_debt
                user.save()
                
                # Create notification about existing debt
                Notification.objects.create(
                    user=user,
                    title="Postojeće dugovanje pronađeno",
                    message=f"Dobrodošli! Pronašli smo vaše postojeće dugovanje u iznosu od {total_debt} RSD. "
                            f"Molimo vas da se obratite salonu za regulisanje dugovanja."
                )
    
    except Exception as e:
        # Log the error but don't break the registration process
        print(f"Error checking existing debt for user {user.username}: {e}")


@receiver(user_logged_in)
def update_ime_prezime(request, user, **kwargs):
    social_info = SocialAccount.objects.filter(user=user).first()
    if social_info:
        extra_data = social_info.extra_data
        # Check if it's Google's data structure
        if 'given_name' in extra_data and 'family_name' in extra_data:
            first_name = extra_data.get('given_name')
            last_name = extra_data.get('family_name')
            full_name = f"{first_name} {last_name}"
        # Check if it's Facebook's data structure
        elif 'name' in extra_data:
            full_name = extra_data.get('name')
        else:
            full_name = None

        if full_name:
            user.ime_prezime = full_name
            user.save()


@login_required
def complete_profile(request):
    if request.method == 'POST':
        broj_telefona = request.POST.get('broj_telefona')
        if broj_telefona:
            request.user.broj_telefona = broj_telefona
            request.user.save()
            
            # Check for existing debt when completing profile (social auth users)
            check_and_notify_existing_debt(request.user)
            
            return redirect('/')
    return render(request, 'complete_profile.html')


def send_action_email(request, user):
    current_site = get_current_site(request)
    email_sibject = 'Aktivirajte vaš nalog'
    email_body = render_to_string('appointment/account/activate.html',{
        'user': user,
        'domain': current_site,
        'protocol': 'https' if request.is_secure() else 'http',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : generate_token().make_token(user)
    })
    email = EmailMessage(subject=email_sibject, body=email_body,from_email=settings.EMAIL_HOST_USER, to=[user.email])
    email.content_subtype = 'html'  # Enable HTML content
    email.send()


def user_register(request):
    form = KorisnikForm()

    if request.method =='POST':
        data ={
            'ime_prezime':request.POST['ime_prezime'],
            'username':request.POST['username'],
            'email':request.POST['email'],
            'password':request.POST['password'],
            'password2':request.POST['password2'],
            'broj_telefona':request.POST['broj_telefona'],
        }
        form = KorisnikForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(request.POST['password'])
            user.save()
            form.save()

            # Check for existing debt records and create notifications
            check_and_notify_existing_debt(user)

            send_action_email(request, user)
            
            messages.success(request, "Proverite vaše email sanduče za aktivaciju naloga, ukoliko ne vidite email pogledajte u folderu nepoželjno(spam)")
            return redirect('user_login')
        else:
            messages.error(request, "Nepravilno popunjena polja, pokusajte ponovo",extra_tags='danger')
    return render(request, 'appointment/account/register.html',{'form':form})


def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_email_verified:
            return redirect('zakazi')
    if request.method =="POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if not user.is_email_verified:
                send_action_email(request, user)
                messages.error(request, "Email nije aktiviran, proverite poštansko sanduče", extra_tags="danger")
                return redirect('user_login')
            else:
                login(request, user)
            return redirect('zakazi')
        else:
            messages.error(request, "Nepravilno korisnicko ime ili lozinka !", extra_tags="danger")
            return redirect('user_login')

    return render(request, 'appointment/account/login.html')


def user_logout(request):
    logout(request)
    return redirect('user_login')


def activate_user(request, uidb64, token):
    
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user = Korisnik.objects.get(pk=uid) 
    except Exception as e:
        user=None
    
    if user and generate_token().check_token(user, token):
        user.is_email_verified = True
        user.save()

        messages.add_message(request, messages.SUCCESS, "Email je verifikovan, sada se možete prijaviti")
        return redirect('user_login')
    if request.user.is_authenticated:
        if not request.user.is_email_verified:
            messages.error(request,"Link za prijavu je istekao, prijavite se za novi link", extra_tags="danger")
            return redirect('user_login')
        else:
            return redirect('user_login')
    else:
        messages.error(request,"Morate se prvo prijaviti", extra_tags="danger")
        return redirect('user_login')