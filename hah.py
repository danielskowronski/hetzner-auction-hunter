#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, requests_file, json, notifiers, argparse

parser = argparse.ArgumentParser(description='hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes to one of dozen providers supported by Notifiers library')
parser.add_argument('--data-url',    nargs=1,required=False,type=str, help='URL to live_data_sb.json', default=['https://www.hetzner.com/_resources/app/jsondata/live_data_sb.json'])
parser.add_argument('--provider',    nargs=1,required=True,type=str,  help='Notifiers provider name - see https://notifiers.readthedocs.io/en/latest/providers/index.html')
parser.add_argument('--tax',         nargs=1,required=False,type=int, help='tax rate (VAT) in percents, defaults to 19 (Germany)', default=[19])
parser.add_argument('--price',       nargs=1,required=False,type=int, help='max price (€)')
parser.add_argument('--disk-count',  nargs=1,required=False,type=int, help='min disk count', default=[1])
parser.add_argument('--disk-size',   nargs=1,required=False,type=int, help='min disk capacity (GB)')
parser.add_argument('--disk-quick',  action='store_true',             help='require SSD/NVMe')
parser.add_argument('--hw-raid',     action='store_true',             help='require Hardware RAID')
parser.add_argument('--red-psu',     action='store_true',             help='require Redundant PSU')
parser.add_argument('--gpu',         action='store_true',             help='require discrete GPU')
parser.add_argument('--ipv4',        action='store_true',             help='require IPv4')
parser.add_argument('--inic',        action='store_true',             help='require Intel NIC')
parser.add_argument('--cpu-count',   nargs=1,required=False,type=int, help='min CPU count', default=[1])
parser.add_argument('--ram',         nargs=1,required=False,type=int, help='min RAM (GB)')
parser.add_argument('--ecc',         action='store_true',             help='require ECC memory')
parser.add_argument('--dc',          nargs=1,required=False,          help='datacenter (FSN1-DC15) or location (FSN)')
parser.add_argument('-f',            nargs='?',                       help='state file')
parser.add_argument('--exclude-tax', action='store_true',             help='exclude tax from output price')
parser.add_argument('--test-mode',   action='store_true',             help='do not send actual messages and ignore state file')
parser.add_argument('--debug',       action='store_true',             help='debug mode')
parser.add_argument('--send-payload',action='store_true',             help='send server data as JSON payload')
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
	s = requests.Session()
	s.mount('file://', requests_file.FileAdapter())
	rsp = s.get(args.data_url[0], headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15'})
	servers = json.loads(rsp.text)['server']
except Exception as e:
	print('Failed to download auction list')
	print(e)
	exit(1)

if not args.test_mode:
	notifier=notifiers.get_notifier(args.provider[0])

for server in servers:
	if args.debug:
		print(json.dumps(server))
	if not args.test_mode and str(server['key']) in idsProcessed:
		continue

	sp_hw_raid=False
	sp_red_psu=False
	sp_ecc=False
	sp_gpu=False
	sp_ipv4=False
	sp_inic=False

	for special in server['specials']:
		if special=='HWR':
			sp_hw_raid=True
		if special=='RPS':
			sp_red_psu=True
		if special=='ECC':
			sp_ecc=True
		if special=='GPU':
			sp_gpu=True
		if special=='IPv4':
			sp_ipv4=True
		if special=='iNIC':
			sp_inic=True

	datacenter=False if args.dc else True

	if args.dc is not None and args.dc[0] in server['datacenter']:
		datacenter=True

	exclude_tax = args.exclude_tax
	price_value = round((100+args.tax[0])*float(server['price'])/100,0) if not exclude_tax else round((100)*float(server['price'])/100,0)
	
	price       = price_value<=args.price[0] if args.price else True
	disk_count  = server['hdd_count']>=args.disk_count[0] if args.disk_count else True
	disk_size   = server['hdd_size']>=args.disk_size[0] if args.disk_size else True
	disk_quick  = (len(server['serverDiskData']['nvme'])+len(server['serverDiskData']['sata']) >0 ) if args.disk_quick else True
	hw_raid     = sp_hw_raid if args.hw_raid else True
	red_psu     = sp_red_psu if args.red_psu else True
	cpu_count   = server['cpu_count']>=args.cpu_count[0] if args.cpu_count else True
	ram         = server['ram_size']>=args.ram[0] if args.ram else True
	ecc         = sp_ecc if args.ecc else True
	gpu         = sp_gpu if args.gpu else True
	ipv4        = sp_ipv4 if args.ipv4 else True
	inic        = sp_inic if args.inic else True

	disk_descriptors=[desc for desc in server['description'] if " GB" in desc or " TB" in desc] # FIXME
	if True or len(disk_descriptors)==0:
		disk_description="%dx %dGB" % (server['hdd_count'], server['hdd_size'])
	else:
		disk_description=", ".join(disk_descriptors)

	if price and disk_count and disk_size and disk_quick and hw_raid and red_psu and cpu_count and ram and ecc and gpu and ipv4 and inic and datacenter:
		msg="<b>Hetzner</b> server #%d for <b>%.2f€: %dGB RAM, %dx %s</b>, %s [DC: %s]\nhttps://www.hetzner.com/sb?search=%d" % \
			(server['key'], price_value, server['ram_size'],server['cpu_count'],server['cpu'],disk_description,
			server['datacenter'],server['key'])
		print(msg)

		if args.send_payload:
			print(json.dumps(server))
			msg+=" <pre>"+json.dumps(server)+"</pre>"


		if not args.test_mode:
			notifier.notify(message=msg, html=True)
			f.write(","+str(server['key']))

if not args.test_mode:
	f.close()
