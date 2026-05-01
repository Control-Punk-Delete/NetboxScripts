import ipinfo
from extras.scripts import Script
from utilities.exceptions import AbortScript
from ipam.models import IPAddress, IPRange, Prefix



class IPInfoEnrichment(Script):
    class Meta(Script.Meta):
        name = "IP Info"
        description = "Enrich IP Address objects via IPInfo"
        scheduling_enabled = False

    def run(self, data, commit):
        

        TOKEN = data.get("api_key", None)

        if not TOKEN:
            self.log_debug("API Key is not definded.")

        ip_family = data.get("family").get("value")

        if data.get("url", "").startswith("/api/ipam/ip-addresses/"):
            ip_str = data.get("address", "").split("/")[0]
            ip_obj= IPAddress.objects.get(pk=data.get("id"))
            input_type = "IP Address"
            
        elif data.get("url", "").startswith("/api/ipam/prefixes/"):
            ip_str = data.get("prefix", "").split("/")[0]
            ip_obj = Prefix.objects.get(pk=data.get("id"))
            input_type = "Prefix"
            
        elif data.get("url", "").startswith("/api/ipam/ip-ranges/"):
            ip_str = data["start_address"].split("/")[0]
            ip_obj = IPRange.objects.get(pk=data.get("id"))
            input_type = "IP Range"
            
        else:
            raise AbortScript("Unexpected input data")

        self.log_debug("Create handler")
        handler = ipinfo.getHandler(TOKEN)

        self.log_debug("Request details")
        details = handler.getDetails(ip_str)

        self.log_success(details.all)

        




        


              
        

