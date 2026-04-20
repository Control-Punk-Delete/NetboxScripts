import ipaddress

from extras.scripts import Script, StringVar
from utilities.exceptions import AbortScript
from ipam.models import IPAddress, IPRange, Prefix

class IPAddressValidator(Script):
    ip_str = StringVar()

    def run(self, data, commit):
        self.log_info(data)
