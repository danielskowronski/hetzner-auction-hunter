FROM python:3.8-slim-buster
RUN python -m pip install httpx[http2]
RUN python -m pip install telegram_send
ADD hah.py hah.py
ADD telegram-send.conf /etc/telegram-send.conf
#RUN ./hah.py --price 200 --disk-size 10000 --disk-count 10 --ram 24 --cpu-score 10000 --test-mode --dc FSN
ENTRYPOINT [ "./hah.py"]
CMD [ "--price", "250", "--disk-size", "10000", "--disk-count", "10", "--ram", "24", "--cpu-score", "10000", "--dc", "FSN", "--tgm-config", "/etc/telegram-send.conf", "--exclude-tax"]