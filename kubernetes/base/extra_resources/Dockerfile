ARG SINGLE_USER_TIP_IMAGE
ARG IB_PYTORCH_IMAGE
FROM $IB_PYTORCH_IMAGE AS pytorch
FROM $SINGLE_USER_TIP_IMAGE as deploytime_singleuser
COPY --chown=jovyan:jovyan --from=pytorch /home/jovyan/local-channel /home/jovyan/pytorch_channel


RUN sed '/local-channel/s/.*/  - .\/pytorch_channel\n/' /home/jovyan/pytorch_channel/local_channel_env.yaml > /home/jovyan/pytorch_env.yaml \
    && conda env create -f /home/jovyan/pytorch_env.yaml --offline \
    && rm -rf /home/jovyan/pytorch_channel

