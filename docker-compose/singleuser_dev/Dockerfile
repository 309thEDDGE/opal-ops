ARG SINGLE_USER_TIP_IMAGE
FROM $SINGLE_USER_TIP_IMAGE as base_singleuser

COPY --chown=jovyan:jovyan opal /opt/data/opal


RUN sed '/local-channel/s/.*/ - .\/local-channel/' /home/jovyan/local-channel/local_channel_env.yaml > /home/jovyan/singleuser_env.yaml \
    && printf "\n  - pip:" >> /home/jovyan/singleuser_env.yaml \
    && printf "\n    - /opt/data/opal/opal-packages" >> /home/jovyan/singleuser_env.yaml \
    && conda env create -f /home/jovyan/singleuser_env.yaml --offline \
    && rm -rf /home/jovyan/tip_deps_channel /home/jovyan/local-channel /home/jovyan/conf /home/jovyan/tip_channel /home/jovyan/tip_scripts
