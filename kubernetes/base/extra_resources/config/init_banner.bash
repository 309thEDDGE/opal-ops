cd /opt/conda/envs/singleuser/share/jupyter/labextensions/opalbanner/static \
&& sed -i "s:OPAL_BANNER_TEXT:$1:g" lib_index_js.c5bdfaa1aff4b7b02e37.js \
&& sed -i "s:OPAL_BANNER_TEXT:$1:g" lib_index_js.c5bdfaa1aff4b7b02e37.js.map \
&& sed -i "s:OPAL_BANNER_COLOR:$2:g" style_index_js.57d21bebc1950465c344.js \
&& sed -i "s:OPAL_BANNER_COLOR:$2:g" style_index_js.57d21bebc1950465c344.js.map
