from django.core.mail import EmailMessage
from django.conf import settings

def send_password_reset_email(employee_email, reset_link):
    """
    Dispatches password reset link over native SMTP infrastructure.
    """
    subject = "New Employee Registered, Reset Password Action Required"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #222; padding: 20px; line-height: 1.5;">
            <h2 style="color: #4B6BFB;">Reset Your Account Password</h2>
            <p>An administrator has initiated a password reset request for your Expense Tracker account.</p>
            <p>Please use the button below to securely configure your new access credentials:</p>
            
            <p style="margin: 25px 0;">
                <a href="{reset_link}" style="background-color: #4B6BFB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                    Reset Password
                </a>
            </p>
            
            <p style="font-size: 0.9em; color: #666;">
                If the button above does not work, copy and paste this link into your browser: <br>
                <a href="{reset_link}" style="color: #4B6BFB;">{reset_link}</a>
            </p>
            <p style="font-weight: bold; color: #dc2626;">This secure link will expire automatically.</p>
        </body>
    </html>
    """
    
    email = EmailMessage(
        subject=subject,
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[employee_email],
    )
    email.content_subtype = "html"  # Crucial: Tells Django to render HTML instead of plain text
    
    try:
        # Django returns 1 if email was sent successfully
        sent_count = email.send(fail_silently=False)
        return sent_count == 1
    except Exception as e:
        print(f"\n[CRITICAL] SMTP Core Delivery Execution Error: {e}\n")
        return False
