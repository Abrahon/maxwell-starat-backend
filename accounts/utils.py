# import logging
# import smtplib
# import random
# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives, BadHeaderError
# from django.utils.html import strip_tags

# logger = logging.getLogger(__name__)


# # 🔹 Generate a 6-digit OTP
# def generate_otp():
#     return str(random.randint(100000, 999999))


# # 🔹 Send OTP via email
# def send_otp_email(to_email, otp_code, name="User"):
#     subject = "Your OTP Code"
#     html_content = f"""
#         <p>Hello {name},</p>
#         <p>Your OTP code is:</p>
#         <h2>{otp_code}</h2>
#         <p>This code will expire in 5 minutes.</p>
#     """
#     plain_text = strip_tags(html_content)
#     from_email = settings.EMAIL_HOST_USER

#     try:
#         msg = EmailMultiAlternatives(
#             subject=subject,
#             body=plain_text,
#             from_email=from_email,
#             to=[to_email],
#         )
#         msg.attach_alternative(html_content, "text/html")
#         msg.send(fail_silently=False)
#         logger.info("OTP sent to %s", to_email)
#         return True
#     except (smtplib.SMTPException, BadHeaderError, ConnectionRefusedError) as exc:
#         logger.exception("Failed sending OTP to %s: %s", to_email, exc)
#         return False


# # 🔹 Send email verification link
# def send_email_verification(to_email, verification_link, name="User"):
#     subject = "Verify your email address"
#     html_content = f"""
#     <div style="font-family:Arial,sans-serif;max-width:600px;margin:20px auto;
#                 border:1px solid #e2e2e2;padding:20px;border-radius:10px;background-color:#f9f9f9;">
#         <h2>Hello {name}</h2>
#         <p>Please verify your email by clicking the button below:</p>
#         <div style="text-align:center;margin:25px 0;">
#             <a href="{verification_link}"
#                style="background:#28a745;color:#fff;padding:12px 20px;
#                       text-decoration:none;border-radius:6px;font-weight:bold;">
#                 Verify Email
#             </a>
#         </div>
#         <p>If you did not create an account, ignore this email.</p>
#     </div>
#     """
#     plain_text = strip_tags(html_content)
#     from_email = settings.EMAIL_HOST_USER

#     try:
#         msg = EmailMultiAlternatives(
#             subject=subject,
#             body=plain_text,
#             from_email=from_email,
#             to=[to_email],
#         )
#         msg.attach_alternative(html_content, "text/html")
#         msg.send(fail_silently=False)
#         logger.info("Verification email sent to %s", to_email)
#         return True
#     except Exception as exc:
#         logger.exception("Failed sending verification email to %s: %s", to_email, exc)
#         return False
import logging
import smtplib
import random
import time
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# 🔹 Retry helper
def send_email_with_retry(msg, retries=3, delay=5):
    """
    Attempts to send an EmailMultiAlternatives message multiple times.
    """
    for i in range(retries):
        try:
            msg.send(fail_silently=False)
            logger.info("Email sent successfully to %s on attempt %d", msg.to, i+1)
            return True
        except Exception as exc:
            logger.warning("Attempt %d failed sending email to %s: %s", i+1, msg.to, exc)
            time.sleep(delay)
    logger.error("Failed to send email to %s after %d attempts", msg.to, retries)
    return False

# 🔹 Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# 🔹 Send OTP via email
def send_otp_email(to_email, otp_code, name="User"):
    subject = "Your OTP Code"
    html_content = f"""
        <p>Hello {name},</p>
        <p>Your OTP code is:</p>
        <h2>{otp_code}</h2>
        <p>This code will expire in 5 minutes.</p>
    """
    plain_text = strip_tags(html_content)
    from_email = settings.EMAIL_HOST_USER

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,
        from_email=from_email,
        to=[to_email],
    )
    msg.attach_alternative(html_content, "text/html")

    return send_email_with_retry(msg)

# 🔹 Send email verification link
def send_email_verification(to_email, verification_link, name="User"):
    subject = "Verify your email address"
    html_content = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:20px auto;
                border:1px solid #e2e2e2;padding:20px;border-radius:10px;background-color:#f9f9f9;">
        <h2>Hello {name}</h2>
        <p>Please verify your email by clicking the button below:</p>
        <div style="text-align:center;margin:25px 0;">
            <a href="{verification_link}"
               style="background:#28a745;color:#fff;padding:12px 20px;
                      text-decoration:none;border-radius:6px;font-weight:bold;">
                Verify Email
            </a>
        </div>
        <p>If you did not create an account, ignore this email.</p>
    </div>
    """
    plain_text = strip_tags(html_content)
    print("plain_text",plain_text)
    from_email = settings.EMAIL_HOST_USER
    print("from_email",from_email)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,
        from_email=from_email,
        to=[to_email],
    )
    msg.attach_alternative(html_content, "text/html")
    print("msg",msg)

    return send_email_with_retry(msg)
