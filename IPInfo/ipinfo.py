import ipinfo
from extras.scripts import Script
from utilities.exceptions import AbortScript



class IPInfoEnrichment(Script):
    class Meta(Script.Meta):
        name = "IP Info"
        description = "Enrich IP Address objects via IPInfo"
        scheduling_enabled = False

    def run(self, data, commit):        
        self.log_debug(data)

