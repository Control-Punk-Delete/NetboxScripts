import json
import ipaddress

from extras.scripts import Script, StringVar
from utilities.exceptions import AbortScript
from ipam.models import IPAddress, IPRange, Prefix

class IPAddressValidator(Script):
    ip_str = StringVar()

    def get_aws_prefixes(self, ip_type: int = 4, raw_file_path = "./netbox/scripts/aws_raw_data"):
        with open(raw_file_path, "r") as file:
            data = json.load(file)
            file.close()

        if ip_type == 4:
            return data.get("prefixes")

        elif ip_type == 6:
            return data.get("ipv6_prefixes")

        else:
            raise AbortScript("Wrong ip_type error")

    def check_ipv4_is_aws(self, ip_str: str = "0.0.0.0"):
        ip = ipaddress.IPv4Address(ip_str)
        
        for item in self.get_aws_prefixes(ip_type=4): 
            if ip in ipaddress.IPv4Network(item.get("ip_prefix")): return True
        
        return False

    def check_ipv6_is_aws(self, ip_str: str = "0.0.0.0"):
        ip = ipaddress.IPv6Address(ip_str)
        
        for item in self.get_aws_prefixes(ip_type=6): 
            if ip in ipaddress.IPv6Network(item.get("ip_prefix")): return True
        
        return False


    def run(self, data, commit):
        self.log_debug(data)
        if data.get("url", "").startswith("/api/ipam/ip-addresses/"):
            ip_str = data['address'].split("/")[0]
            input_type = "IP Address"

        elif data.get("url", "").startswith("/api/ipam/prefixes/"):
            ip_str = data["prefix"].split("/")[0]
            input_type = "Prefix"

        elif data.get("url", "").startswith("/api/ipam/ip-ranges/"):
            ip_str = data["start_address"].split("/")[0]
            input_type = "IP Range"
        
        else:
            raise AbortScript("Unexpected input data")
        
        ip_family = ip_family = data.get('family').get('value')
        
        self.log_debug(f"{input_type} input object. IP Address string:{ip_str}, IP type: {ip_family}")

        if ip_family == 4:
            self.log_debug("IPv4 Verification started")
            self.log_info(self.check_ipv4_is_aws(ip_str = ip_str))

        elif ip_family == 6:
            self.log_debug("IPv6 Verification started")
            pass

        else:
            raise AbortScript(f"Unknown IP Family {ip_family}")
            
        


