# Authentication views
from .views_auth import (
    update_ime_prezime, complete_profile, send_action_email,
    user_register, user_login, user_logout, activate_user
)

# Appointment views
from .views_appointments import (
<<<<<<< HEAD
    potvrdi, termin, zakazi, otkazivanje, zafrizera
=======
    potvrdi, termin, zakazi, otkazivanje, zafrizera, help_page
>>>>>>> origin/izmene
)

# Admin/Management views
from .views_admin import (
    opcije_termini, opcije_klijenti, opcije_izvestaj,
    opcije_istorija, obrisi_duznika, manage_appointment
)

# Profile views
from .views_profile import (
    profile_page, notifications_page, mark_notification_read,
    mark_notification_unread, delete_notification, mark_all_read
)