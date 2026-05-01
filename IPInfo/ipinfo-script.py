import ipinfo
from extras.scripts import Script
from utilities.exceptions import AbortScript



class IPInfo(Script):

    def run(self, data, commit):
        
        self.log_info(data)

