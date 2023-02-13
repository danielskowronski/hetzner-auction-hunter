# tests

## manual "test suite"

```bash
# https://www.hetzner.com/sb?country=ot&price_to=32
./hah.py --exclude-tax --test-mode --send-payload --price 32

# https://www.hetzner.com/sb?country=ot&drives_count_from=12
./hah.py --exclude-tax --test-mode --send-payload --disk-count 12

# https://www.hetzner.com/sb?country=ot&drives_size_from=16000&drives_size_to=16000
./hah.py --exclude-tax --test-mode --send-payload --disk-size 16000

# https://www.hetzner.com/sb?country=ot&price_to=32&driveType=sata%2Bnvme
./hah.py --exclude-tax --test-mode --send-payload --disk-quick --price 32

# https://www.hetzner.com/sb?country=ot&price_to=38&additional=HWR
./hah.py --exclude-tax --test-mode --send-payload --hw-raid --price 38

# https://www.hetzner.com/sb?country=ot&additional=RPS
./hah.py --exclude-tax --test-mode --send-payload --red-psu

# https://www.hetzner.com/sb?country=ot&additional=GPU
./hah.py --exclude-tax --test-mode --send-payload --gpu

# https://www.hetzner.com/sb?country=ot&price_to=32&additional=iNIC
./hah.py --exclude-tax --test-mode --send-payload --inic --price 32

# https://www.hetzner.com/sb?country=ot&price_to=70&ram_from=250
./hah.py --exclude-tax --test-mode --send-payload --ram 250 --price 70

# https://www.hetzner.com/sb?country=ot&price_to=38&ecc=true
./hah.py --exclude-tax --test-mode --send-payload --ecc --price 38

# https://www.hetzner.com/sb?country=ot&price_to=38&location=FSN1-DC1
./hah.py --exclude-tax --test-mode --send-payload --dc FSN1-DC1 --price 38

# https://www.hetzner.com/sb?country=ot&price_to=38&location=FSN
./hah.py --exclude-tax --test-mode --send-payload --dc FSN --price 38
```
