import os

# Settings are read when main.py is imported. Real values come from the environment or .env; these are test defaults.
for name, value in {
    "REGISTRY_URL": "http://registry.test",
    "WEATHER_URL": "http://weather.test",
    "REGISTRY_TIMEOUT_SECONDS": "1",
    "WEATHER_TIMEOUT_SECONDS": "1",
}.items():
    os.environ[name] = value
