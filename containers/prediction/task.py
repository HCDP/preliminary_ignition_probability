from prefect import flow, task
from os import environ
from pytz import timezone
from datetime import datetime, timedelta
import subprocess
from dotenv import load_dotenv
from os import chdir

load_dotenv("/workspace/envs/prod.env")


@flow(log_prints = True)
def get_dependencies(date):
  subprocess.run(["python3", "-W", "ignore", "/workspace/code/prediction/wget_dependencies.py", date])
  
  
@flow(log_prints = True)
def generate_county_map(county, date):
  subprocess.run(["python3", "-W", "ignore", "/workspace/code/prediction/generate_ignition_forecast.py", county, date])
  
@flow(log_prints = True)
def mosaic_maps():
  subprocess.run(["python3", "-W", "ignore", "/workspace/code/prediction/statewide_mosaic.py"])


@flow(log_prints = True)
def inject_upload_config(config_file, date):
  subprocess.run(["python3", "inject_upload_config.py", config_file, date])
  
  
@flow(log_prints = True)
def upload_data():
  subprocess.run(["python3", "upload.py"])


@task
def run_ignition_probability_prediction(date):
  get_dependencies()
  counties = ["bi", "ka", "mn", "oa"]
  for county in counties:
    generate_county_map(county, date)
  mosaic_maps()
  chdir("/sync")
  inject_upload_config("config.json", date)
  upload_data()
  
  
if __name__ == "__main__":
  date_s = environ.get("CUSTOM_DATE")
  if date_s is None:
    hst = timezone('HST')
    today = datetime.today().astimezone(hst)
    date = today - timedelta(days = 1)
    date_s = date.strftime('%Y-%m-%d')
  run_ignition_probability_prediction(date_s)