import rasterio
from rasterio.io import MemoryFile
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import sys
import os
from util import handle_retry

hcdp_api_token = os.environ.get('HCDP_API_TOKEN')
num_agg_maps = 180

def aggregate_map(date, extent, repeat_times, agg_map, n_agg):
    found = False
    date_s = date.strftime("%Y-%m-%d")
    #URL for API raster request
    raster_url = f"https://api.hcdp.ikewai.org/raster?date={date_s}&extent={extent}&datatype=rainfall&production=new&period=day"
    #prepare request
    req = urllib.request.Request(raster_url)
    #add auth header to request
    req.add_header("Authorization", f"Bearer {hcdp_api_token}")
    try:
        #open remote file
        with urllib.request.urlopen(req, timeout = 5) as f:
            #wrap file handle in rasterio memory file
            with MemoryFile(f) as mem_f:
                #open the memory file as a rasterio object
                with mem_f.open() as data:
                    #initialize agg map if first one
                    if agg_map is None:
                        #set agg map to current map's first band (mask nodata)
                        agg_map = data.read(1, masked = True)
                        #less one map and repeat
                        n_agg -= 1
                        repeat_times -= 1
                    #repeat the file until max reached or repeats are exhausted
                    while repeat_times > 0 and n_agg > 0:
                        #add current map to aggregation map
                        agg_map += data.read(1, masked = True)
                        #less one map and repeat
                        n_agg -= 1
                        repeat_times -= 1
        found = True
    except urllib.error.HTTPError as e:
        #file was not found, repeat the next file an additional time
        if e.code != 404:
            raise e
        print(f"Rainfall not found for {extent}, {date_s}...")
    return (found, n_agg, agg_map)


def generate_api_k1(agg_date, extent, n_agg = 180):
    #Generates the [n_agg] sum of rainfall (default 180 days)
    repeat_times = 1
    agg_map = None
    #clone agg date as starting date
    date = agg_date.replace()
    while n_agg > 0:
        found, n_agg, agg_map = handle_retry(aggregate_map, (date, extent, repeat_times, agg_map, n_agg))
        #reset repeat to 1
        if(found):
            repeat_times = 1
        #repeat next map one more time
        else:
            repeat_times += 1
        date = date - timedelta(days = 1)
    return agg_map

if __name__ == "__main__":
    agg_date = None
    extent = sys.argv[1] #required
    #check if an aggregation date was passed
    if len(sys.argv) > 2:
        input_date = sys.argv[2]
        agg_date = parser.parse(input_date)
    #default to yesterday
    else:
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        agg_date = today - timedelta(days = 1)

    api = generate_api_k1(agg_date, extent, num_agg_maps)
    local_dep_dir = os.environ.get('DEPENDENCY_DIR')
    with rasterio.open(local_dep_dir + 'ref_'+extent+'.tif','r') as raster:
        profile = raster.profile
    
    api_file = local_dep_dir + 'API_'+extent+'.tif'
    with rasterio.open(api_file,'w',**profile) as dst:
        dst.write(api,1)

