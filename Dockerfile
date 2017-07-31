FROM gone/python-arm

COPY .docker/service /etc/service
RUN chmod +x /etc/service/*/run
