from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from appointment.models import Termin, Notification
from appointment.push_notifications import send_push_notification_to_user
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send email and push notification reminders for appointments starting in 2 hours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending notifications',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Calculate the time window: appointments starting in 2 hours
        now = timezone.now()
        target_time_start = now + timedelta(hours=1, minutes=45)  # 1h45m from now
        target_time_end = now + timedelta(hours=2, minutes=15)    # 2h15m from now
        
        self.stdout.write(f"Checking for appointments between {target_time_start} and {target_time_end}")
        
        # Get appointments in the next 2 hours (with 15-minute buffer on each side)
        upcoming_appointments = Termin.objects.filter(
            datum=target_time_start.date(),
            vreme__gte=target_time_start.time(),
            vreme__lte=target_time_end.time()
        ).select_related('user', 'frizer', 'usluga')
        
        if not upcoming_appointments.exists():
            self.stdout.write(self.style.SUCCESS('No appointments found in the next 2 hours'))
            return
        
        self.stdout.write(f"Found {upcoming_appointments.count()} upcoming appointments")
        
        sent_count = 0
        error_count = 0
        
        for appointment in upcoming_appointments:
            try:
                # Combine date and time for display
                appointment_datetime = datetime.combine(appointment.datum, appointment.vreme)
                
                # Prepare notification content
                title = "Podsetnik za termin"
                
                # Get all services for the appointment
                services_text = []
                if appointment.usluga:
                    services_text.append(appointment.usluga.name)
                
                if appointment.dodatne_usluge:
                    from appointment.models import Usluge
                    dodatne_usluge = Usluge.objects.filter(id__in=appointment.dodatne_usluge)
                    services_text.extend([usluga.name for usluga in dodatne_usluge])
                
                services_str = ", ".join(services_text) if services_text else "Usluga"
                
                # Email content
                email_subject = f"Podsetnik: Vaš termin za {services_str}"
                email_message = f"""Poštovani {appointment.user.ime_prezime or appointment.user.username},

Podsetnik da imate zakazan termin:

📅 Datum: {appointment.datum.strftime('%d.%m.%Y')}
⏰ Vreme: {appointment.vreme.strftime('%H:%M')}
💇‍♂️ Frizer: {appointment.frizer.name if appointment.frizer else 'Nije specificiran'}
✂️ Usluge: {services_str}
💰 Cena: {appointment.effective_price} RSD

Molimo Vas da stignete na vreme.

Hvala!
Frizerski salon Hasko
"""
                
                # Push notification content
                push_message = f"Vaš termin za {services_str} počinje u 2 sata ({appointment.vreme.strftime('%H:%M')})"
                
                if dry_run:
                    self.stdout.write(f"[DRY RUN] Would send to {appointment.user.email}:")
                    self.stdout.write(f"  Email: {email_subject}")
                    self.stdout.write(f"  Push: {push_message}")
                    sent_count += 1
                    continue
                
                # Send email notification
                email_sent = False
                if appointment.user.email and appointment.user.is_email_verified:
                    try:
                        send_mail(
                            subject=email_subject,
                            message=email_message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[appointment.user.email],
                            fail_silently=False,
                        )
                        email_sent = True
                        logger.info(f"Email reminder sent to {appointment.user.email} for appointment {appointment.id}")
                    except Exception as e:
                        logger.error(f"Failed to send email to {appointment.user.email}: {str(e)}")
                        self.stderr.write(f"Failed to send email to {appointment.user.email}: {str(e)}")
                
                # Create and send push notification
                push_sent = False
                try:
                    # Create notification record
                    notification = Notification.objects.create(
                        user=appointment.user,
                        title=title,
                        message=push_message
                    )
                    # The push notification will be sent automatically via the Notification.save() method
                    push_sent = True
                    logger.info(f"Push notification created for user {appointment.user.username} for appointment {appointment.id}")
                except Exception as e:
                    logger.error(f"Failed to send push notification to {appointment.user.username}: {str(e)}")
                    self.stderr.write(f"Failed to send push notification to {appointment.user.username}: {str(e)}")
                
                # Report results
                if email_sent or push_sent:
                    sent_count += 1
                    notifications_sent = []
                    if email_sent:
                        notifications_sent.append("email")
                    if push_sent:
                        notifications_sent.append("push")
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sent {' and '.join(notifications_sent)} reminder to {appointment.user.ime_prezime or appointment.user.username} "
                            f"for appointment at {appointment.vreme.strftime('%H:%M')}"
                        )
                    )
                else:
                    error_count += 1
                    self.stderr.write(f"Failed to send any notifications to {appointment.user.username}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing appointment {appointment.id}: {str(e)}", exc_info=True)
                self.stderr.write(f"Error processing appointment {appointment.id}: {str(e)}")
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"[DRY RUN] Would send reminders for {sent_count} appointments")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully sent reminders for {sent_count} appointments")
            )
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(f"Failed to process {error_count} appointments")
                )