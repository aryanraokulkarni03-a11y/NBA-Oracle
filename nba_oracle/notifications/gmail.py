from __future__ import annotations

import smtplib
from email.message import EmailMessage

from nba_oracle.config import GMAIL_APP_PASSWORD, GMAIL_RECIPIENT, GMAIL_SENDER
from nba_oracle.runtime.state import record_notification_event


def send_gmail_message(
    subject: str,
    body: str,
    *,
    recipient: str | None = None,
    event_type: str = "generic_email",
) -> str:
    sender = GMAIL_SENDER
    password = GMAIL_APP_PASSWORD
    destination = recipient or GMAIL_RECIPIENT
    if not sender or not password or not destination:
        raise RuntimeError("gmail_not_configured")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = destination
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as client:
            client.login(sender, password)
            client.send_message(message)
        return record_notification_event(
            "gmail",
            event_type,
            True,
            destination,
            {"subject": subject},
        )
    except Exception as exc:  # pragma: no cover - network dependent
        record_notification_event(
            "gmail",
            event_type,
            False,
            destination,
            {"subject": subject, "error": str(exc)},
        )
        raise RuntimeError(f"gmail_send_failed:{exc}") from exc
