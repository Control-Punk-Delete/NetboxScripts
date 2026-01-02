import dns.resolver

from extras.scripts import *
from ipam.models import IPAddress
from ipam.choices import IPAddressStatusChoices  
from netbox_dns.models import (Record)
from utilities.exceptions import AbortScript


 
class DnsResolve(Script):
    def run(self, data, commit):
        self.log_success(f"Hello World: {data}")