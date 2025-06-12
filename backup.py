# backup.py

import os
import tarfile
import boto3
import smtplib
import traceback
from datetime import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText

# Load environment variables
load_dotenv("config.env")

# === CONFIG ===
BACKUP_DIRS = os.getenv("BACKUP_DIRS", "").split(",")
BACKUP_TEMP_DIR = os.getenv("BACKUP_TEMP_DIR")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

LOG_FILE = os.getenv("LOG_FILE")
print("Loaded LOG_FILE:", LOG_FILE)  # Moved print statement after LOG_FILE is defined

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def send_email(subject: str, body: str):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, [EMAIL_RECIPIENT], msg.as_string())
        return True
    except Exception as e:
        log(f"Email sending failed: {str(e)}")
        return False


def compress_dirs(dirs, output_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    archive_name = f"backup-{timestamp}.tar.gz"
    archive_path = os.path.join(output_dir, archive_name)

    with tarfile.open(archive_path, "w:gz") as tar:
        for d in dirs:
            tar.add(d, arcname=os.path.basename(d))
    
    return archive_path


def upload_to_s3(file_path, bucket_name):
    s3 = boto3.client("s3")
    s3_key = f"backups/{os.path.basename(file_path)}"
    s3.upload_file(file_path, bucket_name, s3_key)
    return s3_key


def main():
    try:
        log("Backup started.")
        archive_path = compress_dirs(BACKUP_DIRS, BACKUP_TEMP_DIR)
        log(f"Compressed to {archive_path}")

        s3_key = upload_to_s3(archive_path, S3_BUCKET_NAME)
        log(f"Uploaded to S3 at {s3_key}")

        os.remove(archive_path)
        log("Temporary archive removed.")

        send_email("Backup Success", f"Backup uploaded to S3: {s3_key}")
        log("Success email sent.")

    except Exception as e:
        error_msg = f"Backup failed: {str(e)}\n{traceback.format_exc()}"
        log(error_msg)
        try:
            send_email("Backup Failed", error_msg)
        except Exception as email_err:
            log(f"Could not send error email: {str(email_err)}")


if __name__ == "__main__":
    main()
