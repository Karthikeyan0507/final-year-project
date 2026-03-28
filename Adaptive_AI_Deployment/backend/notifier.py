import os
import smtplib
from email.message import EmailMessage
import threading

def dispatch_notification(contact_info, subject, message_body):
    """
    Dispatches a real notification. 
    If contact_info contains '@', it will send an email using Gmail SMTP.
    Otherwise, it logs that SMS integration requires a paid API (like Twilio).
    """
    if '@' in contact_info:
        # Assuming email
        _send_email_async(contact_info, subject, message_body)
    else:
        # Assuming phone number
        print(f"\n[NOTIFIER] Twilio SMS/WhatsApp integration is required to text phone numbers.")
        print(f"[NOTIFIER] Please enter a valid Email Address in the LYKA Dashboard to receive free real-time alerts!\n")

def _send_email_async(to_email, subject, body):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    
    if not sender_email or not sender_password:
        print("[NOTIFIER] Missing SENDER_EMAIL or SENDER_APP_PASSWORD in environment. Cannot send real email.")
        print(f"[NOTIFIER] Please configure these in your .env file to enable Email Emotion Delivery.")
        return False
        
    def send():
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = to_email
            
            # Gmail SMTP Config
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
            print(f"✅ [NOTIFIER] Successfully dispatched emergency email to {to_email}")
        except Exception as e:
            print(f"❌ [NOTIFIER ERROR] Failed to send email: {e}")
            
    # Send asynchronously to not block the chat pipeline
    threading.Thread(target=send).start()
    return True
