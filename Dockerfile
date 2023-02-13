FROM python:3.10-slim-buster

LABEL desc="hetzner-auction-hunter"
LABEL website="https://github.com/danielskowronski/hetzner-auction-hunter"

COPY requirements.txt /requirements.txt
RUN python3 -m pip install --no-cache-dir -r /requirements.txt

COPY hah.py /hah.py

ENTRYPOINT [ "./hah.py", "--tgm-config", "/etc/telegram-send.conf"]
