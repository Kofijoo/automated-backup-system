# Automated System Backup & Restore

A zero-cost, fully automated Linux/Windows-compatible backup system using **Python**, **Bash**, **AWS S3**, and **Task Scheduler (Windows)** or **cron (Linux)**. This project was built to demonstrate real-world DevOps and scripting skills with cloud integration, reliability, and security in mind.

---

## Features

- Scheduled backups of specified system folders
- Compression and archiving with timestamped `.tar.gz`
- Secure upload to AWS S3 (free tier compatible)
- Local logging of backup operations
- Email alerts for success/failure
- Manual restore script for recovery
- OS-level automation via Task Scheduler or cron

---

## Technologies Used

- Python 3.10+
- Bash scripting
- AWS S3 & IAM
- `boto3`, `python-dotenv`, `smtplib`
- Git Bash / Task Scheduler (Windows) or cron (Linux)

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/Kofijoo/automated-backup-system.git
cd automated-backup-system

###  Install Dependencies
pip install -r requirements.txt

### 3. Configure Environment
### Create and fill config.env:
BACKUP_DIRS=test
BACKUP_TEMP_DIR=C:/Users/YourUser/Desktop/Automated System Backup & Restore/tmp
S3_BUCKET_NAME=your-s3-bucket

AWS_ACCESS_KEY_ID=XXXX
AWS_SECRET_ACCESS_KEY=YYYY
AWS_REGION=us-east-1

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=notify@yourdomain.com

LOG_FILE=logs/backup.log

### 4. Manual Run
./backup.sh

bash -c "cd '/your/project/path' && ./backup.sh"

0 2 * * * /path/to/backup.sh >> /path/to/logs/backup.log 2>&1


/automated-backup-system/
├── backup.py
├── backup.sh
├── restore.py
├── restore.sh
├── config.env
├── logs/
├── tmp/
└── README.md

