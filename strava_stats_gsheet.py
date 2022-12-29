import datetime
import pygsheets
import pandas as pd
import calendar
import math
from PIL import Image, ImageDraw, ImageFont

"""
Strava Yearly Stats from Google Sheet

1) Top activity, % of each activities
2) Number of active days, compared to last year + graph with each day of the year + graph for each month
2a) Number of activities, compared to last year
3) Amount of hours of activities + hours of each month + compared to last year
4) Distance + distance per month + compared to last year
5) Elevation + graph for each month + compared to last year
6) Number of new Personal Records + PR for each distance in the year
7) Longest hike in distance, time, name and date
8) Run: average run length in km and duration,  average pace, longest run
9) Total distance, distance per month, total time, time per month
10) day most run on w/ average km and number of times, Day least often run on w/ average km and number of times, average run per week

TODO
- Kudos, kudos received, kudos given***, most kudos activity

RUN
- 5 best times for 5K, 10K, 10M, Half Marathon
- correlation run pace vs temperature
"""

year=2022

#epoch time for the beginning of the year
start_year=datetime.datetime(year,1,1,0,0,0)
ep_st_year=calendar.timegm(start_year.timetuple())
#print (ep_st_year)

#epoch time for the end of the year
end_year=datetime.datetime(year,12,31,23,59,59)
ep_end_year=calendar.timegm(end_year.timetuple())
#print (ep_end_year)

#epoch time for the beginning of the year-1
start_prvyear=datetime.datetime(year-1,1,1,0,0,0)
ep_st_prvyear=calendar.timegm(start_prvyear.timetuple())
#print (ep_st_prvyear)

#epoch time for the end of the year-1
end_prvyear=datetime.datetime(year-1,12,31,23,59,59)
ep_end_prvyear=calendar.timegm(end_prvyear.timetuple())
#print (ep_end_prvyear)

#Requested year variables
year_stats = {}
#Initialize the year counters
year_stats['activities'] = 0
year_stats['distance'] = 0
year_stats['time'] = 0
year_stats['rcv_kudos'] = 0
year_stats['elevation'] = 0
year_stats['nb_pr'] = 0
year_stats['runs'] = 0
year_stats['run_distance'] = 0
year_stats['run_time'] = 0
# List of all the best efforts of the year (PR)
year_stats['best_eff'] = {}
# List of all the sports of the year
year_stats['sports'] = {}
#Stats for each month of the year
year_stats['months'] = {}
year_stats['run_months'] = {}
year_stats['dow'] = {}
year_stats['woy'] = {}
#store the active days of the year
year_stats['days'] = {}
#PR times of the year
year_stats['pr'] = {}
year_stats['pr_date'] = {}
year_stats['nb_days'] = 0


#Previous year variables
prv_year_stats = {}
#Initialize the previous year counters
prv_year_stats['activities'] = 0
prv_year_stats['distance'] = 0
prv_year_stats['time'] = 0
prv_year_stats['rcv_kudos'] = 0
prv_year_stats['elevation'] = 0
prv_year_stats['nb_pr'] = 0
prv_year_stats['runs'] = 0
prv_year_stats['run_distance'] = 0
prv_year_stats['run_time'] = 0
# List of all the sports of the previous year
prv_year_stats['sports'] = {}
#store the active days of the previous year
prv_year_stats['days'] = {}

gsheet_name = "strava_activities"

def OpenGSheet(sh_name):
	#Get authorization
	gc = pygsheets.authorize()
	
	#Open the GSheet file
	sh = gc.open(sh_name)
	
	#select the first sheet in the file
	wks = sh[0]
	
	return (wks)

def ConvertTime (seconds):
	m, s = divmod(seconds, 60)
	if m > 59:
		h, m = divmod(m, 60)
		return(f"{h:d}h{m:02d}m{s:02d}s")
	return(f"{m:02d}m{s:02d}s")

