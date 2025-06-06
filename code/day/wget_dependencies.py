import os
import sys
import pytz
import requests
import pandas as pd
from datetime import datetime, timedelta
from util import handle_retry
from os.path import join

local_dep_dir = os.environ.get('DEPENDENCY_DIR')
hcdp_api_token = os.environ.get('HCDP_API_TOKEN')
county_list = ['bi','ka','mn','oa']
datasets = [({"datatype": "ndvi_modis"}, "NDVI"), ({"datatype": "rainfall", "production": "new"}, "Preciptation"), ({"datatype": "temperature", "aggregation": "max"}, "Tmax"), ({"datatype": "relative_humidity"}, "RH")]

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
    

for county in county_list:
    for dataset, fname_prefix in datasets:
        outf = join(local_dep_dir, f"{fname_prefix}_{county}.tif")
        get_last_raster(targ_dt, county, dataset, outf)