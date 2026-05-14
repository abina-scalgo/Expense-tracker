# accounts/utils.py
import requests
from django.conf import settings

def send_password_reset_email(employee_email, reset_link):
    url = f"{settings.MAILGUN_BASE_URL}/{settings.MAILGUN_DOMAIN}/messages"
    auth = ("api", settings.MAILGUN_API_KEY)
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #222; padding: 20px; line-height: 1.5;">
            <h2 style="color: #4B6BFB;">Reset Your Portal Password</h2>
            <p>An administrator has initiated a password reset request for your Expense Tracker portal account.</p>
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
    
    payload = {
        "from": settings.MAILGUN_FROM_EMAIL,
        "to": [employee_email],
        "subject": "Portal Access Security: Action Required",
        "html": html_body
    }
    
    try:
        response = requests.post(url, auth=auth, data=payload, timeout=10)
        
        print("\n" + "="*50)
        print("----------- LIVE MAILGUN OUTBOUND TRACE -----------")
        print(f"Target Delivery Endpoint URL: {url}")
        print(f"Server Response HTTP Code: {response.status_code}")
        print(f"Server Response Body Text: {response.text}")
        print("="*50 + "\n")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"\n[CRITICAL] Mailgun Network Execution Error: {e}\n")
        return False
