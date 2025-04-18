#Adapts scripts from [creator] with following defaults:
#--N-seq = 4
#--days ahead = 3
#--NO_INTERACTIVE
import sys
import os
import re
import numpy as np
import rasterio
import pytz
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model
from matplotlib.colors import LinearSegmentedColormap
from os.path import exists

MASTER_DIR = os.environ.get("PROJECT_ROOT") #/home/hawaii_climate_products_container/preliminary/ignition_prob/
N_SEQ = int(os.environ.get("SEQ"))
N_LEAD = int(os.environ.get("LEAD"))
NO_DATA_VAL = int(os.environ.get("NO_DATA_VAL"))

DEP_DIR = MASTER_DIR + "code/prediction/dependencies/"
OUTPUT_DIR = MASTER_DIR + "data_outputs/prediction/tiff/"

###############################################################################
# Write GeoTiff out (1 day, 1 county)
###############################################################################
def output_tiff(data_arr,county,days_ahead):
    #Set reference tiff as the lead0 file
    ref_tiff = os.path.join(DEP_DIR,"predictors/",county,"_".join(("Probability",county,"lag0"))+".tif") #set file name structure
    output_file_name = os.path.join(OUTPUT_DIR,"_".join(("Probability",county,"lead"+"{:02d}".format(days_ahead))))+".tif"
    #Get tiff profile from reference
    with rasterio.open(ref_tiff) as ref:
        ref_profile = ref.profile
        ref_profile.update(compress='lzw')
        ref_profile.update(nodata=NO_DATA_VAL)
        data = ref.read(1)
        mask = np.isnan(data)
        data_arr[mask>0] = NO_DATA_VAL
        with rasterio.open(output_file_name,'w',**ref_profile) as dst:
            dst.write(data_arr,1)


###############################################################################
# Multi-step forecast function using a single-step model
###############################################################################
def multi_step_forecast(model, initial_sequence, days_ahead=1):
    current_seq = np.copy(initial_sequence)
    predicted_images = []
    for _ in range(days_ahead):
        seq_expanded = np.expand_dims(current_seq, axis=0)
        step_pred = model.predict(seq_expanded)[0]
        if step_pred.ndim == 3 and step_pred.shape[-1] > 1:
            step_pred = step_pred[..., 0:1]
        predicted_images.append(step_pred)
        current_seq = np.concatenate([current_seq[1:], np.expand_dims(step_pred, axis=0)], axis=0)
    return predicted_images

###############################################################################
# Multi-step forecasting based on target date
###############################################################################
def dynamic_tif_fire_risk_prediction_by_date(county,lead0_date_str,days_ahead):
    """
    Forecasts for several days based on a target date; loads images with NaN mask,
    then for each forecast day the corresponding ground truth is loaded, compared with the prediction,
    and metrics are calculated.
    """
    pred_dir = os.path.join(DEP_DIR,"predictors/",county)
    date_obj = np.datetime64(lead0_date_str)
    print("pred_dir",pred_dir) #diagnostic
    #Identify sequential input files
    selected_files = [os.path.join(pred_dir,"_".join(("Probability",county,"lag"+str(i)))+".tif") for i in range(N_SEQ) if exists(os.path.join(pred_dir,"_".join(("Probability",county,"lag"+str(i))))+".tif")]
    selected_files = list(reversed(selected_files))
    print("selected_files",selected_files) #diagnostic 
    seq_length = len(selected_files)
    print("seq_length",seq_length) #diagnostic
    if (seq_length<2)|(seq_length>4):
        print("Incorrect number of input files")
        return
    #load the model of appropriate domain and seq_length
    model_path = os.path.join(DEP_DIR,"models/","_".join(("best_model_with_attention",county,str(seq_length)+"seq"))+".keras")
    print("model_path",model_path) #diagnostic
    model = load_model(model_path)

    sequence = []
    for file in selected_files:
        with rasterio.open(file) as src:
            arr = src.read(1)
            mask = np.isnan(arr)
            arr = np.nan_to_num(arr, nan=0)
            arr = np.expand_dims(arr, axis=-1)
            #mask = np.expand_dims(mask, axis=-1) #why the hell do you waste a line doing this if mask gets overwritten later
            sequence.append(arr)
    seq_arrays = np.array(sequence)
    print("seq_arrays",seq_arrays.shape) #diagnostic

    predicted_images = multi_step_forecast(model, seq_arrays, days_ahead=days_ahead) #the actual thing we want is in here
    return predicted_images

if __name__=="__main__":
    county = sys.argv[1]
    if len(sys.argv) < 3:
        #No custom input date specified
        hst = pytz.timezone("HST")
        today = datetime.today().astimezone(hst)
        targ_date = today - timedelta(days=1)
        std_date = targ_date.strftime('%Y-%m-%d')
    else:
        #last argument is custom input date
        std_date = sys.argv[2]
    
    ##--std_date.long_name: "standardized date"
    predictions = dynamic_tif_fire_risk_prediction_by_date(county,std_date,days_ahead=N_LEAD)
    predictions = np.squeeze(np.array(predictions))
    print("predictions from func indexed",predictions[0]) #diagnostic
    print("shaped predictions",predictions.shape) #diagnostic
    #write out using reference tif
    for pred_i in range(predictions.shape[0]):
        out_data = np.squeeze(predictions[pred_i,:,:])
        output_tiff(out_data,county,pred_i+1)
    


