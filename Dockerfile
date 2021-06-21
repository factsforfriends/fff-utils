FROM pypy:3.7-buster
LABEL maintainer="Jens Preussner <jens@factsforfriends.de>"

COPY . /usr/src/fff-utils

RUN \
    apt-get update && \
    apt-get install --assume-yes cron && \
    cd /usr/src/fff-utils && \
    pip install -r requirements.txt && \
    pypy setup.py install

COPY fff-utils-cron /etc/cron.d/fff-utils-cron
RUN \
    chmod 0644 /etc/cron.d/fff-utils-cron && \
    crontab /etc/cron.d/fff-utils-cron

CMD ["cron", "-f"]