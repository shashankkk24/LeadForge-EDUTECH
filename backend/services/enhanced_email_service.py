"""
Enhanced async email service for SMTP dispatch.
Supports multiple providers (Gmail, Office365, custom SMTP).
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class EmailConfig:
    """Email configuration for different providers."""
    
    GMAIL = {
        "host": "smtp.gmail.com",
        "port": 465,
        "use_tls": False,
        "use_ssl": True,
        "timeout": 10,
    }
    
    OFFICE365 = {
        "host": "smtp.office365.com",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "timeout": 10,
    }
    
    CUSTOM = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "use_tls": getattr(settings, 'SMTP_USE_TLS', False),
        "use_ssl": getattr(settings, 'SMTP_USE_SSL', True),
        "timeout": 10,
    }


class EnhancedEmailService:
    """
    Service for sending emails via SMTP.
    
    Features:
    - Multiple provider support (Gmail, Office365, custom)
    - Async/sync operations
    - Attachment support
    - Template support
    - Batch sending with retry logic
    - Simulation mode for testing
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = True,
        use_tls: bool = False,
        timeout: int = 10,
    ):
        """
        Initialize email service.

        Args:
            host: SMTP host
            port: SMTP port
            user: Email username
            password: Email password / app password
            use_ssl: Use SSL connection
            use_tls: Use TLS connection
            timeout: Connection timeout in seconds
        """
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.user = user or settings.SMTP_USER
        self.password = password or settings.SMTP_PASSWORD
        self.use_ssl = use_ssl
        self.use_tls = use_tls
        self.timeout = timeout
        self.has_smtp = self._validate_config()

        if self.has_smtp:
            logger.info(f"✓ SMTP configured: {self.user}@{self.host}:{self.port}")
        else:
            logger.warning("⚠ SMTP not configured - using simulation mode")

    def _validate_config(self) -> bool:
        """Validate SMTP configuration."""
        return bool(self.host and self.port and self.user and self.password)

    async def send_email(
        self,
        to_addr: str,
        subject: str,
        body: str,
        html: bool = True,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Tuple[str, bytes]]] = None,
        retry_count: int = 3,
    ) -> Tuple[bool, str]:
        """
        Send email via SMTP or simulation mode.

        Args:
            to_addr: Recipient email address
            subject: Email subject line
            body: Email body (HTML or plain text)
            html: Whether body is HTML (default: True)
            cc: List of CC recipients
            bcc: List of BCC recipients
            attachments: List of (filename, file_bytes) tuples
            retry_count: Number of retry attempts

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.has_smtp:
            return self._simulate_send(to_addr, subject, body, cc, bcc)

        for attempt in range(retry_count):
            try:
                success, msg = self._send_real_email(
                    to_addr, subject, body, html, cc, bcc, attachments
                )
                if success:
                    return success, msg
                elif attempt < retry_count - 1:
                    logger.warning(f"Retry attempt {attempt + 1}/{retry_count}")
                    continue
                else:
                    return success, msg

            except Exception as e:
                logger.error(f"Email send error (attempt {attempt + 1}): {e}")
                if attempt == retry_count - 1:
                    return False, f"Failed after {retry_count} attempts: {str(e)}"

        return False, "Unknown error sending email"

    def _send_real_email(
        self,
        to_addr: str,
        subject: str,
        body: str,
        html: bool = True,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Tuple[str, bytes]]] = None,
    ) -> Tuple[bool, str]:
        """
        Send email via real SMTP server.

        Args:
            to_addr: Recipient email
            subject: Subject line
            body: Message body
            html: Whether to treat body as HTML
            cc: CC recipients
            bcc: BCC recipients
            attachments: File attachments

        Returns:
            Tuple of (success, message)
        """
        try:
            # Build recipient list
            all_recipients = [to_addr]
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)

            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.user
            msg["To"] = to_addr
            if cc:
                msg["Cc"] = ", ".join(cc)
            msg["Subject"] = subject

            # Attach body
            mime_type = "html" if html else "plain"
            msg.attach(MIMEText(body, mime_type))

            # Attach files if provided
            if attachments:
                for filename, file_bytes in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file_bytes)
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )
                    msg.attach(part)

            # Connect and send
            if self.use_ssl:
                server = smtplib.SMTP_SSL(
                    self.host, self.port, timeout=self.timeout
                )
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                if self.use_tls:
                    server.starttls()

            server.login(self.user, self.password)
            server.sendmail(self.user, all_recipients, msg.as_string())
            server.quit()

            logger.info(f"✓ Email sent to {to_addr} | Subject: {subject}")
            return True, f"Email sent to {to_addr}"

        except smtplib.SMTPAuthenticationError:
            logger.error("✗ SMTP authentication failed - invalid credentials")
            return False, "Authentication failed - check SMTP credentials"

        except smtplib.SMTPException as e:
            logger.error(f"✗ SMTP error: {e}")
            return False, f"SMTP error: {str(e)}"

        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return False, f"Error: {str(e)}"

    def _simulate_send(
        self,
        to_addr: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """
        Simulate sending email (testing/demo mode).

        Args:
            to_addr: Recipient email
            subject: Subject line
            body: Message body
            cc: CC recipients
            bcc: BCC recipients

        Returns:
            Tuple of (success=True, message)
        """
        log_msg = f"[SIMULATED EMAIL]\nTo: {to_addr}"
        if cc:
            log_msg += f"\nCc: {', '.join(cc)}"
        if bcc:
            log_msg += f"\nBcc: {', '.join(bcc)}"
        log_msg += f"\nSubject: {subject}\nBody length: {len(body)} chars"

        logger.info(log_msg)
        return True, f"[SIMULATED] Email queued for {to_addr}"

    async def send_batch_emails(
        self,
        recipients: List[Dict[str, Any]],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Send emails to multiple recipients with retry logic.

        Args:
            recipients: List of email dicts with:
                - to: recipient email
                - subject: email subject
                - body: email body
                - html: (optional) whether body is HTML
                - cc: (optional) list of CC addresses
                - bcc: (optional) list of BCC addresses
            max_retries: Max retry attempts per email

        Returns:
            Dict with:
                - sent: number of successful sends
                - failed: number of failed sends
                - errors: list of error details
                - total: total recipients
        """
        results = {
            "sent": 0,
            "failed": 0,
            "errors": [],
            "total": len(recipients),
        }

        for recipient in recipients:
            success, msg = await self.send_email(
                to_addr=recipient["to"],
                subject=recipient["subject"],
                body=recipient["body"],
                html=recipient.get("html", True),
                cc=recipient.get("cc"),
                bcc=recipient.get("bcc"),
                retry_count=max_retries,
            )

            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "recipient": recipient["to"],
                    "error": msg,
                })

        logger.info(
            f"Batch send complete: {results['sent']}/{results['total']} sent, "
            f"{results['failed']} failed"
        )
        return results

    @staticmethod
    def create_html_template(
        name: str,
        company: str,
        pain_point: str,
        solution: str,
        cta: str,
    ) -> str:
        """
        Create templated HTML email.

        Args:
            name: Recipient name
            company: Company name
            pain_point: Identified pain point
            solution: Solution positioning
            cta: Call-to-action text

        Returns:
            HTML email body
        """
        return f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .cta {{ background: #667eea; color: white; padding: 12px 20px; 
                           text-align: center; border-radius: 5px; text-decoration: none; 
                           display: inline-block; }}
                    .footer {{ text-align: center; font-size: 12px; color: #999; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Hey {name}! 👋</h1>
                    </div>
                    <div class="content">
                        <p>I noticed {company} is dealing with <strong>{pain_point}</strong>.</p>
                        <p>I work with schools like yours on <strong>{solution}</strong>.</p>
                        <p style="margin-top: 20px;">
                            <a href="#" class="cta">{cta}</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p>You received this email because we think you might find value in our solution.</p>
                    </div>
                </div>
            </body>
        </html>
        """


# Convenience function for legacy compatibility
async def send_email(
    to_addr: str,
    subject: str,
    body: str,
    html: bool = True,
) -> Tuple[bool, str]:
    """
    Convenience function to send a single email.

    Args:
        to_addr: Recipient email
        subject: Subject line
        body: Email body
        html: Whether body is HTML

    Returns:
        Tuple of (success, message)
    """
    service = EnhancedEmailService()
    return await service.send_email(to_addr, subject, body, html)
