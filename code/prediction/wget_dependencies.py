import os
import sys
import pytz
import requests
import pandas as pd
from datetime import datetime, timedelta
from util import handle_retry
from os.path import join

local_dep_dir = os.environ.get('PREDICTOR_DIR') #/home/hawaii_climate_products_container/preliminary/ignition_probability/code/prediction/dependencies/
hcdp_api_token = os.environ.get('HCDP_API_TOKEN')
county_list = ['bi','ka','mn','oa']
datasets = [({"datatype": "ignition_probability"}, "Probability")]
seq_length = int(os.environ.get("SEQ"))

def dataset2params(dataset):
    return "&".join("=".join(item) for item in dataset.items())

def get_raster(date, county, dataset, outf):
    date_s = date.strftime('%Y-%m-%d')
    url = f"https://api.hcdp.ikewai.org/raster?period=day&date={date_s}&extent={county}&{dataset2params(dataset)}&returnEmptyNotFound=False"
    found = False
    try:
        req = requests.get(url, headers = {'Authorization': f'Bearer {hcdp_api_token}'}, timeout = 5)
        req.raise_for_status()
        with open(outf, 'wb') as f:
            f.write(req.content)
        found = True
        print(f"Found raster for {county} dataset {dataset} for date {date_s}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code != 404:
            raise e
    return found

#reset date for each dataset
def get_last_raster(date, county, dataset, outf):
    while True:
        found = handle_retry(get_raster, (date, county, dataset, outf))
        if(found):
            break
        date -= timedelta(days = 1)
    return date

targ_dt = None
if len(sys.argv) > 1:
    #Set input to specific date
    target_date = sys.argv[1]
    targ_dt = pd.to_datetime(target_date)
else:
    #Set to previous day
    hst = pytz.timezone('HST')
    today = datetime.today().astimezone(hst)
    targ_dt = today - timedelta(days = 1)

#Perform this fetch for all n days in input sequence
fetched_dates = []
for lag_n in range(seq_length):
    #should go from 0 to seq_length-1
    #lead/lag 0 day == "targ_dt" most recent condition OR user-specified date
    lag_dt = targ_dt - timedelta(days=lag_n)
    print(lag_dt)

    for county in county_list:
        for dataset, fname_prefix in datasets:
            outf = join(local_dep_dir,"predictors",county, f"{fname_prefix}_{county}_lag{str(lag_n)}.tif") #restore after test
            actual_date = get_last_raster(lag_dt, county, dataset, outf)
            fetched_dates.append(county+' '+actual_date.strftime('%Y-%m-%d'))
date_str = targ_dt.strftime('%Y-%m-%d')
date_fname = local_dep_dir + f"input_date_list_{date_str}.txt"
with open(date_fname,"w") as date_file:
    date_file.write("\n".join(str(i) for i in fetched_dates))
            
