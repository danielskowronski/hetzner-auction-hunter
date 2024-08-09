# hetzner-auction-hunter

**unofficially** checks for newest servers on Hetzner server auction (server-bidding) and pushes to one of dozen providers supported by [Notifiers library](https://pypi.org/project/notifiers/), including Pushover, SimplePush, Slack, Gmail, Email (SMTP), Telegram, Gitter, Pushbullet, Join, Zulip, Twilio, Pagerduty, Mailgun, PopcornNotify, StatusPage.io, iCloud, VictorOps (Splunk).

This repository is a fork of the original [Hetzner Auction Hunter](https://github.com/danielskowronski/hetzner-auction-hunter), with additional features and improvements.

[Hetzner Auction website](https://www.hetzner.com/sb)

[![Docker Pulls](https://img.shields.io/docker/pulls/danielskowronski/hetzner-auction-hunter)](https://hub.docker.com/repository/docker/danielskowronski/hetzner-auction-hunter)

The price displayed on hetzner.com by default includes the monthly rate for an IPv4 address, therefore it's slightly higher than one reported by this tool. You can disable it by toggling the *Enable IPv6 only* switch available on top of the list (on hetzner.com). 

## New Features in This Fork

- **CPU Model Filtering**: Added a new `--cpu-model` argument to filter servers based on specific CPU models (e.g., "Ryzen 9 3900").
- **Enhanced Server Configuration Output**: Improved the display of server configuration details in the console, including CPU, RAM, and disk information.
- **Bug Fixes and Code Improvements**: Fixed bugs related to argument parsing and updated the code structure for better maintainability.

## Requirements

- Python 3
- Properly configured [Notifiers provider](https://notifiers.readthedocs.io/en/latest/providers/index.html)
- Some writable file to store processed offers (defaults to `/tmp/hah.txt`)

## Usage

```plaintext
usage: hah.py [-h] [--data-url DATA_URL] [--provider PROVIDER] [--tax TAX] [--price PRICE] [--disk-count DISK_COUNT] [--disk-size DISK_SIZE] [--disk-min-size DISK_MIN_SIZE] [--disk-quick] [--hw-raid] [--red-psu] [--gpu] [--ipv4] [--inic]
              [--cpu-count CPU_COUNT] [--ram RAM] [--ecc] [--dc DC] [--cpu-model CPU_MODEL] [-f [F]] [--exclude-tax] [--test-mode] [--debug] [--send-payload]

hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes to one of dozen providers supported by Notifiers library

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
  --disk-min-size DISK_MIN_SIZE
                        min disk capacity per disk (GB)
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
  --cpu-model CPU_MODEL
                        filter by CPU model (e.g., "Ryzen 9 3900")
  -f [F]                state file
  --exclude-tax         exclude tax from output price
  --test-mode           do not send actual messages and ignore state file
  --debug               debug mode
  --send-payload        send server data as JSON payload
```

Since there are way too many combinations of providers and their parameters to support as CLI args, you must pass `--provider PROVIDER` as defined on [Notifiers providers list](https://notifiers.readthedocs.io/en/latest/providers/index.html) and export all relevant ENV variables as per [Notifiers usage guide](https://notifiers.readthedocs.io/en/latest/usage.html?highlight=NOTIFIERS_#environment-variables). 

### Directly on Machine

You'll probably want to put it in crontab and make sure that the state file is on permanent storage (`/tmp/` may or may not survive reboot).

#### Prepare Local Environment

```bash
pyenv activate
python3 -m pip install -r requirements.txt
```

#### Export ENV Variables

Those are just examples. Check out https://notifiers.readthedocs.io/en/latest/providers/index.html

For **Pushover**: [register](https://pushover.net/signup), get your User Key from [main page](https://pushover.net) and then [register app](https://pushover.net/apps/build) for which you'll get an app token. Then export as follows:

```bash
export NOTIFIERS_PUSHOVER_USER=...
export NOTIFIERS_PUSHOVER_TOKEN=...
export HAH_PROVIDER=pushover
```

For **Gmail**: register, [enable 2FA](https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome) (required because Google enforces app passwords for non-OAuth clients and you can't have an app password without 2FA), [create an app password](https://myaccount.google.com/apppasswords) selecting Mail as service. Then export as follows:

```bash
export NOTIFIERS_GMAIL_USERNAME="...@gmail.com" # username
export NOTIFIERS_GMAIL_PASSWORD="..." # app password
export NOTIFIERS_GMAIL_FROM="$NOTIFIERS_GMAIL_USERNAME <$NOTIFIERS_GMAIL_USERNAME>" # optional From field, recommended to use real account email
export NOTIFIERS_GMAIL_TO="..." # recipient
export HAH_PROVIDER=gmail
```

For **Telegram** (discouraged, but provided for legacy compatibility): talk to [@BotFather](https://t.me/BotFather) to create a new bot and obtain a token, talk to [@myidbot](https://t.me/myidbot) to get your personal chat ID. Then export as follows: 

```bash
export NOTIFIERS_TELEGRAM_TOKEN="...:..."
export NOTIFIERS_TELEGRAM_CHAT_ID="..." 
export HAH_PROVIDER=telegram
```

#### Run

To get servers cheaper than 38 EUR with more than 24GB of RAM and disks at least 3TB:

```bash
./hah.py --provider $HAH_PROVIDER --price 38 --disk-size 3000 --ram 24
```

To find servers with a specific CPU model (e.g., "Ryzen 9 3900"):

```bash
./hah.py --provider $HAH_PROVIDER --cpu-model "Ryzen 9 3900"
```

### Docker

Example run for Pushover:

```bash
docker build . -t hetzner-auction-hunter:latest --no-cache=true

docker run --rm \
  -v /tmp/hah:/tmp/ \
  -e NOTIFIERS_PUSHOVER_USER=$NOTIFIERS_PUSHOVER_USER \
  -e NOTIFIERS_PUSHOVER_TOKEN=$NOTIFIERS_PUSHOVER_TOKEN \
  hetzner-auction-hunter:latest --provider $HAH_PROVIDER --price 40 --disk-size 3000 --ram 24
```

For more universal executions, you may consider using `docker run --env-file`.

## Debugging

```bash
curl https://www.hetzner.com/_resources/app/jsondata/live_data_sb.json | jq > live_data_sb.json
./hah.py --data-url "file:///${PWD}/live_data_sb.json" --debug ...
```

## Docker Image for hub.docker.com

```bash
hadolint Dockerfile
export TAG=ikdanyt/hetzner-auction-hunter:v...
docker build . -t $TAG --no-cache=true
docker push $TAG
```

---

This fork is maintained by [IkdanYT](https://github.com/IkdanYT/hetzner-auction-hunter).
