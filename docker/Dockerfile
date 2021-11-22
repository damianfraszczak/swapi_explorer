FROM python:3.8

ARG RUNNING_USER=swapi
ENV PYTHONUNBUFFERED=1
ENV NAME=swapi_explorer
ENV PYTHONPATH "/home/${RUNNING_USER}/app/:${PYTHONPATH}"
ENV PATH="/home/${RUNNING_USER}/.local/bin:${PATH}"

RUN pip install --upgrade pip

RUN adduser --quiet --disabled-password ${RUNNING_USER}
USER ${RUNNING_USER}

WORKDIR /home/${RUNNING_USER}/swapi_explorer/
COPY requirements.txt requirements.txt
RUN pip install --user -r requirements.txt
COPY swapi_explorer .
