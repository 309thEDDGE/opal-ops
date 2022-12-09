ARG SINGLE_USER_TIP_IMAGE
FROM $SINGLE_USER_TIP_IMAGE as deploytime_singleuser

ARG OPAL_BANNER_COLOR
ARG OPAL_BANNER_TEXT


#RUN cd /opt/data/opal/devops-software/opalbanner/opalbanner/labextension/static/ \
    #&& sed -i "s:OPAL_BANNER_TEXT:$OPAL_BANNER_TEXT:g" lib_index_js.c5bdfaa1aff4b7b02e37.js \
    #&& sed -i "s:OPAL_BANNER_TEXT:$OPAL_BANNER_TEXT:g" lib_index_js.c5bdfaa1aff4b7b02e37.js.map \
    #&& sed -i "s:OPAL_BANNER_COLOR:$OPAL_BANNER_COLOR:g" style_index_js.57d21bebc1950465c344.js \
    #&& sed -i "s:OPAL_BANNER_COLOR:$OPAL_BANNER_COLOR:g" style_index_js.57d21bebc1950465c344.js.map

#RUN source /opt/conda/bin/activate \
    #&& conda activate singleuser \
    #&& cd /opt/data/opal/devops-software/opalbanner \
    #&& pip install .
