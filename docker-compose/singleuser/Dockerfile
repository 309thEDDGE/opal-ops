ARG IB_SINGLEUSER_IMAGE

FROM $IB_SINGLEUSER_IMAGE as base_singleuser
RUN rm -rf /opt/data/opal
COPY --chown=jovyan:jovyan opal /opt/data/opal
COPY --chown=jovyan:jovyan weave /opt/data/weave
# Sed replaces the "  - ./local-channel" entry in the conda env file and replaces it with the three local channels: tip_channel, tip_deps_channel, and local-channel
# local_channel in this block refers to the local conda channel as it exists within the IB singleuser image
RUN conda search --channel file:///home/jovyan/local-channel --offline \
    && sed -i 's/name: pytorch/name: singleuser/' /home/jovyan/local-channel/local_channel_env.yaml \
    && sed '/local-channel/s/.*/ - .\/local-channel/' /home/jovyan/local-channel/local_channel_env.yaml > /home/jovyan/singleuser_env.yaml \
    && printf "\n  - pip:" >> /home/jovyan/singleuser_env.yaml \
    && printf "\n    - /opt/data/opal/opal-packages" >> /home/jovyan/singleuser_env.yaml \
    && printf "\n    - /opt/data/weave" >> /home/jovyan/singleuser_env.yaml \
    && CONDA_OVERRIDE_CUDA="12.9" conda env create -f /home/jovyan/singleuser_env.yaml --offline \
    && rm -rf /home/jovyan/tip_deps_channel /home/jovyan/local-channel /home/jovyan/conf /home/jovyan/tip_channel /home/jovyan/tip_scripts
ENV PATH="/opt/conda/envs/singleuser/bin:$PATH"

RUN source /opt/conda/bin/activate \
    && conda activate singleuser 

ENTRYPOINT ["tini", "-g", "--"]
CMD ["/usr/local/bin/start-notebook.sh"]