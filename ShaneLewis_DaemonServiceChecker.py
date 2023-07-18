import psutil
import smtplib
import subprocess
import time
import traceback
import logging
import ssl

# Configuration
service_name = "<service name of your choice"  # Name of the service to monitor
recipient_email = "<email of where you want it to go"  # Email address to receive alerts
smtp_server = "smtp.example.com"  # SMTP server details
smtp_port = 465  # SMTP server port
smtp_username = "<smtp username"
smtp_password = "<smtp password"
ssl_context = ssl.create_default_context()

# Logging configuration
log_file = "daemon.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_service_status():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == service_name:
            return True  # Service is running
    return False  # Service is not running

def send_email(subject, body):
    message = "Subject: {}\n\n{}".format(subject, body)
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=ssl_context) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, recipient_email, message)
        logging.info("Email notification sent.")
    except smtplib.SMTPException as e:
        logging.error("Failed to send email: %s", e)
        traceback.print_exc()

def restart_service():
    try:
        subprocess.run(["systemctl", "restart", service_name], check=True)
        logging.info("Service restarted successfully.")
    except subprocess.CalledProcessError as e:
        send_email("Service Restart Failed", "Failed to restart the {} service.".format(service_name))
        logging.error("Failed to restart service: %s", e)
        traceback.print_exc()

def main():
    while True:
        if not check_service_status():
            subject = "Notification for Service Down: {}".format(service_name)
            body = "The {} service has stopped. Attempting to restart...".format(service_name)
            send_email(subject, body)
            restart_service()
        time.sleep(45)  # Delay between checks

if __name__ == "__main__":
    main()