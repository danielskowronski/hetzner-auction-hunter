#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import requests_file
import json
import notifiers
import argparse
import html2text
import base64


class Server:
    def get_disk_description(self):
        disk_descriptors = [
            desc for desc in self.server_raw["description"] if " GB" in desc or " TB" in desc]
        if len(disk_descriptors) == 0:
            disk_description = "%dx %dGB" % (
                self.server_raw["hdd_count"], self.server_raw["hdd_size"])
        else:
            disk_description = ", ".join(disk_descriptors)
        return disk_description

    def has_quick_disk(self):
        nvme_count = len(self.server_raw.get(
            "serverDiskData", []).get("nvme", []))
        sata_count = len(self.server_raw.get(
            "serverDiskData", []).get("sata", []))
        return nvme_count+sata_count > 0

    def get_smallest_disk_size(self):
        general_drives = self.disk_map.get("general", [])
        if len(general_drives) > 0:
            smallest_drive = min(general_drives)
        else:
            smallest_drive = -1
        return smallest_drive

    def __init__(self, server_raw, tax_percent=0):
        self.server_raw = server_raw
        self.tax_percent = tax_percent

        self.id = server_raw.get("id", 0)
        self.datacenter = server_raw.get("datacenter", "UNKNOWN_DATACENTER")
        self.price = server_raw.get("price", 0.0)*(100+self.tax_percent)/100

        self.ram_size = server_raw.get("ram_size", 0)
        self.ram_description = server_raw.get("ram", ["UNKNOWN_RAM"])[0]

        self.cpu_count = server_raw.get("cpu_count", 0)
        self.cpu_description = server_raw.get("cpu", "UNKNOWN_CPU")

        self.disk_count = server_raw.get("hdd_count", 0)
        self.disk_size_total = server_raw.get("hdd_size", 0)
        self.disk_map = server_raw.get(
            "serverDiskData", {"nvme": [], "sata": [], "hdd": [], "general": []})
        self.disk_quick = self.has_quick_disk()
        self.disk_description = self.get_disk_description()

        self.sp_hw_raid = False
        self.sp_red_psu = False
        self.sp_ecc = False
        self.sp_gpu = False
        self.sp_ipv4 = False
        self.sp_inic = False
        for special in server_raw.get("specials", []):
            if special == 'HWR':
                self.sp_hw_raid = True
            if special == 'RPS':
                self.sp_red_psu = True
            if special == 'ECC':
                self.sp_ecc = True
            if special == 'GPU':
                self.sp_gpu = True
            if special == 'IPv4':
                self.sp_ipv4 = True
            if special == 'iNIC':
                self.sp_inic = True
        # interesting fields left: setup_price, fixed_price, next_reduce*, serverDiskData, traffic, bandwidth

    def get_url(self):
        return f"https://www.hetzner.com/sb?search={self.id}"

    def get_header(self):
        msg = f"Hetzner server #{self.id} in {self.datacenter} for {self.price}€"
        return msg

    def get_message(self, html=True, verbose=True):
        url = self.get_url()
        msg = f"<b>Hetzner</b> server #{self.id} in {self.datacenter} for {self.price}€: <br />" + \
              f"<b>{self.ram_size}GB RAM, {self.cpu_count}x {self.cpu_description}</b>, {self.disk_description}<br />" + \
              f"<a href='{self.get_url()}'>{url}</a><br />"
        if verbose:
            json_raw = json.dumps(self.server_raw)
            msg += f"<br /><u>Details</u>:<br /><pre>{json_raw}</pre><br />"
        if not html:
            msg = html2text.html2text(msg)
        return msg


