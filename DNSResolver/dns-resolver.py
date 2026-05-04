import dns.resolver
import ipaddress

from extras.scripts import *
from ipam.models import IPAddress
from netbox_dns.models import (Record)
from utilities.exceptions import AbortScript
from tenancy.models import Tenant  

 
class DnsResolve(Script):

    class Meta(Script.Meta):
        name = "DNS Resolver"
        description = "Make an resolve an DNS Record object"
        scheduling_enabled = False

    def resolve_dns_record(self, record):
        try:
            return [answer.to_text() for answer in dns.resolver.resolve(record, 'A')]
        except Exception as e:
            self.log_debug(f"Python DNS raise error: {e}")
            return []


    def run(self, data, commit):

        self.log_info(data)

        
        