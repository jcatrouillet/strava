# Strava backup and statistics/analytics scripts

In 2022, Strava started to make the yearly statistics as part of the subscription.
I love statistics but I did not intend to pay for Strava subscription just for that.
So I created this set of scripts to get my own statistics, freely inspired by the Strava 2021 stastistics and [SmashRun](https://smashrun.com/).

There're three different Python scripts:
1) <b>strava2gsheets_fullsync.py</b>: Retrieve all activities from Strava API v3 and store them in Google Sheet
Be careful if you have a large number of activities in Strava as it imposes a rate-limit of 100 API calls per 15 minutes.
My script is looking for this limit but if you're doing other calls, it can get wrong.

2) <b>strava2gsheets_deltaupdate.py</b>: Retrieve activities not already stored in Google Sheet

To use the 2 scripts above, you will need to setup a Strava app, follow the steps [here](https://developers.strava.com/docs/getting-started/)

3) <b>strava_stats_gsheet.py</b>: Analyze the Google Sheet to generate yearly statistics like Strava used to give for free in the past
This script will produce two outputs:

  a) an image with your days of the year with activities (file named active_days_<year>.jpg) like this one:
![example of graph generated](https://github.com/jcatrouillet/strava/blob/main/active_days_2022.jpg)

  b) a console output that you can use to create your own presentation like [that](https://github.com/jcatrouillet/strava/blob/main/Strava%20stats%202022.odp). Here is a sample output:

```
Analyzing year 2022
Analyzing year 2021

Statistics for year 2022
===========================
Top Sports in 2022
221 activities in 2022
222 activities in 2021
Run: 174 activities
Walk: 31 activities
Workout: 5 activities
Hike: 9 activities
Ride: 2 activities
Dec: 15 activities
Nov: 25 activities
Oct: 18 activities
Sep: 18 activities
Aug: 18 activities
Jul: 29 activities
Jun: 14 activities
May: 17 activities
Apr: 13 activities
Mar: 16 activities
Feb: 18 activities
Jan: 20 activities
Top Sports in 2021
Hike: 14 activities
Run: 127 activities
Workout: 2 activities
Walk: 30 activities
Ride: 32 activities
Rowing: 17 activities
Active days in 2022: 199
Active days in 2021: 186
Number of hours in 2022: 190h19m25s
Number of hours in 2021: 155h34m26s
Distance in 2022: 1540
Distance in 2021: 1333
Elevation in 2022: 8062
Elevation in 2021: 5977

Days active
===========
Days active in 2022: 199
Days active in 2021: 186

Sports details in 2022
=========================
Run: 174 activities - 79%
Walk: 31 activities - 14%
Workout: 5 activities - 2%
Hike: 9 activities - 4%
Ride: 2 activities - 1%
---------------------------
Sports details in 2021
---------------------------
Hike: 14 activities - 6%
Run: 127 activities - 57%
Workout: 2 activities - 1%
Walk: 30 activities - 14%
Ride: 32 activities - 14%
Rowing: 17 activities - 8%

Achievements
============
97 personal records including:
400m: 01m52s on Sat 15 October 2022
1/2 mile: 03m51s on Sun 13 November 2022
1k: 04m49s on Sun 13 November 2022
1 mile: 07m53s on Sat 15 October 2022
2 mile: 17m03s on Thu 25 August 2022
5k: 27m16s on Mon 19 December 2022
10k: 59m04s on Sun 23 October 2022
15k: 1h32m22s on Sun 06 November 2022
10 mile: 1h38m58s on Sun 06 November 2022
20k: 2h04m09s on Sun 06 November 2022
Half-Marathon: 2h11m29s on Sun 06 November 2022

Total Time
==========
Total time in 2022: 190h19m25s
Total time in 2021: 155h34m26s
Dec: 14h09m15s
Nov: 17h48m24s
Oct: 14h01m15s
Sep: 12h07m33s
Aug: 11h18m52s
Jul: 21h48m05s
Jun: 22h49m05s
May: 19h26m35s
Apr: 16h44m18s
Mar: 13h05m19s
Feb: 12h54m17s
Jan: 14h06m27s

Total distance
==============
Total distance in 2022: 1540 km
Total distance in 2021: 1333 km
Dec: 139 km
Nov: 145 km
Oct: 130 km
Sep: 101 km
Aug: 106 km
Jul: 147 km
Jun: 153 km
May: 148 km
Apr: 115 km
Mar: 116 km
Feb: 113 km
Jan: 126 km

Total kudos
==============
Total kudos received in 2022: 1161
Most kudo'd activity in 2022: 16 kudos for Golden Gate Half Marathon 2022 on Sun 06 November 2022

Total elevation
==============
Total elevation in 2022: 8062 m
Total elevation in 2021: 5977 m
Dec: 651 m
Nov: 784 m
Oct: 402 m
Sep: 734 m
Aug: 152 m
Jul: 781 m
Jun: 1896 m
May: 277 m
Apr: 1686 m
Mar: 143 m
Feb: 381 m
Jan: 174 m

Hikes in 2022
==============
9 hikes in 2022
14 hikes in 2021
Longest hike: 29 km - 7h37m33s
Longest hike: ⛅ Morning Hike - Half Dome on Tue 07 June 2022

Runs in 2022
==============
174 runs in 2022
127 runs in 2021
Run distance in 2022: 1255 km
Run distance in 2021: 893 km
Run time in 2022: 131h29m03s
Run time in 2021: 94h22m35s
Dec: 15 runs - 139 km - 14h09m15s
Nov: 17 runs - 130 km - 13h22m32s
Oct: 17 runs - 126 km - 12h50m58s
Sep: 16 runs - 93 km - 9h53m00s
Aug: 14 runs - 99 km - 10h08m48s
Jul: 12 runs - 86 km - 9h14m30s
Jun: 8 runs - 67 km - 7h34m02s
May: 15 runs - 106 km - 11h29m08s
Apr: 11 runs - 77 km - 8h24m50s
Mar: 15 runs - 106 km - 11h21m41s
Feb: 16 runs - 105 km - 10h48m51s
Jan: 18 runs - 120 km - 12h11m28s
Average run distance in 2022: 7.21 km
Average run distance in 2021: 7.03 km
Average run duration in 2022: 45m20s
Average run duration in 2021: 44m35s
Average run pace in 2022: 6m17s
Average run pace in 2021: 6m21s
Thursday: 2 runs - 12 km - 1h10m54s
Wednesday: 35 runs - 200 km - 20h09m03s
Monday: 37 runs - 217 km - 22h26m32s
Sunday: 46 runs - 523 km - 56h15m31s
Friday: 45 runs - 246 km - 25h05m06s
Saturday: 7 runs - 44 km - 5h00m48s
Tuesday: 2 runs - 13 km - 1h21m09s
Longest run: 21.38 km - 2h16m42s
Longest run: Morning Run on Sun 16 October 2022
Average runs per week: 3.3
```