def GenerateActiveDays(stats):

	#Generate image for the active days of the year
	im = Image.new('RGB', (600, 700), (241, 242, 114))
	draw = ImageDraw.Draw(im)

	myFont = ImageFont.truetype('strava_font.otf', 16)

	for m in range(1,13,1):

		range_days=calendar.monthrange(2022, m)

		for d in range(1,range_days[1]+1,1):
			if f"{year}-{str(m).zfill(2)}-{str(d).zfill(2)}" in stats['days'].keys():
				draw.ellipse((35*m, 20*d, 35*m+12, 20*d+12), fill=(230, 90, 43))
			else:
				draw.ellipse((35*m, 20*d, 35*m+12, 20*d+12), fill=(255, 255, 255))

		date=datetime.datetime(2022,m,1)
		st_month=date.strftime('%b')
		draw.text((35*m+6, 650), st_month, font=myFont, fill =(0, 0, 0), anchor="mt")

	im.save(f"active_days_{year}.jpg", quality=95)

	return()

def analyze_data (activities, stats, prev=0):

	if prev:
		print (f"Analyzing year {year-1}")
	else:
		print (f"Analyzing year {year}")
		
	for index, act in activities.iterrows():
		#print (act)
		stats['distance']+=(int(act['distance'])/1000)
		stats['time']+=act['moving_time']
		if act['kudos_count'] > 0:
			if "most_kudos" in stats.keys():
				if act['kudos_count'] > stats["most_kudos"]:
					stats["most_kudos_name"]=act['name']
					stats["most_kudos_date"]=act['start_date_local'].strftime('%a %d %B %Y')
					stats["most_kudos"] = act['kudos_count']
					
			else:
				stats["most_kudos"] = act['kudos_count']
				stats["most_kudos_name"]=act['name']
				stats["most_kudos_date"]=act['start_date_local'].strftime('%a %d %B %Y')
				
			stats['rcv_kudos']+=act['kudos_count']
		
		stats['activities']+=1
		stats['elevation']+=act['total_elevation_gain']

		#Check if the sport type is already in the dictionary, if yes, add une occurence of the sport
		if  act['sport_type'] in stats['sports'].keys():
			stats['sports'][act['sport_type']]+=1
		#if no, initialize the sport to 1
		else:
			stats['sports'][act['sport_type']]=1
		
		stats['nb_pr']+=act['pr_count']
		
		#Mark the day of the activity as active
		stats['days'][act['start_date_local'].date().isoformat()] = 1

		if act['type'] == "Run":
			stats['run_distance'] += (int(act['distance'])/1000)
			stats['run_time'] += act['moving_time']
			stats['runs']+=1

		
		# Advanced stats only for the requested year, not previous year
		if prev == 0:

			#if there's a PR, need to get the detailed activity
			if act['pr_count'] > 0 and act['sport_type'] == "Run":
				for pr in ('400m','1/2 mile','1k','1 mile','2 mile','5k','10k','15k','10 mile','20k','Half-Marathon'):
					if act[pr]:
						stats['pr'][pr]=act[pr]
						stats['pr_date'][pr]=act['start_date_local'].strftime('%a %d %B %Y')
			
			if not act['start_date_local'].strftime('%b') in stats['months'].keys():
				stats['months'][act['start_date_local'].strftime('%b')] = {}
			
			#Add time to the month of the activity
			if  'time' in stats['months'][act['start_date_local'].strftime('%b')].keys():
				stats['months'][act['start_date_local'].strftime('%b')]['time']+=act['moving_time']
			else:
				stats['months'][act['start_date_local'].strftime("%b")]['time']=act['moving_time']

			#Add distance to the month of the activity
			if  'distance' in stats['months'][act['start_date_local'].strftime('%b')].keys():
				stats['months'][act['start_date_local'].strftime('%b')]['distance']+=act['distance']/1000
			else:
				stats['months'][act['start_date_local'].strftime("%b")]['distance']=act['distance']/1000

			#Add active day to the month of the activity
			if  'active' in stats['months'][act['start_date_local'].strftime('%b')].keys():
				stats['months'][act['start_date_local'].strftime('%b')]['active']+=1
			else:
				stats['months'][act['start_date_local'].strftime("%b")]['active']=1
			
			#Add elevation to the month of the activity
			if  'elevation' in stats['months'][act['start_date_local'].strftime('%b')].keys():
				stats['months'][act['start_date_local'].strftime('%b')]['elevation']+=act['total_elevation_gain']
			else:
				stats['months'][act['start_date_local'].strftime("%b")]['elevation']=act['total_elevation_gain']
			
			# Hike stats
			if act['type'] == "Hike":
				if 'hike_distance' in stats.keys():
					if act['distance']/1000 > stats['hike_distance']:
						stats['hike_distance'] = act['distance'] / 1000
						stats['hike_time'] = act['moving_time']
						stats['hike_name'] = act['name']
						stats['hike_date'] = act['start_date_local'].strftime('%a %d %B %Y')
				else:
					stats['hike_distance'] = act['distance'] / 1000
					stats['hike_time'] = act['moving_time']
					stats['hike_name'] = act['name']
					stats['hike_date'] = act['start_date_local'].strftime('%a %d %B %Y')

			#Run stats
			if act['type'] == "Run":
				if 'longrun_distance' in stats.keys():
					if act['distance']/1000 > stats['longrun_distance']:
						stats['longrun_distance'] = act['distance'] / 1000
						stats['longrun_time'] = act['moving_time']
						stats['longrun_name'] = act['name']
						stats['longrun_date'] = act['start_date_local'].strftime('%a %d %B %Y')
				else:
					stats['longrun_distance'] = act['distance'] / 1000
					stats['longrun_time'] = act['moving_time']
					stats['longrun_name'] = act['name']
					stats['longrun_date'] = act['start_date_local'].strftime('%a %d %B %Y')

				#Monthly run statistics
				if not act['start_date_local'].strftime('%b') in stats['run_months'].keys():
					stats['run_months'][act['start_date_local'].strftime('%b')] = {}
				
				#Add time to the month of the run
				if  'time' in stats['run_months'][act['start_date_local'].strftime('%b')].keys():
					stats['run_months'][act['start_date_local'].strftime('%b')]['time']+=act['moving_time']
				else:
					stats['run_months'][act['start_date_local'].strftime("%b")]['time']=act['moving_time']

				#Add distance to the month of the run
				if  'distance' in stats['run_months'][act['start_date_local'].strftime('%b')].keys():
					stats['run_months'][act['start_date_local'].strftime('%b')]['distance']+=act['distance']/1000
				else:
					stats['run_months'][act['start_date_local'].strftime("%b")]['distance']=act['distance']/1000

				#Add run to the month
				if  'runs' in stats['run_months'][act['start_date_local'].strftime('%b')].keys():
					stats['run_months'][act['start_date_local'].strftime('%b')]['runs']+=1
				else:
					stats['run_months'][act['start_date_local'].strftime("%b")]['runs']=1
				

				#Day of the week run statistics
				if not act['start_date_local'].strftime('%A') in stats['dow'].keys():
					stats['dow'][act['start_date_local'].strftime('%A')] = {}

				#Add time to the day of the run
				if  'time' in stats['dow'][act['start_date_local'].strftime('%A')].keys():
					stats['dow'][act['start_date_local'].strftime('%A')]['time']+=act['moving_time']
				else:
					stats['dow'][act['start_date_local'].strftime("%A")]['time']=act['moving_time']

				#Add distance to the day of the run
				if  'distance' in stats['dow'][act['start_date_local'].strftime('%A')].keys():
					stats['dow'][act['start_date_local'].strftime('%A')]['distance']+=act['distance']/1000
				else:
					stats['dow'][act['start_date_local'].strftime("%A")]['distance']=act['distance']/1000

				#Add run to day to the week
				if  'runs' in stats['dow'][act['start_date_local'].strftime('%A')].keys():
					stats['dow'][act['start_date_local'].strftime('%A')]['runs']+=1
				else:
					stats['dow'][act['start_date_local'].strftime("%A")]['runs']=1
				
				#Week of the year stats
				if not act['start_date_local'].strftime('%U') in stats['woy'].keys():
					stats['woy'][act['start_date_local'].strftime('%U')] = 1
				else:
					stats['woy'][act['start_date_local'].strftime('%U')] += 1

	return(stats)

