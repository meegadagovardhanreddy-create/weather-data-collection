                          ┌──────────────────────────┐
                          │      User / Developer     │
                          └──────────────┬───────────┘
                                         │
                                         │ Executes Project
                                         ▼
                 ┌───────────────────────────────────────────┐
                 │        Application Layer (Python)          │
                 │────────────────────────────────────────────│
                 │  • app.py                                  │
                 │  • Loads .env credentials                   │
                 │  • Triggers weather data collection         │
                 └───────────────┬────────────────────────────┘
                                 │
                                 │ Uses API Key (OpenWeather)
                                 ▼
                    ┌────────────────────────────────┐
                    │        OpenWeather API          │
                    │     (External Data Source)       │
                    └──────────────────┬───────────────┘
                                       │
                                       │ Returns JSON Weather Data
                                       ▼
                   ┌────────────────────────────────────────┐
                   │       Data Processing Layer             │
                   │─────────────────────────────────────────│
                   │ • Extract temperature, humidity, status │
                   │ • Add UTC timestamp                     │
                   │ • Convert into structured JSON          │
                   └───────────────────┬─────────────────────┘
                                       │
                                       │ Upload using boto3
                                       ▼
                     ┌──────────────────────────────────────┐
                     │             AWS S3 Bucket             │
                     │      (weather-data-collection-gmr)    │
                     │──────────────────────────────────────│
                     │ • Stores JSON weather snapshots       │
                     │ • Maintains historical data           │
                     └──────────────────────────────────────┘
