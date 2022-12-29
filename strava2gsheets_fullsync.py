import time
import requests
import json
import six
import datetime as dt
import calendar

import pygsheets
import pandas as pd
from pandas import json_normalize

"""
Strava Stats stored in a Google Sheet
"""

url = "https://www.strava.com/api/v3"
client_id = "Your Strava client id"
client_secret = "Your Strava client secret"
refresh_token = "Your Strava refresh_token"

gsheet_name = "strava_activities"

api_cnt = 0
cur_row = 1

full_cols = {}
first_run=1

df_acti=pd.DataFrame()

class Error(Exception):
  """Generic error class."""


class WrongHTTPCode(Error):
  """Raised when Strava do not answer with 200 OK"""

def open_gsheet(gsheet_nam):

	#authorization
	gc = pygsheets.authorize()
	
	sh = gc.open(gsheet_nam)
	return (sh)

def Authenticate(client_id, client_secret, refresh_token):
	# Configure OAuth2 access token for authorization: strava_oauth

	url_auth = f"https://www.strava.com/oauth/token?client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token&refresh_token={refresh_token}"
	response = requests.post(url_auth)

	if response.status_code == 200:
		json_response=json.loads(response.text)
		auth_token = json_response["access_token"]
		return (auth_token)
	else:
		print ("Strava Authentication failed")
	return ()

def check_api (api_cnt):
	if (api_cnt>99):
		#Get current time
		now = dt.datetime.now()
		minutes=int(now.strftime('%M'))
		
		rem = minutes % 15
		
		print (f"Sleeping for {15-rem} minutes")
		time.sleep((15-rem)*60)
		api_cnt = 0


def Activity_Detail (auth_token, act_id, api_cnt):

	"""
	Parameters: 
	auth_token: Integer | Strava autehntication token
	act_id: Integer | Id of the activity to retrieve
	"""

	url_act = f"{url}/activities/{act_id}"
	headers = {}
	headers["Accept"] = "application/json"
	headers["Authorization"] = f"Bearer {auth_token}"
	
	check_api(api_cnt)
	response = requests.get(url_act,headers=headers)
	api_cnt+=1

	#TODO check response status

	json_response=json.loads(response.text)
	
	return(json_response)

def Activities (auth_token, api_cnt, page=1, before="", after="", ):

	"""
	Parameters: 
	page: Integer | Page number. Defaults to 1. (optional)
	before: Integer | An epoch timestamp to use for filtering activities that have taken place before a certain time. (optional)
	after: Integer | An epoch timestamp to use for filtering activities that have taken place after a certain time. (optional)
	"""

	url_act = f"{url}/athlete/activities?page={page}&per_page=200"
	headers = {}
	headers["Accept"] = "application/json"
	headers["Authorization"] = f"Bearer {auth_token}"
	
	check_api(api_cnt)
	response = requests.get(url_act,headers=headers)

	if not response.status_code == 200:
		print (response)
		
		if response.status_code == 429:
			api_cnt =100
			check_api(api_cnt)
			response = requests.get(url_act,headers=headers)
		else:
			raise WrongHTTPCode(f"Strava Server returned {response.status_code} response")
	
	json_response=json.loads(response.text)
	return(json_response)

def ConvertTime (seconds):
	m, s = divmod(seconds, 60)
	if m > 59:
		h, m = divmod(m, 60)
		return(f"{h:d}h{m:02d}m{s:02d}s")
	return(f"{m:02d}m{s:02d}s")

def Analyze_Activity_Page (json_act, df_acti, first_run, full_cols):

	print ("Analyzing Activity Page...")
	
	acti = json_normalize(json_act)

	if first_run == 1:

		#Add PR columns to dataframe
		acti["400m"] = ""
		acti["1/2 mile"] = ""
		acti["1k"] = ""
		acti["1 mile"] = ""
		acti["2 mile"] = ""
		acti["1 mile"] = ""
		acti["5k"] = ""
		acti["10k"] = ""
		acti["15k"] = ""
		acti["10 mile"] = ""
		acti["20k"] = ""
		acti["Half-Marathon"] = ""
	
		df_acti=acti
		
		first_run = 0
		
		full_cols=list(df_acti)
		
	else:
		cols = list(acti)
		
		cols = list(set(full_cols) - set(cols))
		
		for col in cols:
			acti[col]=""
			#print (f"Adding column {col}")
		
		#Resorting acti index as the orginal columns
		acti = acti[full_cols]
		
		#Concatenate the two dataframes
		df_acti=pd.concat([df_acti,acti], axis=0, join='outer', ignore_index=True)
	
	row=0;
	
	for act in json_act:
		#if there's a running PR, need to get the detailed activity
		if act['pr_count'] > 0 and act['sport_type'] == "Run":
			json_det = Activity_Detail (auth_token, act['id'], api_cnt)
			#print (f"{json.dumps(json_det, indent=2,separators=(six.ensure_str(','), six.ensure_str(': ')))}")
			if "best_efforts" in json_det.keys():
				best_efforts = json_det['best_efforts']

				for be in best_efforts:
				
					#Check only the best PR (rank==1)
					if be['pr_rank'] == 1:
						#print (f"Found PR for {be['name']}")
						df_acti.at[row,be['name']] = be['moving_time']

						
		row+=1

	return (first_run, full_cols, df_acti)

auth_token=Authenticate(client_id, client_secret, refresh_token)

#Open Google Sheet
sh=open_gsheet(gsheet_name)
#select the first sheet 
wks = sh[0]

# Collect Strava Data
page=1
json_act = Activities(auth_token,api_cnt, page)

#print (f"{json.dumps(json_act, indent=2,separators=(six.ensure_str(','), six.ensure_str(': ')))}")

while not json_act == []:
	#Extract statistics from activity page
	first_run, full_cols, df_acti=Analyze_Activity_Page(json_act, df_acti, first_run, full_cols)

	#Save DataFrame in GSheet (Row,column)
	#wks.set_dataframe(df_acti,(cur_row,1))
	#cur_row+=df.shape[0]
	
	page+=1
	json_act = Activities(auth_token,api_cnt, page)
	
	#print (f"{json.dumps(json_act, indent=2,separators=(six.ensure_str(','), six.ensure_str(': ')))}")

wks.set_dataframe(df_acti,(1,1))