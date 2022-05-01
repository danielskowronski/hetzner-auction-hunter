FROM python:3.8-slim-buster

RUN python -m pip install httpx[http2]
RUN python -m pip install telegram_send

ADD hah.py hah.py
ADD telegram-send.conf /etc/telegram-send.conf

ENTRYPOINT [ "./hah.py", "--tgm-config", "/etc/telegram-send.conf"]