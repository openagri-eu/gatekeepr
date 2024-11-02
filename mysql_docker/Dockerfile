FROM mysql:8.0

# Add a database
ENV DB_NAME=gatekeeper
ENV DB_PASS=asdasdasd

COPY ./sql_scripts/ /docker-entrypoint-initdb.d/
