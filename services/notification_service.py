import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from flask import current_app


class BaseNotificationProvider(ABC):
    """Abstract interface for all emergency notification providers."""

    @abstractmethod
    def send_notification(self, recipient: str, subject: str, message: str, metadata: dict = None) -> bool:
        """Send notification to a recipient."""
        pass


class ConsoleNotificationProvider(BaseNotificationProvider):
    """Fallback / Demonstration provider that logs notifications to the application log/console."""

    def send_notification(self, recipient: str, subject: str, message: str, metadata: dict = None) -> bool:
        print("\n" + "=" * 65)
        print(" [BLUE LINE - SIMULATED EMERGENCY DISPATCH] ")
        print(f" RECIPIENT: {recipient}")
        print(f" SUBJECT  : {subject}")
        print("-" * 65)
        print(message)
        print("=" * 65 + "\n")
        return True


class EmailNotificationProvider(BaseNotificationProvider):
    """SMTP Email provider for sending notifications."""

    def __init__(self, server: str, port: int, username: str, password: str, use_tls: bool = True, default_sender: str = None):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.default_sender = default_sender or 'alerts@blueline.local'

    def send_notification(self, recipient: str, subject: str, message: str, metadata: dict = None) -> bool:
        if not self.server or not self.username or not self.password:
            # Fall back to console in dev/demo mode
            print(f"[EmailNotificationProvider] SMTP credentials missing, routing to console for {recipient}")
            return ConsoleNotificationProvider().send_notification(recipient, subject, message, metadata)

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.default_sender
            msg['To'] = recipient

            part = MIMEText(message, 'plain')
            msg.attach(part)

            with smtplib.SMTP(self.server, self.port, timeout=10) as s:
                if self.use_tls:
                    s.starttls()
                s.login(self.username, self.password)
                s.send_message(msg)
            return True
        except Exception as e:
            print(f"[EmailNotificationProvider Error] Failed to send email to {recipient}: {e}")
            return False


# Stubs for future extensions (B.Tech major project requirement)
class SMSNotificationProvider(BaseNotificationProvider):
    """Future Extension: SMS Gateway integration (Twilio / Fast2SMS / MSG91)."""

    def send_notification(self, recipient: str, subject: str, message: str, metadata: dict = None) -> bool:
        print(f"[SMSNotificationProvider - STUB/FUTURE] Would send SMS to {recipient}: {message[:100]}...")
        return True


class WhatsAppNotificationProvider(BaseNotificationProvider):
    """Future Extension: WhatsApp Business Cloud API integration."""

    def send_notification(self, recipient: str, subject: str, message: str, metadata: dict = None) -> bool:
        print(f"[WhatsAppNotificationProvider - STUB/FUTURE] Would send WhatsApp to {recipient}")
        return True


class PushNotificationProvider(BaseNotificationProvider):
    """Future Extension: Firebase Cloud Messaging (FCM) Web Push."""

    def send_notification(self, recipient: str, subject: str, message: str, metadata: dict = None) -> bool:
        print(f"[PushNotificationProvider - STUB/FUTURE] Would send push alert to {recipient}")
        return True


class NotificationService:
    """Unified service for orchestrating emergency contact notifications."""

    @classmethod
    def get_provider(cls) -> BaseNotificationProvider:
        """Instantiate configured notification provider."""
        demo_mode = current_app.config.get('DEMO_MODE', True)
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_user = current_app.config.get('MAIL_USERNAME')
        mail_pass = current_app.config.get('MAIL_PASSWORD')

        if demo_mode or not (mail_server and mail_user and mail_pass):
            return ConsoleNotificationProvider()

        return EmailNotificationProvider(
            server=mail_server,
            port=current_app.config.get('MAIL_PORT', 587),
            username=mail_user,
            password=mail_pass,
            use_tls=current_app.config.get('MAIL_USE_TLS', True),
            default_sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )

    @classmethod
    def build_alert_message(cls, alert, user, nearest_police=None) -> str:
        """Compose standardized emergency message format."""
        time_str = alert.created_at.strftime('%Y-%m-%d %I:%M:%S %p UTC') if alert.created_at else "Just now"
        map_link = alert.google_maps_url or "Coordinates not yet available"

        police_info = "None stored in database"
        if nearest_police:
            police_info = f"{nearest_police.station_name} ({nearest_police.city}, {nearest_police.state})"

        message = (
            "====================================================\n"
            "🚨 BLUE LINE EMERGENCY ALERT 🚨\n"
            "====================================================\n"
            f"User Name      : {user.full_name}\n"
            f"User Phone     : {user.phone}\n"
            f"User Blood Grp : {user.blood_group or 'Not specified'}\n"
            f"Emergency Type : {alert.emergency_type}\n"
            f"Trigger Method : {alert.trigger_type}\n"
            f"Incident Time  : {time_str}\n"
            f"Current Status : {alert.status}\n"
            f"User Remarks   : {alert.description or 'No extra details provided'}\n"
            "----------------------------------------------------\n"
            f"Latitude       : {alert.latitude if alert.latitude is not None else 'Pending'}\n"
            f"Longitude      : {alert.longitude if alert.longitude is not None else 'Pending'}\n"
            f"GPS Accuracy   : {alert.accuracy if alert.accuracy is not None else 'Pending'} meters\n"
            f"Live Map Link  : {map_link}\n"
            "----------------------------------------------------\n"
            f"Nearest Station: {police_info}\n"
            "National Help  : 112 (National Emergency Helpline)\n"
            "----------------------------------------------------\n"
            "ACTION REQUIRED: Please immediately reach out to the user and verify their safety.\n"
            "[Note: In Demo Mode, emergency services dispatch is simulated.]\n"
            "===================================================="
        )
        return message

    @classmethod
    def notify_emergency_contacts(cls, alert, user, contacts: List[Any], nearest_police=None) -> List[Dict[str, Any]]:
        """Dispatch notifications to all active emergency contacts."""
        results = []
        provider = cls.get_provider()
        subject = f"🚨 EMERGENCY ALERT: {user.full_name} needs help ({alert.emergency_type})"
        message = cls.build_alert_message(alert, user, nearest_police)

        for contact in contacts:
            if not contact.is_active:
                continue

            destination = contact.email if contact.email else f"Phone: {contact.phone}"
            success = provider.send_notification(
                recipient=destination,
                subject=subject,
                message=message,
                metadata={'alert_id': alert.id, 'contact_name': contact.name}
            )

            results.append({
                'contact_id': contact.id,
                'name': contact.name,
                'relationship': contact.relationship,
                'recipient': destination,
                'status': 'SENT' if success else 'FAILED',
                'provider': provider.__class__.__name__
            })

        return results
