from garminconnect import Garmin
import os
import matplotlib.pyplot as plt
import numpy as np

# Initialize and login
client = Garmin(
    os.getenv("GARMIN_EMAIL", "lizkirstein@icloud.com"),
    os.getenv("GARMIN_PASSWORD", "Succulentsarecool49!")
)
client.login()

# Get today's stats
from datetime import date
_today = date.today().strftime('%Y-%m-%d')
stats = client.get_stats(_today)
# print("Stats for today", stats["bodyBatteryDynamicFeedbackEvent"])

# test = client.get_user_summary(_today)
# print(test)

test = client.get_stress_data(_today)

stress_values = np.array(test.get('stressValuesArray'))
times = (stress_values[:, 0] - stress_values[0, 0]) / (1000 * 60)
stress = stress_values[:, 1]
masked_stress = np.ma.masked_where(stress <= 0, stress)
plt.plot(times, masked_stress)
plt.show()


# Get heart rate data
# hr_data = client.get_heart_rates(_today)
# print(f"Resting HR: {hr_data.get('restingHeartRate', 'n/a')}")

# print(stats['bodyBatteryMostRecentValue'])


# feb15 = client.get_stats('2026-02-15')
# print('Stats for Feb 15th', feb15["bodyBatteryDynamicFeedbackEvent"])
# dec28 = client.get_stats('2025-12-28')
# print('Stats for Dec 28th', dec28["bodyBatteryDynamicFeedbackEvent"])