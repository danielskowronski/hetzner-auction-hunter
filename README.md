# hetzner-auction-hunter
checks for newest servers on Hetzner server auction (server-bidding) and pushes them via telegram_send

https://www.hetzner.com/sb

## requirements
* python3
* httpx module with http2 support: `pip install httpx[http2]`
* properly configured [telegram_send](https://pypi.org/project/telegram-send/#installation)
* some writable file to store processed offers (defaults to /tmp/hah.txt)

## usage
```
usage: hah.py [-h] [--tax TAX] --price PRICE [--disk-count DISK_COUNT] --disk-size DISK_SIZE
              [--disk-quick] [--disk-ent] [--hw-raid] [--red-psu] [--cpu-count CPU_COUNT]
              --cpu-score CPU_SCORE --ram RAM [--ecc] [--dc DC] [-f [F]] [--test-mode]
              [--tgm-config TGM_CONFIG]

hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes them via telegram_send

optional arguments:
  -h, --help            show this help message and exit
  --tax TAX             tax rate (VAT) in percents, defaults to 19 (Germany)
  --price PRICE         max price (€)
  --disk-count DISK_COUNT
                        min disk count
  --disk-size DISK_SIZE
                        min disk capacity (GB)
  --disk-quick          require SSD/NVMe
  --disk-ent            require Enterprise HDD or Datacenter SSD
  --hw-raid             require Hardware RAID
  --red-psu             require Redundant PSU
  --cpu-count CPU_COUNT
                        min CPU count
  --cpu-score CPU_SCORE
                        min CPU benchmark score
  --ram RAM             min RAM (GB)
  --ecc                 require ECC memory
  --dc DC               datacenter (FSN1-DC15) or location (FSN)
  -f [F]                state file
  --test-mode           do not send actual messages and ignore state file
  --tgm-config TGM_CONFIG
                        file path to custom telegram configuration
```

Example: `./hah.py --price 51 --disk-size 3000 --ram 24 --cpu-score 10000` - this will get servers cheaper than 51 EUR with more than 24GB of RAM, disks at least 3TB and CPU with score better than 10k.

You'll probably want to put it in crontab.
