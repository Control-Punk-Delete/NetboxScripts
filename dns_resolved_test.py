import dns.resolver

from extras.scripts import *
from ipam.models import IPAddress
from netbox_dns.models import DNSRecord
from utilities.exceptions import AbortScript
from ipam.choices import IPAddressStatusChoices  

 
class DnsResolve(Script):
    def run(self, data, commit):
        self.log_success(f"Hello World: {data}")