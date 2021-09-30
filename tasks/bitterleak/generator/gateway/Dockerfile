FROM alpine

RUN apk add --no-cache iproute2 iptables bridge-utils bash \
  && apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/community tshark \
  && apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/testing mitmproxy py3-setuptools
RUN mkdir /root/output
COPY run.sh /root
WORKDIR /root/output
CMD /root/run.sh
