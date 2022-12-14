ARG SINGLE_USER_TIP_IMAGE
ARG IB_PYTORCH_IMAGE
FROM $IB_PYTORCH_IMAGE AS pytorch
FROM $SINGLE_USER_TIP_IMAGE as base_singleuser
COPY --chown=jovyan:jovyan --from=pytorch /home/jovyan/local-channel /home/jovyan/pytorch_channel
COPY --chown=jovyan:jovyan opal /opt/data/opal

# Sed replaces the "  - ./local-channel" entry in the conda env file and replaces it with the three local channels: tip_channel, tip_deps_channel, and local-channel
# local_channel in this block refers to the local conda channel as it exists within the IB singleuser image
#RUN sed '/local-channel/s/.*/ - .\/local-channel/' /home/jovyan/local-channel/local_channel_env.yaml > /home/jovyan/singleuser_env.yaml \
    #&& printf "\n  - pip:" >> /home/jovyan/singleuser_env.yaml \
    #&& printf "\n    - /opt/data/opal/opal-packages" >> /home/jovyan/singleuser_env.yaml \
    #&& conda env create -f /home/jovyan/singleuser_env.yaml --offline \
    #&& rm -rf /home/jovyan/tip_deps_channel /home/jovyan/local-channel /home/jovyan/conf /home/jovyan/tip_channel /home/jovyan/tip_scripts


RUN sed '/local-channel/s/.*/  - .\/pytorch_channel\n/' /home/jovyan/pytorch_channel/local_channel_env.yaml > /home/jovyan/pytorch_env.yaml \
    && printf "\n  - pip:" >> /home/jovyan/pytorch_env.yaml \
    && printf "\n    - /opt/data/opal/opal-packages" >> /home/jovyan/pytorch_env.yaml \
    && conda env create -f /home/jovyan/pytorch_env.yaml --offline \
    && rm -rf /home/jovyan/pytorch_channel
