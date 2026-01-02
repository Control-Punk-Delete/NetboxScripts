
from extras.scripts import *
from utilities.exceptions import AbortScript


class DnsResolve(Script):
     
    dns_record = StringVar(description="DNS record to resolve for IP addresses")

    def run(self, data, commit):
        self.log_success(f"Hello World: {data}")
