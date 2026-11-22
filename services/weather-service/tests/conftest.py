import os

# Settings are read when main.py is imported. Real values come from the environment or .env; these are test defaults.
for name, value in {
    "PROVIDER_BASE_URL": "http://provider.test/v1/forecast",
    "PROVIDER_TIMEOUT_SECONDS": "1",
    "PROVIDER_RETRIES": "2",
    "FORECAST_FRESH_SECONDS": "10800",
    "FORECAST_MAX_STALE_SECONDS": "86400",
    "RETRY_AFTER_SECONDS": "60",
}.items():
    os.environ[name] = value
