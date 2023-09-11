#!/bin/bash -ex

GDBPIDF="/tmp/init-graphdb-serv.pid"
GDBOUTF="/tmp/init-graphdb-out.txt"

start_graphdb(){
    rm -f ${GDBPIDF}
    graphdb -s -p ${GDBPIDF} >${GDBOUTF} 2>&1 &
    sleep 1
}

wait_graphdb(){
    count=0
    while ! nc -z localhost 7200; do   
        count=$((count+1))
        if [ $count -gt 1000 ]; then
            return
        fi
        # else 
        sleep 0.1 # wait for 1/10 of the second before check again
    done
}

stop_graphdb(){
    kill -9 $(cat ${GDBPIDF})
    sleep 1
    rm -f ${GDBPIDF}
    rm -f ${GDBOUTF}
}

createdb() {
    curl -X POST http://localhost:7200/rest/repositories -H 'Content-Type: multipart/form-data' -F config=@lwua23-repo.ttl
}


# one could do it like this 
#start_graphdb
#wait_graphdb
#createdb
#wait_configdb
#stop_graphdb

# but actually this just works too:
REPODIR="/opt/graphdb/home/data/repositories/lwua23"
mkdir -p ${REPODIR}
cp ./lwua23-repo.ttl ${REPODIR}/config.ttl
