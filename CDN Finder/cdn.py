from extras.scripts import *
from glob import glob
from itertools import chain

class IPValidator(Scripts):
    CDN_IPSv4_LIST = []
    CDN_IPSv6_LIST = []

    def cdn_list_vreator(self):
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
        self.log_debug(f"Script is starting")
        self.log_debug(f"Start running cdn list creation")

        self.cdn_list_vreator(self)

        self.log_info(f"v4: {self.CDN_IPSv4_LIST}")
        self.log_info(f"v4: {self.CDN_IPSv6_LIST}")