def PrintResults (stats, prv_stats):
	
	print("")
	print (f"Statistics for year {year}")
	print ("===========================")
	print (f"Top Sports in {year}")
	print (f"{stats['activities']} activities in {year}")
	print (f"{prv_stats['activities']} activities in {year-1}")
	for i in stats['sports'].keys():
		print (f"{i}: {stats['sports'][i]} activities")
	print (f"Top Sports in {year-1}")
	for i in prv_stats['sports'].keys():
		print (f"{i}: {prv_stats['sports'][i]} activities")
	print (f"Active days in {year}: {stats['nb_days']}")
	print (f"Active days in {year-1}: {prv_stats['nb_days']}")
	print (f"Number of hours in {year}: {stats['time']}")
	print (f"Number of hours in {year-1}: {prv_stats['time']}")
	print (f"Distance in {year}: {round(stats['distance'])}")
	print (f"Distance in {year-1}: {round(prv_stats['distance'])}")
	print (f"Elevation in {year}: {round(stats['elevation'])}")
	print (f"Elevation in {year-1}: {round(prv_stats['elevation'])}")
	print ("")
	print ("Days active")
	print ("===========")
	print (f"Days active in {year}: {stats['nb_days']}")
	print (f"Days active in {year-1}: {prv_stats['nb_days']}")
	# TODO create graph for active days per month
	print ("")
	print (f"Sports details in {year}")
	print ("=========================")
	for i in stats['sports'].keys():
		pct = round(stats[f"pct_{i}"])
		print (f"{i}: {stats['sports'][i]} activities - {pct}%")
	print ("---------------------------")
	print (f"Sports details in {year-1}")
	print ("---------------------------")
	for i in prv_stats['sports'].keys():
		pct = round(prv_stats[f"pct_{i}"])
		print (f"{i}: {prv_stats['sports'][i]} activities - {pct}%")
	# TODO create graph for activities per sport in the year
	print ("")
	print ("Achievements")
	print ("============")
	print (f"{stats['nb_pr']} personal records including:")
	for i in ('400m','1/2 mile','1k','1 mile','2 mile','5k','10k','15k','10 mile','20k','Half-Marathon'):
		if i in stats['pr'].keys():
			print (f"{i}: {stats['pr'][i]} on {stats['pr_date'][i]}")
	print ("")
	print ("Total Time")
	print ("==========")
	print (f"Total time in {year}: {stats['time']}")
	print (f"Total time in {year-1}: {prv_stats['time']}")
	for i in stats['months'].keys():
		print(f"{i}: {stats['months'][i]['time']}")
	# TODO create time graph per month
	print ("")
	print ("Total distance")
	print ("==============")
	print (f"Total distance in {year}: {round(stats['distance'])} km")
	print (f"Total distance in {year-1}: {round(prv_stats['distance'])} km")
	for i in stats['months'].keys():
		print(f"{i}: {round(stats['months'][i]['distance'])} km")
	# TODO create distance graph per month
	print ("")
	print ("Total kudos")
	print ("==============")
	print (f"Total kudos received in {year}: {stats['rcv_kudos']}")
	print (f"Most kudo'd activity in {year}: {stats['most_kudos']} kudos for {stats['most_kudos_name']} on {stats['most_kudos_date']}")
	print ("")
	print ("Total elevation")
	print ("==============")
	print (f"Total elevation in {year}: {round(stats['elevation'])} m")
	print (f"Total elevation in {year-1}: {round(prv_stats['elevation'])} m")
	for i in stats['months'].keys():
		print(f"{i}: {round(stats['months'][i]['elevation'])} m")
	# TODO create elevation graph per month
	print ("")
	print (f"Hikes in {year}")
	print ("==============")
	print (f"{stats['sports']['Hike']} hikes in {year}")
	print (f"{prv_stats['sports']['Hike']} hikes in {year-1}")
	print (f"Longest hike: {round(stats['hike_distance'])} km - {ConvertTime(stats['hike_time'])}")
	print (f"Longest hike: {stats['hike_name']} on {stats['hike_date']}")
	print ("")
	print (f"Runs in {year}")
	print ("==============")
	print (f"{stats['sports']['Run']} runs in {year}")
	print (f"{prv_stats['sports']['Run']} runs in {year-1}")
	print (f"Run distance in {year}: {round(stats['run_distance'])} km")
	print (f"Run distance in {year-1}: {round(prv_stats['run_distance'])} km")
	print (f"Run time in {year}: {ConvertTime(stats['run_time'])}")
	print (f"Run time in {year-1}: {ConvertTime(prv_stats['run_time'])}")
	for i in stats['run_months'].keys():
		print(f"{i}: {round(stats['run_months'][i]['runs'])} runs - {round(stats['run_months'][i]['distance'])} km - {ConvertTime(stats['run_months'][i]['time'])}")
	print (f"Average run distance in {year}: {round(stats['run_distance']/stats['sports']['Run'],2)} km")
	print (f"Average run distance in {year-1}: {round(prv_stats['run_distance']/prv_stats['sports']['Run'],2)} km")
	print (f"Average run duration in {year}: {ConvertTime(round(stats['run_time']/stats['sports']['Run']))}")
	print (f"Average run duration in {year-1}: {ConvertTime(round(prv_stats['run_time']/prv_stats['sports']['Run']))}")
	#Calculate average pace
	pace=stats['run_time']/stats['run_distance']
	#Convert in min/km
	pacesec=round(pace%60)
	pace=math.floor(pace/60)
	pace=f"{pace}m{pacesec}s"
	print (f"Average run pace in {year}: {pace}")
	#Calculate average pace
	pace=prv_stats['run_time']/prv_stats['run_distance']
	#Convert in min/km
	pacesec=round(pace%60)
	pace=math.floor(pace/60)
	pace=f"{pace}m{pacesec}s"
	print (f"Average run pace in {year-1}: {pace}")
	for i in stats['dow'].keys():
		print(f"{i}: {round(stats['dow'][i]['runs'])} runs - {round(stats['dow'][i]['distance'])} km - {ConvertTime(stats['dow'][i]['time'])}")
	print (f"Longest run: {round(stats['longrun_distance'],2)} km - {ConvertTime(stats['longrun_time'])}")
	print (f"Longest run: {stats['longrun_name']} on {stats['longrun_date']}")
	nb_weeks = len(stats['woy'])
	print (f"Average runs per week: {round(stats['sports']['Run']/nb_weeks,1)}")
	return()
	
