from garminconnect import Garmin
import os
import numpy as np
from datetime import date
from dotenv import load_dotenv

dirname = os.path.dirname(__file__)
load_dotenv(dotenv_path=os.path.join(dirname, '.env'))

# Initialize and login
client = Garmin(
    os.getenv("GARMIN_EMAIL"),
    os.getenv("GARMIN_PASSWORD")
)
client.login()

_today = date.today().strftime('%Y-%m-%d')


def get_stats(day=_today):
    """Return client stats for a given day."""
    return client.get_stats(day)


def get_sleep_data(day=_today):
    """Return client sleep data for a given day"""
    return client.get_sleep_data(day)


def get_stress_values(day=_today):
    stress_data = client.get_stress_data(day)
    stress_values = np.array(stress_data.get('stressValuesArray'))
    return stress_values


# Get heart rate data
# hr_data = client.get_heart_rates(_today)
# print(f"Resting HR: {hr_data.get('restingHeartRate', 'n/a')}")

# print(stats['bodyBatteryMostRecentValue'])


# feb15 = client.get_stats('2026-02-15')
# print('Stats for Feb 15th', feb15["bodyBatteryDynamicFeedbackEvent"])
# dec28 = client.get_stats('2025-12-28')
# print('Stats for Dec 28th', dec28["bodyBatteryDynamicFeedbackEvent"])