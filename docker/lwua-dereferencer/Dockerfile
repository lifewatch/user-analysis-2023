FROM python:3.11-slim as python
VOLUME /data
VOLUME /logging
WORKDIR /dereferencer-py
ENV PYTHONUNBUFFERED=true

# check for inspiration on including poetry 
#  - https://hub.docker.com/r/airdock/python-poetry
#  - https://binx.io/nl/2022/06/13/poetry-docker/


# create an image version point where poetry and its dependencies are available
# and use that to build the python package locally
FROM python as poetry
# gcc needed in the build of many python dependencies 
# removed from python-slim for size trimming - but have to re-add here
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y gcc
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -

# get the source code in
COPY ./dereferencer-py /dereferencer-py
# use poetry to build and install -- creating the local .venv
RUN poetry install --no-interaction --no-ansi -vvv


# now go back to the original slim image to build the runtime image
# and just grab the build env from the intermediate stage
FROM python as runtime
# ensure the .venv python is used
ENV PATH="/dereferencer-py/.venv/bin:$PATH" 
# ensure we have the build folder from the poetry stage of this image
COPY --from=poetry /dereferencer-py /dereferencer-py

RUN rm -f /dereferencer-py/logging && ln -s /logging /dereferencer-py/logging
ENTRYPOINT ["python", "-m", "dereferencer"]