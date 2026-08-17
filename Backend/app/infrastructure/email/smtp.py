"""
SMTP email adapter — async plain-text delivery via fastapi-mail.

All send_* functions are no-ops when SMTP is not configured (MAIL_SERVER is empty).
"""

from email.message import EmailMessage
from email.utils import formataddr

import aiosmtplib

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def _send(to: str, subject: str, body: str) -> None:
    """Internal helper — sends a plain-text email. Silently skips if SMTP is unconfigured."""
    body = body.replace("https://your-domain.com", settings.APP_URL)
    if not settings.mail_enabled:
        logger.debug("Email skipped (SMTP not configured): subject='%s' to='%s'", subject, to)
        return

    try:
        message = EmailMessage()
        message["From"] = formataddr((settings.MAIL_FROM_NAME, settings.MAIL_FROM))
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            start_tls=settings.MAIL_STARTTLS,
            use_tls=settings.MAIL_SSL_TLS,
            timeout=settings.MAIL_TIMEOUT_SECONDS,
        )
        logger.info("Email sent: subject='%s' to='%s'", subject, to)
    except Exception as exc:
        logger.warning("Failed to send email to '%s': %s", to, exc)


async def send_welcome_email(to: str, full_name: str) -> None:
    """Sent after a new user successfully registers."""
    subject = f"Chào mừng {full_name} đến với AI Learning Assistant!"
    body = (
        f"Xin chào {full_name},\n\n"
        "Tài khoản của bạn đã được tạo thành công trên nền tảng AI Learning Assistant.\n\n"
        "Bạn có thể đăng nhập và bắt đầu lập lộ trình học tập ngay hôm nay.\n\n"
        "Chúc bạn học tập hiệu quả!\n"
        "— Đội ngũ AI Learning Assistant"
    )
    await _send(to, subject, body)


async def send_deadline_reminder_email(
    to: str,
    full_name: str,
    goal_title: str,
    days_left: int,
) -> None:
    """Sent when a study goal deadline is within 3 days."""
    subject = f"[Nhắc nhở] Lộ trình '{goal_title}' còn {days_left} ngày nữa là hết hạn"
    body = (
        f"Xin chào {full_name},\n\n"
        f"Lộ trình học tập '{goal_title}' của bạn còn {days_left} ngày nữa là đến hạn.\n\n"
        "Hãy kiểm tra tiến độ và hoàn thành các nhiệm vụ còn lại để đạt mục tiêu đã đề ra!\n\n"
        "Truy cập ngay: https://your-domain.com/study-plans\n\n"
        "— Đội ngũ AI Learning Assistant"
    )
    await _send(to, subject, body)



