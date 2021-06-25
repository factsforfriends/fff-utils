FROM pypy:3.7-buster
LABEL maintainer="Jens Preussner <jens@factsforfriends.de>"

COPY . /usr/src/fff-utils

RUN \
    cd /usr/src/fff-utils && \
    pip install -r requirements.txt && \
    pypy setup.py install

CMD ["fff-utils"]