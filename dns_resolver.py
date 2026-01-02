
from dcim.models import IPAddress
from extras.scripts import Script


class DnsResolve(Script):
     
    dns_record = StringVar("DNS Record", description="DNS record to resolve for IP addresses")

    def run(self):
        self.log_success("Hello World", self.dns_record)

