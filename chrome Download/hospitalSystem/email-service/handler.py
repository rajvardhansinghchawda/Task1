import json
import smtplib
from email.message import EmailMessage
import os

def send_email(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        email_type = body.get('type')
        recipient = body.get('email')
        data = body.get('data', {})

        # SMTP Settings (must be provided via environment variables)
        SMTP_SERVER = os.environ.get('SMTP_SERVER', os.environ.get('EMAIL_HOST', ''))
        SMTP_PORT = int(os.environ.get('SMTP_PORT', os.environ.get('EMAIL_PORT', '587')))
        SMTP_USER = os.environ.get('SMTP_USER', os.environ.get('EMAIL_HOST_USER', ''))
        SMTP_PASS = os.environ.get('SMTP_PASS', os.environ.get('EMAIL_HOST_PASSWORD', ''))

        print(f"DEBUG: SMTP_SERVER={SMTP_SERVER}, SMTP_PORT={SMTP_PORT}, SMTP_USER={SMTP_USER}")
        print(f"DEBUG: Recipient={recipient}, Type={email_type}")

        if not SMTP_SERVER or not SMTP_USER or not SMTP_PASS:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "SMTP is not configured",
                    "missing": [
                        k for k, v in {
                            "SMTP_SERVER/EMAIL_HOST": SMTP_SERVER,
                            "SMTP_USER/EMAIL_HOST_USER": SMTP_USER,
                            "SMTP_PASS/EMAIL_HOST_PASSWORD": SMTP_PASS,
                        }.items() if not v
                    ]
                })
            }

        msg = EmailMessage()
        msg['From'] = SMTP_USER
        msg['To'] = recipient

        if email_type == 'BOOKING_CONFIRMATION':
            msg['Subject'] = 'Appointment Confirmed'
            content = f"""Hello {data.get('patient')},

Your appointment with {data.get('doctor')} is confirmed.

Date: {data.get('date')}
Time: {data.get('time')}

Thank you,
Mini Hospital Management System"""
            msg.set_content(content)

        elif email_type == 'SIGNUP_WELCOME':
            msg['Subject'] = 'Welcome to Hospital HMS'
            msg.set_content(f"Hello {data.get('name', 'User')},\n\nWelcome to our platform. We're glad to have you!")

        elif email_type == 'BOOKING_NOTIFICATION_DOCTOR':
            msg['Subject'] = 'New Appointment Booked'
            content = f"""Hello {data.get('doctor')},

A new appointment has been booked by {data.get('patient')}.

Date: {data.get('date')}
Time: {data.get('time')}

Thank you,
Mini Hospital Management System"""
            msg.set_content(content)

        elif email_type == 'OTP_VERIFICATION':
            msg['Subject'] = 'Your Hospital HMS Verification Code'
            content = f"""Your OTP verification code is: {data.get('otp')}

This code expires in 5 minutes.

If you did not request this code, please ignore this email.

Thank you,
Mini Hospital Management System"""
            msg.set_content(content)
        
        else:
            return {"statusCode": 400, "body": json.dumps({"message": "Invalid email type"})}

        # Send email using SMTP
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            print(f"Email successfully sent to {recipient}")
        except Exception as smtp_err:
            print(f"SMTP Error for {recipient}: {smtp_err}")
            # Still returning 200 for demo purposes if requested, but better to return 500
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Failed to send email via SMTP",
                    "error": str(smtp_err)
                })
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Email sent successfully",
                "recipient": recipient
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to send email",
                "error": str(e)
            })
        }
