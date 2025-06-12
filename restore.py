# restore.py

import os
import sys
import boto3
import tarfile
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

# === CONFIG ===
BACKUP_TEMP_DIR = os.getenv("BACKUP_TEMP_DIR")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
LOG_FILE = os.getenv("LOG_FILE")


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def list_backups():
    """List all available backups in S3 bucket"""
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="backups/")
    
    if "Contents" not in response:
        print("No backups found.")
        return []
    
    backups = []
    for item in response["Contents"]:
        key = item["Key"]
        if key.endswith(".tar.gz"):
            size_mb = item["Size"] / (1024 * 1024)
            last_modified = item["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
            backups.append({
                "key": key,
                "filename": os.path.basename(key),
                "size_mb": round(size_mb, 2),
                "last_modified": last_modified
            })
    
    return backups


def download_backup(backup_key, output_dir):
    """Download a specific backup from S3"""
    s3 = boto3.client("s3")
    local_path = os.path.join(output_dir, os.path.basename(backup_key))
    
    print(f"Downloading {backup_key} to {local_path}...")
    s3.download_file(S3_BUCKET_NAME, backup_key, local_path)
    
    return local_path


def extract_backup(archive_path, extract_to):
    """Extract the backup archive to the specified directory"""
    print(f"Extracting {archive_path} to {extract_to}...")
    
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=extract_to)


def main():
    parser = argparse.ArgumentParser(description="Restore backups from S3")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--restore", help="Restore a specific backup by filename")
    parser.add_argument("--latest", action="store_true", help="Restore the latest backup")
    parser.add_argument("--output-dir", default="./restored", help="Directory to extract files to")
    
    args = parser.parse_args()
    
    if args.list:
        backups = list_backups()
        if backups:
            print("\nAvailable backups:")
            for i, backup in enumerate(backups):
                print(f"{i+1}. {backup['filename']} ({backup['size_mb']} MB) - {backup['last_modified']}")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    backups = list_backups()
    if not backups:
        print("No backups available to restore.")
        return
    
    backup_to_restore = None
    
    if args.latest:
        # Sort by last_modified and get the latest
        backups.sort(key=lambda x: x["last_modified"], reverse=True)
        backup_to_restore = backups[0]
        print(f"Restoring latest backup: {backup_to_restore['filename']}")
    
    elif args.restore:
        # Find the backup with the specified filename
        for backup in backups:
            if backup["filename"] == args.restore or backup["key"] == args.restore:
                backup_to_restore = backup
                break
        
        if not backup_to_restore:
            print(f"Backup '{args.restore}' not found.")
            return
    
    else:
        parser.print_help()
        return
    
    try:
        log(f"Starting restore of {backup_to_restore['key']}")
        
        # Download the backup
        local_path = download_backup(backup_to_restore["key"], BACKUP_TEMP_DIR)
        log(f"Downloaded backup to {local_path}")
        
        # Extract the backup
        extract_backup(local_path, args.output_dir)
        log(f"Extracted backup to {args.output_dir}")
        
        # Clean up
        os.remove(local_path)
        log("Temporary archive removed")
        
        print(f"Restore completed successfully to {args.output_dir}")
        log("Restore completed successfully")
        
    except Exception as e:
        error_msg = f"Restore failed: {str(e)}"
        print(error_msg)
        log(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()