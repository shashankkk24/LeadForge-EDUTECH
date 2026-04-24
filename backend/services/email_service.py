"""
Email service for SMTP dispatch and outreach logging.
Handles real Gmail SMTP sends with fallback to simulation mode.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Tuple

from config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.has_smtp = settings.has_smtp_config

        if self.has_smtp:
            logger.info(f"SMTP configured: {self.user}@{self.host}")
        else:
            logger.info("SMTP not configured - using simulation mode")

    async def send_email(
        self,
        to_addr: str,
        subject: str,
        body: str,
        html: bool = True,
    ) -> Tuple[bool, str]:
        """
        Send email via SMTP or simulation mode.

        Args:
            to_addr: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML (default: True)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.has_smtp:
            return self._simulate_send(to_addr, subject, body)

        try:
            return self._send_real_email(to_addr, subject, body, html)

        except Exception as e:
            logger.error(f"Failed to send email to {to_addr}: {e}")
            return False, f"Error: {str(e)}"

    def _send_real_email(self, to_addr: str, subject: str, body: str, html: bool = True) -> Tuple[bool, str]:
        """
        Send email via real Gmail SMTP.

        Args:
            to_addr: Recipient email
            subject: Subject line
            body: Message body
            html: Whether to treat body as HTML

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.user
            msg["To"] = to_addr
            msg["Subject"] = subject

            # Attach body
            mime_type = "html" if html else "plain"
            msg.attach(MIMEText(body, mime_type))

            # Send via SMTP
            with smtplib.SMTP_SSL(self.host, self.port, timeout=10) as server:
                server.login(self.user, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_addr}")
            return True, f"Email sent to {to_addr}"

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed - invalid credentials")
            return False, "Authentication failed - check SMTP credentials"

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False, f"SMTP error: {str(e)}"

        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False, f"Unexpected error: {str(e)}"

    def _simulate_send(self, to_addr: str, subject: str, body: str) -> Tuple[bool, str]:
        """
        Simulate sending email (for testing/demo without real SMTP).

        Args:
            to_addr: Recipient email (not actually sent)
            subject: Subject line
            body: Message body

        Returns:
            Tuple of (success=True, message)
        """
        logger.info(f"[SIMULATED] Email to {to_addr} | Subject: {subject} | Body length: {len(body)}")
        return True, f"[SIMULATED] Email queued for {to_addr}"

    async def send_batch_emails(self, recipients: list[dict]) -> dict:
        """
        Send emails to multiple recipients.

        Args:
            recipients: List of dicts with 'to', 'subject', 'body'

        Returns:
            Dict with sent/failed counts
        """
        results = {"sent": 0, "failed": 0, "errors": []}

        for recipient in recipients:
            success, msg = await self.send_email(
                recipient["to"],
                recipient["subject"],
                recipient["body"],
            )

            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"recipient": recipient["to"], "error": msg})

        logger.info(
            f"Batch send complete: {results['sent']} sent, {results['failed']} failed"
        )
        return results

    def format_html_email(self, title: str, content: str, cta_text: str, cta_link: str) -> str:
        """
        Format email as HTML.

        Args:
            title: Email title/header
            content: Email body content
            cta_text: Call-to-action button text
            cta_link: Call-to-action URL

        Returns:
            HTML string
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}
        .header {{
            background-color: #007bff;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .content {{
            padding: 20px;
        }}
        .cta {{
            display: inline-block;
            background-color: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="content">
            <p>{content}</p>
            <a href="{cta_link}" class="cta">{cta_text}</a>
        </div>
    </div>
</body>
</html>"""
