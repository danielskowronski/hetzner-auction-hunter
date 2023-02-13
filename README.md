# hetzner-auction-hunter

**unofficially** checks for newest servers on Hetzner server auction (server-bidding) and pushes to one of dozen providers supported by [Notifiers library](https://pypi.org/project/notifiers/), including Pushover, SimplePush, Slack, Gmail, Email (SMTP), Telegram, Gitter, Pushbullet, Join, Zulip, Twilio, Pagerduty, Mailgun, PopcornNotify, StatusPage.io, iCloud, VictorOps (Splunk)

[Hetzner Auction website](https://www.hetzner.com/sb)

[![Docker Pulls](https://img.shields.io/docker/pulls/danielskowronski/hetzner-auction-hunter)](https://hub.docker.com/repository/docker/danielskowronski/hetzner-auction-hunter)

## requirements

* python3
* properly configured [Notifiers provider](https://notifiers.readthedocs.io/en/latest/providers/index.html)
* some writable file to store processed offers (defaults to `/tmp/hah.txt`)

## usage

```
usage: hah.py [-h] [--data-url DATA_URL] --provider PROVIDER [--tax TAX] [--price PRICE] [--disk-count DISK_COUNT] [--disk-size DISK_SIZE]
              [--disk-quick] [--hw-raid] [--red-psu] [--gpu] [--ipv4] [--inic] [--cpu-count CPU_COUNT] [--ram RAM] [--ecc] [--dc DC]
              [-f [F]] [--exclude-tax] [--test-mode] [--debug] [--send-payload]

hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes to one of dozen providers supported by Notifiers
library

options:
  -h, --help            show this help message and exit
  --data-url DATA_URL   URL to live_data_sb.json
  --provider PROVIDER   Notifiers provider name - see https://notifiers.readthedocs.io/en/latest/providers/index.html
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
  --debug               debug mode
  --send-payload        send server data as JSON payload
```

Since there are way too many combinations of providers and their parameters to support as CLI args, you must pass `--provider PROVIDER` as defined on [Notifiers providers list](https://notifiers.readthedocs.io/en/latest/providers/index.html) and export all relevant ENV variables as per [Notifiers usage guide](https://notifiers.readthedocs.io/en/latest/usage.html?highlight=NOTIFIERS_#environment-variables). 

### directly on machine

You'll probably want to put it in crontab and make sure that state file is on permanent storage (`/tmp/` may or may not survive reboot).

#### prepare local env

```bash
python3 -m venv .
source ./bin/activate
python3 -m pip install -r requirements.txt
```

#### export ENV variables

Those are just examples. Check out https://notifiers.readthedocs.io/en/latest/providers/index.html

For **Pushover**: [register](https://pushover.net/signup), get your User Key from [main page](https://pushover.net) and then [register app](https://pushover.net/apps/build) for which you'll get app token. Then export as follows:

```bash
export NOTIFIERS_PUSHOVER_USER=...
export NOTIFIERS_PUSHOVER_TOKEN=...
export HAH_PROVIDER=pushover
```

For **Gmail**: register, [enable 2FA](https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome) (required bacuse Google enforces app passwords for non-OAuth clients and you can't have app password without 2FA), [create app password](https://myaccount.google.com/apppasswords) selecting Mail as service. Then export as follows:

```bash
export NOTIFIERS_GMAIL_USERNAME="...@gmail.com" # username
export NOTIFIERS_GMAIL_PASSWORD="..." # app password
export NOTIFIERS_GMAIL_FROM="$NOTIFIERS_GMAIL_USERNAME <$NOTIFIERS_GMAIL_USERNAME>" # optional From field, recommended to use real account email
export NOTIFIERS_GMAIL_TO="..." # recipient
export HAH_PROVIDER=gmail
```

#### run

To get servers cheaper than 38 EUR with more than 24GB of RAM, disks at least 3TB:

```bash
./hah.py --provider $HAH_PROVIDER --price 38 --disk-size 3000 --ram 24
```

### docker

Run in test mode or change path `"${HOME}/Library/Application Support/telegram-send.conf"` to where your local telegram-send installed config. 

```bash
docker build . -t hetzner-auction-hunter:latest --no-cache=true

docker run --rm \
  -v /tmp/hah:/tmp/ \
  -e NOTIFIERS_PUSHOVER_USER=$NOTIFIERS_PUSHOVER_USER \
  -e NOTIFIERS_PUSHOVER_TOKEN=$NOTIFIERS_PUSHOVER_TOKEN \
  hetzner-auction-hunter:latest --provider $HAH_PROVIDER --price 38 --disk-size 3000 --ram 24
```

For more universal executions you may consider using `docker run --env-file`.

## debugging

```bash
curl https://www.hetzner.com/_resources/app/jsondata/live_data_sb.json | jq > live_data_sb.json
./hah --data-url "file:///${PWD}/live_data_sb.json" --debug ...
```

## docker image for hub.docker.com

```bash
hadolint Dockerfile
export TAG=danielskowronski/hetzner-auction-hunter:v2.0.0-alpha1
docker build . -t $TAG --no-cache=true
docker push $TAG
```