import os
import json
import boto3
import requests
from datetime import datetime, timezone
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS & API credentials
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Validate environment variables
if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET, OPENWEATHER_API_KEY]):
    raise ValueError("Missing one or more environment variables in .env file!")

# List of cities to fetch
CITIES = ["London", "New York", "Hyderabad", "Tokyo"]

# Log file
LOG_FILE = "weather.log"

def log(message):
    """Append message with timestamp to log file and print it."""
    timestamp = datetime.now(timezone.utc).isoformat()
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, "a") as f:
        f.write(full_message + "\n")

def fetch_weather(city, retries=2):
    """Fetch weather data with retry logic."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=imperial"
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "city": city,
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["description"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except requests.RequestException as e:
            log(f"Error fetching {city} (attempt {attempt + 1}): {e}")
            time.sleep(5)  # Wait 5 seconds before retry
    log(f"Failed to fetch data for {city} after {retries+1} attempts.")
    return None

def upload_to_s3(data, bucket_name):
    """Upload data to S3 in a folder by current date."""
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    date_folder = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{date_folder}/weather_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=json.dumps(data, indent=4),
            ContentType="application/json"
        )
        log(f"Uploaded {filename} to bucket {bucket_name}")
    except Exception as e:
        log(f"Failed to upload {filename} to S3: {e}")

def collect_weather():
    """Collect weather data for all cities and upload to S3."""
    all_data = []
    for city in CITIES:
        weather = fetch_weather(city)
        if weather:
            all_data.append(weather)
    if all_data:
        upload_to_s3(all_data, S3_BUCKET)
    else:
        log("No weather data collected to upload.")

def main():
    """Main loop: run once or loop every hour."""
    while True:
        log("Starting weather data collection...")
        collect_weather()
        log("Weather data collection completed.")
        # Sleep for 1 hour (3600 seconds) for continuous run
        time.sleep(3600)

if __name__ == "__main__":
    main()

