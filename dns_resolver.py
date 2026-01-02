
from extras.scripts import *
from utilities.exceptions import AbortScript


class DnsResolve(Script):
     
    dns_record = StringVar(description="DNS record to resolve for IP addresses")

    def run(self, data, commit):

        if data['dns_record'] == "test":
            raise AbortScript("Empty DNS record provided")
        self.log_success(f"Hello World: {data['dns_record']}")
