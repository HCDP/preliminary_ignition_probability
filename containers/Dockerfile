#SET UP FROM PRODUCTION BASE IMAGE
FROM ghcr.io/hcdp/task-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_ignition_probability"
LABEL org.opencontainers.image.description="Base Image for preliminary ignition probability workflows."

## PACKAGE/LIBRARY INSTALLATIONS ##
# Fetch the latest apt repo information.
RUN apt update
# Let APT know that we don't have a terminal.
ENV DEBIAN_FRONTEND=noninteractive

# Upgrade pip **Might not be necessary for this build
RUN pip install --upgrade pip

# Install libgdal
# Check version
RUN apt-get install -y libgdal-dev

# Time zone package
RUN apt-get install -y tzdata

#Install ignition probability python dependencies
RUN python3 -m pip install numpy
RUN python3 -m pip install scipy
RUN python3 -m pip install gdal==$(gdal-config --version)
RUN python3 -m pip install rasterio
RUN python3 -m pip install matplotlib
RUN python3 -m pip install pandas
RUN python3 -m pip install scikit-learn
RUN python3 -m pip install tiffile
RUN python3 -m pip install python-dotenv
RUN python3 -m pip install pathlib

RUN mkdir -p /workspace/code
RUN mkdir -p /workspace/dependencies
RUN mkdir -p /workspace/envs
RUN mkdir -p /sync

RUN wget https://raw.githubusercontent.com/ikewai/data-uploader/main/upload.py -O /sync/upload.py

ADD /tools /sync