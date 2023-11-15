FROM ontotext/graphdb:10.0.2

RUN mkdir -p /root/graphdb-import/data
WORKDIR /root/graphdb-import/data

COPY ./initdb /initdb
RUN cd /initdb  && sh ./init_graphdb.sh 