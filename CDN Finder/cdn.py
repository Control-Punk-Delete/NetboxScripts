import ipaddress
from extras.scripts import *
from glob import glob
from itertools import chain


class CDNCreation(Script):
    CDN_IPSv4_LIST = []
    CDN_IPSv6_LIST = []


    def cdn_list_creator(self):
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

    def run(self, data, commit):
        
        self.log_info(f"Script is starting")
        self.log_info(f"Start running cdn list creation")

        self.cdn_list_creator()

        self.log_info(f"CDN List v4: {self.CDN_IPSv4_LIST}")
        self.log_info(f"CDN List v6: {self.CDN_IPSv6_LIST}")