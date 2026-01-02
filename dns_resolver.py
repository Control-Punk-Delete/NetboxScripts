
from extras.scripts import *
from utilities.exceptions import AbortScript


class DnsResolve(Script):
     
    dns_record = StringVar(description="DNS record to resolve for IP addresses")

    def run(self):

        if not self.dns_record:
            raise AbortScript("Empty DNS record provided")
        self.log_success("Hello World", self.dns_record)

