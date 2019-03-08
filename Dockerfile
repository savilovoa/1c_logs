FROM python:3
MAINTAINER savilovoa@gmail.com

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV L_DATA=/var/lib/1c_logs/data \
    L_SINCE=/var/lib/1c_logs/since \
    L_LOG=/var/log/1c_logs \
    L_ETC=/usr/local/etc/1c_logs \
    L_WORKDIR=/usr/lib/1c_logs

COPY app/lib/ ${L_WORKDIR}/
COPY app/etc/ ${L_ETC}/
COPY app/since/ ${L_SINCE}/

RUN mkdir -p ${L_DATA} \
  && mkdir -p ${L_LOG}

WORKDIR ${L_WORKDIR}

VOLUME ["${L_DATA}", "${L_SINCE}", "${L_ETC}", "${L_LOG}"]

CMD python ./send2elastic.py
