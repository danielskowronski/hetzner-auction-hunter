#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import httpx, json, telegram_send, argparse

parser = argparse.ArgumentParser(description='hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes them via telegram_send')
parser.add_argument('--tax',        nargs=1,required=False,type=int,help='tax rate (VAT) in percents, defaults to 19 (Germany)', default=[19])
parser.add_argument('--price',      nargs=1,required=True,type=int, help='max price (€)')
parser.add_argument('--disk-count', nargs=1,required=False,type=int,help='min disk count', default=[1])
parser.add_argument('--disk-size',  nargs=1,required=True,type=int, help='min disk capacity (GB)')
parser.add_argument('--disk-quick', action='store_true',            help='require SSD/NVMe')
parser.add_argument('--disk-ent',   action='store_true',            help='require Enterprise HDD or Datacenter SSD')
parser.add_argument('--hw-raid',    action='store_true',            help='require Hardware RAID')
parser.add_argument('--red-psu',    action='store_true',            help='require Redundant PSU')
parser.add_argument('--cpu-count',  nargs=1,required=False,type=int, help='min CPU count', default=[1])
parser.add_argument('--cpu-score',  nargs=1,required=True,type=int, help='min CPU benchmark score')
parser.add_argument('--ram',        nargs=1,required=True,type=int, help='min RAM (GB)')
parser.add_argument('--ecc',        action='store_true',            help='require ECC memory')
parser.add_argument('--dc',         nargs=1,required=False,         help='datacenter (FSN1-DC15) or location (FSN)')
parser.add_argument('-f',           nargs='?',                      help='state file')
parser.add_argument('--test-mode',  action='store_true',            help='do not send actual messages and ignore state file')
args = parser.parse_args()

if not args.test_mode:
	if args.f==None:
		file='/tmp/hah.txt'
	else:
		file=args.f

	f = open(file,'a+')
	idsProcessed=open(file).read()

servers = None
try:
    client = httpx.Client(http2=True)
    rsp = client.get('https://www.hetzner.com/a_hz_serverboerse/live_data.json')
    servers = json.loads(rsp.text)['server']
except:
    print('Failed to download auction list')
    exit(1)

for server in servers:
	if not args.test_mode and str(server['key']) in idsProcessed:
		continue

	sp_ent_hdd=False
	sp_dc_ssd=False
	sp_hw_raid=False
	sp_red_psu=False

	for special in server['specials']:
		if special=='Ent. HDD':
			sp_ent_hdd=True
		if special=='DC SSD':
			sp_dc_ssd=True
		if special=='HWR':
			sp_hw_raid=True
		if special=='Red.PS':
			sp_red_psu=True

	datacenter=False if args.dc else True

	if args.dc is not None and args.dc[0] in server['datacenter']:
		datacenter=True

	price_value= round((100+args.tax[0])*float(server['price'])/100,0)
	price      = price_value<=args.price[0]
	disk_count = server['hdd_count']>=args.disk_count[0]
	disk_size  = server['hdd_size']>=args.disk_size[0]
	disk_quick = server['is_highio'] if args.disk_quick else True
	disk_ent   = (sp_ent_hdd or sp_dc_ssd) if args.disk_ent else True
	hw_raid    = sp_hw_raid if args.hw_raid else True
	red_psu    = sp_red_psu if args.red_psu else True
	cpu_count  = server['cpu_count']>=args.cpu_count[0]
	cpu_score  = server['cpu_benchmark']>=args.cpu_score[0]
	ram        = server['ram']>=args.ram[0]
	ecc        = server['is_ecc'] if args.ecc else True

	if price and disk_count and disk_size and disk_quick and disk_ent and cpu_count and cpu_score and ram and ecc and datacenter:
		msg="Hetzner server %.2f€: %dGB, %s (%d), %s HDD (%s)\nhttps://www.hetzner.com/sb ID: %d" % \
			(price_value, server['ram'],server['cpu'],server['cpu_benchmark'],server['hdd_hr'],
			server['datacenter'][0],server['key'])
		print(msg)

		if not args.test_mode:
			telegram_send.send(messages=[msg], parse_mode="markdown")
			f.write(","+str(server['key']))

if not args.test_mode:
	f.close()
