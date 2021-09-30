FROM alpine

RUN apk add --no-cache curl iproute2 bash bc \
  && apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/community tshark
COPY run.sh /root
CMD /root/run.sh
