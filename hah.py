#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests, telegram_send, argparse

parser = argparse.ArgumentParser(description='hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes them viatelegram_send')
parser.add_argument('--price',      nargs=1,required=True,type=int, help='max price (€)')
parser.add_argument('--disk-size',  nargs=1,required=True,type=int, help='min disk capacity (GB)')
parser.add_argument('--disk-quick', action='store_true',            help='require SSD/NVMe')
parser.add_argument('--cpu-score',  nargs=1,required=True,type=int, help='min CPU benchmark score')
parser.add_argument('--ram',        nargs=1,required=True,type=int, help='min RAM (GB)')
parser.add_argument('--ecc',        action='store_true',            help='require ECC memory')
parser.add_argument('-f',           nargs='?',                      help='state file')
parser.add_argument('--test-mode',  action='store_true',            help='do not send actual messages and ignore state file')
args = parser.parse_args()

tax=1.19

if not args.test_mode:
	if args.f==None:
		file='/tmp/hah.txt'
	else:
		file=args.f

	f = open(file,'a+')
	idsProcessed=open(file).read()

r = requests.get('https://www.hetzner.com/a_hz_serverboerse/live_data.json')
servers = r.json()['server']

for server in servers:
	if not args.test_mode and str(server['key']) in idsProcessed:
		continue

	price      = round(tax*float(server['price']),0)<=args.price[0]
	disk_size  = server['hdd_size']>=args.disk_size[0]
	disk_quick = server['is_highio'] if args.disk_quick else True
	cpu_score  = server['cpu_benchmark']>=args.cpu_score[0]
	ram        = server['ram']>=args.ram[0]
	ecc        = server['is_ecc'] if args.ecc else True

	if price and disk_size and disk_quick and cpu_score and ram and ecc:
		msg="Hetzner server %.2f€: %dGB, %s (%d), %s HDD \nhttps://www.hetzner.com/sb ID: %d" % (tax*float(server['price']), server['ram'],server['cpu'],server['cpu_benchmark'],server['hdd_hr'],server['key'])
		print(msg)

		if not args.test_mode:
			telegram_send.send(messages=[msg], parse_mode="markdown")
			f.write(","+str(server['key']))

if not args.test_mode:
	f.close()
