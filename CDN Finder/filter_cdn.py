#from extras.scripts import *

#class CDNDetector(Script):

    # IP Address is created
    # To Do Prefix is created
    # To Do IP Range is created

#    def run(self, data, commit):

import ipaddress
from glob import glob
from itertools import chain


# Test IP object
data = {
                    "id": 10,
                    "url": "/api/ipam/ip-addresses/10/",
                    "display_url": "/ipam/ip-addresses/10/",
                    "display": "2.2.2.2/32",
                    "family": {
                            "value": 4,
                            "label": "IPv4"},
                    "address": "23.47.124.141/32",
                    "vrf": None,
                    "tenant": None,
                    "status": {
                        "value": "active",
                        "label": "Active" },
                    "role": None,
                    "assigned_object_type": None,
                    "assigned_object_id": None,
                    "assigned_object": None,
                    "nat_inside": None,
                    "nat_outside": [],
                    "dns_name": "",
                    "description": "",
                    "comments": "",
                    "tags": [],
                    "custom_fields": {},
                    "created": "2026-01-02T20:34:14.514284Z",
                    "last_updated": "2026-01-02T20:34:14.514305Z"
                    }


# Create list of ipv4 CDNs ipaddres
CDN_IPSv4_LIST = []

for line in (
    line.strip()
    for line in chain.from_iterable(open(f) for f in glob("cdn-lists/ipv4networks-*"))
):
    if not line or line.startswith("#"):
        continue
    try:
        net = ipaddress.ip_network(line, strict=False)
        if isinstance(net, ipaddress.IPv4Network):
            CDN_IPSv4_LIST.append(net)
    except ValueError:
        pass

# Create list of ipv6 CDNs ipaddres 
CDN_IPSv6_LIST = []

for line in (
    line.strip()
    for line in chain.from_iterable(open(f) for f in glob("cdn-lists/ipv6networks-*"))
):
    if not line or line.startswith("#"):
        continue
    try:
        net = ipaddress.ip_network(line, strict=False)
        if isinstance(net, ipaddress.IPv6Network):
            CDN_IPSv6_LIST.append(net)
    except ValueError:
        pass

print("CDN v4 IP Addresses:", len(CDN_IPSv4_LIST))
print("CDN v6 IP Addresses:", len(CDN_IPSv6_LIST))

def is_cdn(ip_address, ip_type: int = 4):
    if ip_type == 4:
        for cdn_network in CDN_IPSv4_LIST:
            if ip_address in cdn_network:
                return True
            
    elif ip_type == 6:
        for cdn_network in CDN_IPSv6_LIST:
            if ip_address in cdn_network:
                return True
    else:
        print("ERROR: Function is_cdn get wrong ip_type parameter.")
        exit()
    return False


def vlaidation(ip_address, ip_type: int = 4):

    if not ip_type  in [4, 6]:
        print("ERROR: Function validation get wrong ip_type parameter.")
        exit()

    # Private IP address detection
    if ip_address.is_private:
        print(f"IP Address {str(ip_address)} is private. Skip cansel validation process.")
        exit()

    print(f"IP Address {str(ip_address)} is global.")

    # Reserved IP Address detection
    if ip_address.is_reserved:
        print(f"Global IP Address {str(ip_address)} is reserved.")
        print("Add tag - 'reserved'")

    # Multicast IP Address detection
    if ip_address.is_multicast:
        print(f"Global IP Address {str(ip_address)} is multicast.")
        print("Add tag - 'multicast'")

    if is_cdn(ip_address) and ip_type == 4:
        print(f"Global IP Address {str(ip_address)} is CDN.")
        print("Add tag - 'cdn'")
        exit()

    print(f"Global IP Address is verificated!")
    print("Add tag - 'verificated'")


# If data object is IP address
if data['url'].startswith('/api/ipam/ip-addresses/'):
    if data['family']['value'] == 4:
        ip_address = ipaddress.IPv4Address(data['address'].split("/")[0])
        vlaidation(ip_address)

    elif data['family']['value'] == 6:
        ip_address = ipaddress.IPv6Address(data['address'].split("/")[0])
        vlaidation(ip_address, 6)






class IPValidator(Scripts):
    CDN_IPSv4_LIST = []
    CDN_IPSv6_LIST = []

    def __init__(self):
        for line in (
            line.strip()
            for line in chain.from_iterable(open(f) for f in glob("cdn-lists/ipv4networks-*"))
        ):
            if not line or line.startswith("#"):
                continue
            try:
                net = ipaddress.ip_network(line, strict=False)
                if isinstance(net, ipaddress.IPv4Network):
                    self.CDN_IPSv4_LIST.append(net)
            except ValueError:
                pass

        for line in (
            line.strip()
            for line in chain.from_iterable(open(f) for f in glob("cdn-lists/ipv6networks-*"))
        ):
            if not line or line.startswith("#"):
                continue
            try:
                net = ipaddress.ip_network(line, strict=False)
                if isinstance(net, ipaddress.IPv6Network):
                    self.CDN_IPSv6_LIST.append(net)
            except ValueError:
                pass