def send_notification(notifier, server, send_payload):
    if notifier == None:
        print(f"DUMMY NOTIFICATION TITLE: "+server.get_header())
        msg = server.get_message(
            html=False, verbose=send_payload).encode("utf-8")
        msg_base64 = base64.b64encode(msg).decode("utf-8")
        print(f"DUMMY NOTIFICATION BODY:  {msg_base64}")
    else:
        html_html = notifier.schema.get("properties").get("html")
        html_pamo = notifier.schema.get("properties").get("parse_mode")
        html_supported = html_html or html_pamo

        title_subject = notifier.schema.get("properties").get("subject")
        title_title = notifier.schema.get("properties").get("title")

        msg = server.get_message(html=html_supported, verbose=send_payload)
        title = server.get_header()

        if html_html:
            if title_subject:
                notifier.notify(message=msg, html=True, subject=title)
            elif title_title:
                notifier.notify(message=msg, html=True, title=title)
            else:
                notifier.notify(message=msg, html=True)
        elif html_pamo:
            if title_subject:
                notifier.notify(message=msg, parse_mode="html", subject=title)
            elif title_title:
                notifier.notify(message=msg, parse_mode="html", title=title)
            else:
                notifier.notify(message=msg, parse_mode="html")
        else:
            if title_subject:
                notifier.notify(message=msg, subject=title)
            elif title_title:
                notifier.notify(message=msg, title=title)
            else:
                notifier.notify(message=msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='hah.py -- checks for newest servers on Hetzner server auction (server-bidding) and pushes to one of dozen providers supported by Notifiers library')
    parser.add_argument('--data-url', nargs=1, required=False, type=str,
                        default=[
                            'https://www.hetzner.com/_resources/app/jsondata/live_data_sb.json'],
                        help='URL to live_data_sb.json')
    parser.add_argument('--provider', nargs=1, required=False, type=str,
                        default=["dummy"],
                        help='Notifiers provider name - see https://notifiers.readthedocs.io/en/latest/providers/index.html')
    parser.add_argument('--tax', nargs=1, required=False, type=int,
                        default=[19],
                        help='tax rate (VAT) in percents, defaults to 19 (Germany)')
    parser.add_argument('--price', nargs=1, required=False, type=int,
                        help='max price (€)')
    parser.add_argument('--disk-count',  nargs=1, required=False, type=int,
                        default=[1],
                        help='min disk count')
    parser.add_argument('--disk-size', nargs=1, required=False, type=int,
                        help='min disk capacity (GB)')
    parser.add_argument('--disk-min-size', nargs=1, required=False, type=int,
                        help='min disk capacity per disk (GB)')
    parser.add_argument('--disk-quick', action='store_true',
                        help='require SSD/NVMe')
    parser.add_argument('--hw-raid', action='store_true',
                        help='require Hardware RAID')
    parser.add_argument('--red-psu', action='store_true',
                        help='require Redundant PSU')
    parser.add_argument('--gpu', action='store_true',
                        help='require discrete GPU')
    parser.add_argument('--ipv4', action='store_true',
                        help='require IPv4')
    parser.add_argument('--inic', action='store_true',
                        help='require Intel NIC')
    parser.add_argument('--cpu-count', nargs=1, required=False, type=int,
                        default=[1],
                        help='min CPU count')
    parser.add_argument('--ram', nargs=1, required=False, type=int,
                        help='min RAM (GB)')
    parser.add_argument('--ecc', action='store_true',
                        help='require ECC memory')
    parser.add_argument('--dc', nargs=1, required=False,
                        help='datacenter (FSN1-DC15) or location (FSN)')
    parser.add_argument('-f', nargs='?',
                        default='/tmp/hah.txt',
                        help='state file')
    parser.add_argument('--exclude-tax', action='store_true',
                        help='exclude tax from output price')
    parser.add_argument('--test-mode',  action='store_true',
                        help='do not send actual messages and ignore state file')
    parser.add_argument('--debug', action='store_true',
                        help='debug mode')
    parser.add_argument('--send-payload', action='store_true',
                        help='send server data as JSON payload')
    parser.add_argument('--search', nargs=1, required=False, type=str,
                        help='search for specific server by CPU description')

    cli_args = parser.parse_args()

    if not cli_args.test_mode:
        f = open(cli_args.f, 'a+')
        idsProcessed = open(cli_args.f).read()
        if cli_args.provider[0] == "dummy":
            notifier = None
        else:
            notifier = notifiers.get_notifier(cli_args.provider[0])

    servers = None
    try:
        s = requests.Session()
        s.mount('file://', requests_file.FileAdapter())
        rsp = s.get(cli_args.data_url[0], headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15'})
        servers = json.loads(rsp.text)['server']
    except Exception as e:
        print('Failed to download auction list')
        print(e)
        exit(1)

    for server_raw in servers:
        tax = cli_args.tax[0] if not cli_args.exclude_tax else 0.0
        server = Server(server_raw, tax)

        if cli_args.debug:
            print(json.dumps(server_raw))
        if not cli_args.test_mode and str(server.id) in idsProcessed:
            continue

        datacenter_matches = False if cli_args.dc else True
        if cli_args.dc is not None and cli_args.dc[0] in server.datacenter:
            datacenter_matches = True

        price_matches = server.price <= cli_args.price[0] if cli_args.price else True

        cpu_count_matches = server.cpu_count >= cli_args.cpu_count[
            0] if cli_args.cpu_count else True
        ram_matches = server.ram_size >= cli_args.ram[0] if cli_args.ram else True

        disk_count_matches = server.disk_count >= cli_args.disk_count[
            0] if cli_args.disk_count else True
        disk_size_matches = server.disk_size_total >= cli_args.disk_size[
            0] if cli_args.disk_size else True
        disk_min_size_matches = server.get_smallest_disk_size(
        ) >= cli_args.disk_min_size[0] if cli_args.disk_min_size else True
        disk_quick_matches = server.has_quick_disk() if cli_args.disk_quick else True

        hw_raid_matches = server.sp_hw_raid if cli_args.hw_raid else True
        red_psu_matches = server.sp_red_psu if cli_args.red_psu else True
        ecc_matches = server.sp_ecc if cli_args.ecc else True
        gpu_matches = server.sp_gpu if cli_args.gpu else True
        ipv4_matches = server.sp_ipv4 if cli_args.ipv4 else True
        inic_matches = server.sp_inic if cli_args.inic else True

        if cli_args.search:
            search_matches = cli_args.search[0] in server.cpu_description
        else:
            search_matches = True


        if price_matches and disk_count_matches and disk_size_matches and disk_min_size_matches and \
                disk_quick_matches and hw_raid_matches and red_psu_matches and cpu_count_matches and \
                ram_matches and ecc_matches and gpu_matches and ipv4_matches and inic_matches and \
                datacenter_matches and search_matches:

            print(server.get_header())
            if not cli_args.test_mode:
                send_notification(notifier, server, cli_args.send_payload)
                f.write(","+str(server.id))

    if not cli_args.test_mode:
        f.close()
