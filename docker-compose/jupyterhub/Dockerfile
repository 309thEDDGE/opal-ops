ARG JUPYTERHUB_IMAGE

FROM $JUPYTERHUB_IMAGE as deploytime_jupyterhub

ARG OPAL_BANNER_COLOR
ARG OPAL_BANNER_TEXT

COPY --chown=jovyan:jovyan ./customize/page.html /opt/conda/envs/jupyterhub/share/jupyterhub/templates/page.html
COPY --chown=jovyan:jovyan ./customize/jupyterhub-80.png /opt/conda/envs/jupyterhub/share/jupyterhub/static/images/jupyterhub-80.png
COPY --chown=jovyan:jovyan ./customize/favicon.ico /opt/conda/envs/jupyterhub/share/jupyterhub/static/favicon.ico

RUN sed -i "s:OPAL_BANNER_COLOR:$OPAL_BANNER_COLOR:g" /opt/conda/envs/jupyterhub/share/jupyterhub/templates/page.html
RUN sed -i "s:OPAL_BANNER_TEXT:$OPAL_BANNER_TEXT:g" /opt/conda/envs/jupyterhub/share/jupyterhub/templates/page.html

USER root
