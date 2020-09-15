FROM python:3.8-alpine

RUN apk --no-cache add dnsmasq && pip install requests

WORKDIR /app
COPY unifi.py ./
COPY run.sh ./

EXPOSE 53 53/udp
CMD ["./run.sh"]