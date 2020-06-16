# hetzner-auction-hunter
checks for newest servers on Hetzner server auction (server-bidding) and pushes them via telegram_send

https://www.hetzner.com/sb

## requirements
* python3
* properly configured [telegram_send](https://pypi.org/project/telegram-send/#installation)
* some witable file to store processed offers (defaulted to /tmp/hah.txt)

## usage
```
usage: hah.py [-h] --price PRICE --disk-size DISK_SIZE [--disk-quick] --cpu-score CPU_SCORE --ram RAM [--ecc] [-f [F]]

hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes them viatelegram_send

optional arguments:
  -h, --help            show this help message and exit
  --price PRICE         max price (€)
  --disk-size DISK_SIZE
                        min disk capacity (GB)
  --disk-quick          require SSD/NVMe
  --cpu-score CPU_SCORE
                        min CPU benchmark score
  --ram RAM             min RAM (GB)
  --ecc                 require ECC memory
  -f [F]                state file
  --test-mode           do not send actual messages and ignore state file
```

Example: `./hah.py --price 51 --disk-size 3000 --ram 24 --cpu-score 10000` - this will get servers cheaper than 51 EUR with more than 24GB of RAM, disks at least 3TB and CPU with score better tan 10k.

You'll probably want to put it in crontab.
