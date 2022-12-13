ARG SINGLE_USER_TIP_IMAGE
ARG IB_PYTORCH_IMAGE
FROM $IB_PYTORCH_IMAGE AS pytorch
FROM $SINGLE_USER_TIP_IMAGE as deploytime_singleuser
COPY --chown=jovyan:jovyan --from=pytorch /home/jovyan/local-channel /home/jovyan/pytorch_channel

# Sed replaces the "  - ./local-channel" entry in the conda env file and replaces it with the three local channels: tip_channel, tip_deps_channel, and local-channel
# RUN sed '/local-channel/s/.*/  - .\/pytorch_channel\n/' /home/jovyan/pytorch_channel/local_channel_env.yaml > /home/jovyan/pytorch_env.yaml \
#     && printf "\n  - pip:" >> /home/jovyan/pytorch_env.yaml \
#     && printf "\n    - /opt/data/opal/opal-packages/kinds" >> /home/jovyan/pytorch_env.yaml \
#     && printf "\n    - /opt/data/opal/opal-packages/search" >> /home/jovyan/pytorch_env.yaml \
#     && printf "\n    - /opt/data/opal/opal-packages/core" >> /home/jovyan/pytorch_env.yaml \
#     && conda env create -f /home/jovyan/pytorch_env.yaml --offline \
#     && rm -rf /home/jovyan/pytorch_channel

RUN sed '/local-channel/s/.*/  - .\/pytorch_channel\n/' /home/jovyan/pytorch_channel/local_channel_env.yaml > /home/jovyan/pytorch_env.yaml \
    && conda env create -f /home/jovyan/pytorch_env.yaml --offline \
    && rm -rf /home/jovyan/pytorch_channel


# ARG OPAL_BANNER_COLOR
# ARG OPAL_BANNER_TEXT


# RUN cd /opt/data/opal/devops-software/opalbanner/opalbanner/labextension/static/ \
#     && sed -i "s:OPAL_BANNER_TEXT:$OPAL_BANNER_TEXT:g" lib_index_js.c5bdfaa1aff4b7b02e37.js \
#     && sed -i "s:OPAL_BANNER_TEXT:$OPAL_BANNER_TEXT:g" lib_index_js.c5bdfaa1aff4b7b02e37.js.map \
#     && sed -i "s:OPAL_BANNER_COLOR:$OPAL_BANNER_COLOR:g" style_index_js.57d21bebc1950465c344.js \
#     && sed -i "s:OPAL_BANNER_COLOR:$OPAL_BANNER_COLOR:g" style_index_js.57d21bebc1950465c344.js.map

# RUN source /opt/conda/bin/activate \
#     && conda activate singleuser \
#     && cd /opt/data/opal/devops-software/opalbanner \
#     && pip install .
