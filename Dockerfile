FROM mcr.microsoft.com/aiforearth/base-py:1.5


# RUN conda config --append channels oggm
RUN conda config --add channels conda-forge
RUN conda config --set channel_priority strict

# Example of installing additonal Anaconda packages - numpy and pandas
RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
	&& conda install -n ai4e_py_api numpy pandas statsmodels scikit-learn==0.19.1 netCDF4 xarray matplotlib rasterio shapely affine

RUN pip install geopandas

# Copy custom module
COPY ./models /app/my_api/models
COPY ./gppd_ai4earth /app/my_api/gppd_ai4earth
# Copy API code
COPY ./my_api /app/my_api/
COPY ./supervisord.conf /etc/supervisord.conf

# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    TRACE_SAMPLING_RATE=1.0

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_Test \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=base-py\ example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 \
    ENVSERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/my_api/tasker

# Expose the port that is to be used when calling your API
EXPOSE 1212
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost:1212/${API_PREFIX}/ || exit 1
ENTRYPOINT [ "/startup.sh" ]
