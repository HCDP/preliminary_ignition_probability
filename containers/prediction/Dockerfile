FROM ghcr.io/hcdp/task-preliminary-ignition-probability-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_ignition_probability"
LABEL org.opencontainers.image.description="Future preliminary ignition probability."

ADD /envs/prediction/prod.env /workspace/envs
ADD /code/prediction /workspace/code

WORKDIR /code/prediction/dependencies/models
RUN wget -nv https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/workflow_data/preliminary/ignition_prob/dependencies/prediction_dependencies.tar.gz
RUN tar -xf prediction_dependencies.tar.gz
RUN rm prediction_dependencies.tar.gz

# Get the container's upload config as specified in the code repo.
ADD /containers/prediction/configs/upload.json /sync/config.json
# Add the task wrapper script.
ADD /containers/prediction/task.sh /workspace/task.sh

WORKDIR /workspace
# This container is intended to run the task wrapper at launch, unless otherwise specified at run-time.
CMD [ "/bin/bash", "task.sh" ]
