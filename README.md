# hetzner-auction-hunter

**unofficially** checks for newest servers on Hetzner server auction (server-bidding) and pushes them via [telegram_send](https://github.com/rahiel/telegram-send)

https://www.hetzner.com/sb

## requirements

* python3
* properly configured [telegram_send](https://pypi.org/project/telegram-send/#installation)
* some writable file to store processed offers (defaults to `/tmp/hah.txt`)

## usage
```
usage: hah.py [-h] [--tax TAX] [--price PRICE] [--disk-count DISK_COUNT] [--disk-size DISK_SIZE] [--disk-quick] [--hw-raid] [--red-psu]
              [--gpu] [--ipv4] [--inic] [--cpu-count CPU_COUNT] [--ram RAM] [--ecc] [--dc DC] [-f [F]] [--exclude-tax] [--test-mode]
              [--tgm-config TGM_CONFIG] [--debug] [--send-payload]

hah.py -- unofficially checks for newest servers on Hetzner server auction (server-bidding) and pushes them via telegram_send

options:
  -h, --help            show this help message and exit
  --tax TAX             tax rate (VAT) in percents, defaults to 19 (Germany)
  --price PRICE         max price (€)
  --disk-count DISK_COUNT
                        min disk count
  --disk-size DISK_SIZE
                        min disk capacity (GB)
  --disk-quick          require SSD/NVMe
  --hw-raid             require Hardware RAID
  --red-psu             require Redundant PSU
  --gpu                 require discrete GPU
  --ipv4                require IPv4
  --inic                require Intel NIC
  --cpu-count CPU_COUNT
                        min CPU count
  --ram RAM             min RAM (GB)
  --ecc                 require ECC memory
  --dc DC               datacenter (FSN1-DC15) or location (FSN)
  -f [F]                state file
  --exclude-tax         exclude tax from output price
  --test-mode           do not send actual messages and ignore state file
  --tgm-config TGM_CONFIG
                        file path to custom telegram configuration
  --debug               debug mode
  --send-payload        send server data as JSON payload
```

### directly on machine

To get servers cheaper than 100 EUR with more than 24GB of RAM, disks at least 3TB:

```bash
python3 -m venv .
source ./bin/activate
python3 -m pip install -r requirements.txt

./hah.py --price 38 --disk-size 3000 --ram 24
```

You'll probably want to put it in crontab.

### docker

![Docker Pulls](https://img.shields.io/docker/pulls/danielskowronski/hetzner-auction-hunter)

Run in test mode or change path `"${HOME}/Library/Application Support/telegram-send.conf"` to where your local telegram-send installed config. 

```bash
docker build . -t hetzner-auction-hunter:latest

docker run --rm \
  -v "${HOME}/Library/Application Support/telegram-send.conf":/etc/telegram-send.conf \
  -v /tmp/hah:/tmp/ \
  hetzner-auction-hunter:latest --price 38 --disk-size 3000 --ram 24
```

`telegram-send` does not support ENV variables as source of token or chat ID.

## debugging

```bash
curl https://www.hetzner.com/_resources/app/jsondata/live_data_sb.json | jq > live_data_sb.json
```
