# Tests

## Manual "Test Suite"

These tests can be run manually to validate that the various command-line options are functioning correctly.

### General Tests

```bash
# Test filtering by maximum price
./hah.py --exclude-tax --test-mode --send-payload --price 32

# Test filtering by minimum disk count
./hah.py --exclude-tax --test-mode --send-payload --disk-count 12

# Test filtering by exact disk size
./hah.py --exclude-tax --test-mode --send-payload --disk-size 16000

# Test filtering by quick disks (SSD/NVMe) and price
./hah.py --exclude-tax --test-mode --send-payload --disk-quick --price 32

# Test filtering by hardware RAID and price
./hah.py --exclude-tax --test-mode --send-payload --hw-raid --price 38

# Test filtering by redundant PSU
./hah.py --exclude-tax --test-mode --send-payload --red-psu

# Test filtering by discrete GPU
./hah.py --exclude-tax --test-mode --send-payload --gpu

# Test filtering by Intel NIC and price
./hah.py --exclude-tax --test-mode --send-payload --inic --price 32

# Test filtering by RAM size and price
./hah.py --exclude-tax --test-mode --send-payload --ram 250 --price 70

# Test filtering by ECC memory and price
./hah.py --exclude-tax --test-mode --send-payload --ecc --price 38

# Test filtering by specific datacenter (FSN1-DC1) and price
./hah.py --exclude-tax --test-mode --send-payload --dc FSN1-DC1 --price 38

# Test filtering by location (FSN) and price
./hah.py --exclude-tax --test-mode --send-payload --dc FSN --price 38
```

### New Feature: CPU Model Filtering

```bash
# Test filtering by specific CPU model (e.g., Ryzen 9 3900)
./hah.py --exclude-tax --test-mode --send-payload --cpu-model "Ryzen 9 3900"

# Test filtering by Intel Xeon CPU model
./hah.py --exclude-tax --test-mode --send-payload --cpu-model "Xeon"
```

These tests cover the various options available in the `hah.py` script and should help ensure that the script behaves as expected across a variety of scenarios.
