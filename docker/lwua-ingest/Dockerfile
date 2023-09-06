FROM python:3.10-buster

COPY . /lwua
WORKDIR /lwua


# TODO COPY and build the lwua python module
# but rather swithch to using poetry -- mpo has pattern for making it available inside docker
#RUN python -m pip install --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt && \
#    python setup.py install

ENTRYPOINT ["./entrypoint.sh"] 
