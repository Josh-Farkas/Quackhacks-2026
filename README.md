# Quackhacks 2026
Stevens Hackathon project

## User Guide
Our program requires your account information from Steam and Garmin; here's what you'll need to do before you start.
First, get your own Steam API Key: https://steamcommunity.com/dev/apikey
Next, get your Steam account ID. This can be found on the desktop application by navigating to your Account Details, or by inputting your account URL into this website: https://steamid.io/
This is all you need from Steam. For Garmin, you will need to input your email and password (All saved locally, nothing will be online). Once you have these items, you can continue to starting the program.
In the console, you will be prompted to either (1) Set your Steam ID, Steam API key, and Garmin login, (2) Generate report, (3) Run Steam monitoring, or (q) quit.
First, type 1, and enter your information. Next, type 3 to start running your steam monitoring, then leave the program running in the background. To get a report on one day's worth of data, make sure you have the steam monitoring running for at least 24 hours. You can quit and then return to the program after that time has elapsed and simply type 2 to generate your report.

## Inspiration
All three of us are avid gamers that also care about our mental health. Sometimes gaming can cause more harm to your mental health than one might realize. We wanted to build something to help gamers see how their sessions directly impact their mental and physical health. One might enjoy playing horror games but after looking into stress levels and sleep score realize it's not good to play them right before bed as it increases stress and causes poor sleep.

## What it does
Our project connects gameplay data with biometric health signals to generate personalized reports.

Each day, users can:
- View stress levels over time
- See body battery trends
- Visualize gaming sessions directly overlaid on stress graphs

Rather than discouraging gaming our tool provides actionable insight so users can make informed decisions about when and what to play.

## How we built it
We utilized two APIs for this project, garminConnectAPI and the steam API. Using garminConnect we are able to access all past data from the user with timestamps. The data we are using is stress levels, body battery, and sleep scores. The steamAPI is a little different, we cannot access any previous data. The use of this API is to get which game is currently being played. The program will run as a background process and check every three minutes if a game is open in steam. It will then log the timestamp and the name of the game open or "none" if no game is open. We then align the steam session with Garmin stress timestamps and plot the trends using matplotlib. We used python report library to generate pdf files of the plots.

## Challenges we ran into
One of the biggest challenges was using the steam API. Finding the right python library to use was difficult since some didn't have all the data we needed. It is also a challenge because steam doesn't store vital data from past gaming sessions, meaning we have to actively monitor the player to determine when they were playing what game. Also since steam doesn't store past data we had to make up our own bluff data to test with. Another challenge we faced was accessing sleep score data from Garmin. The sleep score data is stored in the next days data since it is logged at the time you wake up. Meaning when getting stress and body battery data for February 28th 2026 the sleep score data would be found under March 1st 2026. This caused a lot of issues as we couldn't figure out how it was stored at first. For the current day we didn't have a sleep score yet so when testing the sleep score didn't exist yet.

## Accomplishments that we're proud of
We are super proud of getting the steam API working well enough to make this project feasible. We are also proud of getting two unrelated APIs working together to create something meaningful. We are most proud of building something that is easily scalable and genuinely useful.

## What we learned
We learned that API limitations often require creative engineering solutions. Since we found out the steam API doesn't save any previous gaming data we have to come up with a way to capture the data we needed to make this project happen. We also learned that visualization design matters as much as analysis when communicating insights. We spent a lot of time figuring out the best way to graph and show data trends that would be the most useful for gamers. We also learned new technologies like the garminConnectAPI, the steam API, python report library, and python matplotlib library.

## What's next for Recent Impacts of Gaming on Your Sleep and Mental Health
Future improvements include expanding use to other biometric health devices like apple watch or fitbit allowing it to be more accessible to different gamers. Another future implementation is real time stress spike alerts during an active gaming session so gamers can make active decisions to help their metnal health rather than see the data the next day. We would also integrate a web dashboard interface for insights making it super user friendly. Another thing would be adding machine learning based predictions of burnout or suggestions for a "healthy" gaming session creating almost a mental health companion catered towards gamers. This project truly has so much potential to grow and become accessible to all gamers and empower smarter gaming.