#Open Google Sheet
sh=OpenGSheet(gsheet_name)

#Get the values
activities_df = sh.get_as_df()

#print (activities_df)

#Convert the local time column in datetime format
activities_df['start_date_local']=pd.to_datetime(activities_df['start_date_local'])

#print (activities_df.start_date_local)

#Filter the data for the selected year
act_year = activities_df.loc[activities_df['start_date_local'].dt.year == year]

# print (act_year)

year_stats = analyze_data(act_year, year_stats)

#Filter the data for the previous year
act_year = activities_df.loc[activities_df['start_date_local'].dt.year == year-1]

prv_year_stats = analyze_data(act_year, prv_year_stats, 1)

#Calculate the percent for each sport
for k in year_stats['sports'].keys():
	year_stats[f"pct_{k}"] = year_stats['sports'][k]/year_stats['activities']*100

#Calculate the percent for each sport in previous year
for k in prv_year_stats['sports'].keys():
	prv_year_stats[f"pct_{k}"] = prv_year_stats['sports'][k]/prv_year_stats['activities']*100
	
#Convert the times in H:m:s
year_stats['time'] = ConvertTime(year_stats['time'])
prv_year_stats['time'] = ConvertTime(prv_year_stats['time'])

for m in range(1, 13):
	d=datetime.date(2022,m,1)
	year_stats['months'][d.strftime('%b')]["time"] = ConvertTime(year_stats['months'][d.strftime('%b')]["time"])

for k in year_stats['pr'].keys():
	year_stats['pr'][k] = ConvertTime(year_stats['pr'][k])

#Calculate number of active days
year_stats['nb_days'] = len(year_stats['days'].keys())
prv_year_stats['nb_days'] = len(prv_year_stats['days'].keys())

PrintResults(year_stats,prv_year_stats)

GenerateActiveDays(year_stats)
