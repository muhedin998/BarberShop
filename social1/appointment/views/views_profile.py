from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import ProfileUpdateForm
from django.contrib import messages


@login_required
def profile_page(request):
    user = request.user
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil je uspešno ažuriran!')
            return redirect('profile_page')
        else:
            messages.error(request, 'Greška pri ažuriranju profila. Molimo pokušajte ponovo.', extra_tags='danger')
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user
    }
    return render(request, 'appointment/profil-page.html', context)


def notifications_page(request):
    return render(request, 'appointment/notifications_page.html')