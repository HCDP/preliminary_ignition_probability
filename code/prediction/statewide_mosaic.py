import os
import subprocess

MASTER_DIR = os.environ.get("PROJECT_ROOT")
OUTPUT_DIR = MASTER_DIR + "data_outputs/prediction/tiff/"
N_LEAD = int(os.environ.get("LEAD"))

def statewide_mosaic(lead):
    icode_list = ['bi','ka','mn','oa']
    file_names = [OUTPUT_DIR+"_".join(("Probability",icode,"lead"+"{:02d}".format(lead)))+'.tif' for icode in icode_list]
    output_name = OUTPUT_DIR + 'Probability_statewide_'+"lead"+"{:02d}".format(lead) + '.tif'
    cmd = "gdal_merge.py -o "+output_name+" -of gtiff -co COMPRESS=LZW -init -9999 -a_nodata -9999"
    return subprocess.run(cmd.split()+file_names).returncode

#should run date agnostic. Will automatically mosaic the existing county files in the container
if __name__=="__main__":
    for lead in range(N_LEAD):
        rtn = statewide_mosaic(lead+1)
        if rtn == 0:
            print("Mosaic completed for lead",lead+1)
        else:
            print(f"Mosaic failed for lead {lead+1}. Check files.")