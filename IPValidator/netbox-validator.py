import json
import ipaddress

from extras.scripts import Script, StringVar
from utilities.exceptions import AbortScript
from ipam.models import IPAddress, IPRange, Prefix

class IPAddressValidator(Script):

    # AWS 
    def get_aws_prefixes(self, ip_type: int = 4, raw_file_path = "./netbox/scripts/aws_raw_data"):
        with open(raw_file_path, "r") as file:
            data = json.load(file)
            file.close()

        if ip_type == 4:
            return data.get("prefixes")

        elif ip_type == 6:
            return data.get("ipv6_prefixes")

        else:
            raise "Wrong ip_type error"

    def is_aws(self, ip_str: str = "0.0.0.0", ip_type: int = 4):

        if ip_type == 4:
            ip = ipaddress.IPv4Address(ip_str)
            for item in self.get_aws_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(item.get("ip_prefix")): return True
            
            return False
        elif ip_type == 6:
            ip = ipaddress.IPv6Address(ip_str)
            for item in self.get_aws_prefixes(ip_type): 
                if ip in ipaddress.IPv6Network(item.get("ip_prefix")): return True
            
            return False
        else:
            raise "Unexpected ip_type"
        

    # Azure
    def get_azure_prefixes(self, ip_type: int = 4, raw_file_path = "./netbox/scripts/azure_raw_data"):
        with open(raw_file_path, "r") as file:
            data = json.load(file)
            file.close()


        if ip_type == 4:
            ipv4_prefixes = []



            for application in data.get("values"):
                for prefix in application.get("properties").get("addressPrefixes"):
                    try:
                        ipv4_prefixes.append(str(ipaddress.IPv4Network(prefix)))
                    except ipaddress.AddressValueError as e:
                        continue

            return ipv4_prefixes

        elif ip_type == 6:
            ipv6_prefixes = []
            for application in data.get("values"):
                for prefix in application.get("properties").get("addressPrefixes"):
                    try:
                        ipv6_prefixes.append(str(ipaddress.IPv6Network(prefix)))
                    except ipaddress.AddressValueError as e:

                        continue
            return ipv6_prefixes
        else:
            raise "Wrong ip_type error"

    def is_azure(self, ip_str: str = "0.0.0.0", ip_type: int = 4):

        if ip_type == 4:
            ip = ipaddress.IPv4Address(ip_str)
            for prefix in self.get_azure_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(prefix): return True
            return False
        
        elif ip_type == 6:
            ip = ipaddress.IPv6Address(ip_str)
            for item in self.get_azure_prefixes(ip_type): 
                if ip in ipaddress.IPv6Network(item.get("ip_prefix")): return True
            return False
        
        else:
            raise "Unexpected ip_type"
        

    # ms365
    def get_ms365_prefixes(self, ip_type: int = 4, raw_file_path = "./netbox/scripts/ms365_raw_data"):
        with open(raw_file_path, "r") as file:
            data = json.load(file)
            file.close()

        if ip_type == 4:
            ipv4_prefixes = []
            
            for application in data:
                for prefix in application.get("ips", []):
                    try:
                        ipv4_prefixes.append(str(ipaddress.IPv4Network(prefix)))
                    except ipaddress.AddressValueError as e:
                        continue

            return ipv4_prefixes

        elif ip_type == 6:
            ipv6_prefixes = []
            
            for application in data:
                for prefix in application.get("ips", []):
                    try:
                        ipv6_prefixes.append(str(ipaddress.IPv6Network(prefix)))
                    except ipaddress.AddressValueError as e:
                        continue
                    
            return ipv6_prefixes

        else:
            raise "Wrong ip_type error"

    def is_ms365(self, ip_str: str = "0.0.0.0", ip_type: int = 4):

        if ip_type == 4:
            ip = ipaddress.IPv4Address(ip_str)
            for prefix in self.get_ms365_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(prefix): return True
            return False
        
        elif ip_type == 6:
            ip = ipaddress.IPv6Address(ip_str)
            for prefix in self.get_ms365_prefixes(ip_type): 
                if ip in ipaddress.IPv6Network(prefix): return True
            return False
        
        else:
            raise "Unexpected ip_type"


    # Cloudflare
    def get_cloudflare_prefixes(self, ip_type: int = 4, raw_file_path = "./netbox/scripts/cloudflare_raw_data"):
        with open(raw_file_path, "r") as file:
            data = json.load(file)
            file.close()

        if ip_type == 4:
            return data.get("result").get("ipv4_cidrs")

        elif ip_type == 6:
            return data.get("result").get("ipv6_cidrs")

        else:
            raise "Wrong ip_type error"

    def is_cloudflare(self, ip_str: str = "0.0.0.0", ip_type: int = 4):
        if ip_type == 4:
            ip = ipaddress.IPv4Address(ip_str)
            for prefix in self.get_cloudflare_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(prefix): return True
            return False
        
        elif ip_type == 6:

            ip = ipaddress.IPv6Address(ip_str)
            for prefix in self.get_cloudflare_prefixes(ip_type): 
                if ip in ipaddress.IPv6Network(prefix): return True
            return False
        
        else:
            raise "Unexpected ip_type"


    # Google
    def get_google_prefixes(self, ip_type: int = 4, raw_file_path = "./netbox/scripts/google_raw_data"):
        with open(raw_file_path, "r") as file:
            data = json.load(file)
            file.close()

        if ip_type == 4:
            return [service.get("ipv4Prefix") for service in data.get("prefixes") if "ipv4Prefix" in service.keys()]

        elif ip_type == 6:
            return [service.get("ipv6Prefix") for service in data.get("prefixes") if "ipv6Prefix" in service.keys()]

        else:
            raise "Wrong ip_type error"

    def is_google(self, ip_str: str = "0.0.0.0", ip_type: int = 4):
        
        if ip_type == 4:
            ip = ipaddress.IPv4Address(ip_str)
            for prefix in self.get_google_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(prefix): return True
            return False

        elif ip_type == 6:
            ip = ipaddress.IPv6Address(ip_str)
            for prefix in self.get_google_prefixes(ip_type): 
                if ip in ipaddress.IPv6Network(prefix): return True
            return False
        else:
            raise "Unexpected ip_type"

    # Google Cloud
    def get_google_cloud_prefixes(self, ip_type: int = 4, raw_file_path = "./netbox/scripts/google_cloud_raw_data"):
        with open(raw_file_path, "r") as file:
            data = json.load(file)
            file.close()

        if ip_type == 4:
            return [service.get("ipv4Prefix") for service in data.get("prefixes") if "ipv4Prefix" in service.keys()]

        elif ip_type == 6:
            return [service.get("ipv6Prefix") for service in data.get("prefixes") if "ipv6Prefix" in service.keys()]

        else:
            raise "Wrong ip_type error"

    def is_google_cloud(self, ip_str: str = "0.0.0.0", ip_type: int = 4):

        if ip_type == 4:
            ip = ipaddress.IPv4Address(ip_str)
            for prefix in self.get_google_cloud_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(prefix): return True
            return False

        elif ip_type == 6:
            ip = ipaddress.IPv6Address(ip_str)
            for prefix in self.get_google_cloud_prefixes(ip_type): 
                if ip in ipaddress.IPv6Network(prefix): return True
            return False

        else:
            raise "Unexpected ip_type"


    # Akamai
    def get_akamai_prefixes(self, ip_type: int = 4, raw_filev4_path = "./netbox/scripts/akamai_raw_data", raw_filev6_path = "./netbox/scripts/akamai_v6_raw_data"):
        if ip_type == 4:

            with open(raw_filev4_path, "r") as file:
                data = file.readlines()

            file.close()
            return [prefix.strip() for prefix in data]

        elif ip_type == 6:

            with open(raw_filev6_path, "r") as file:
                data = file.readlines()

            file.close()
            return [prefix.strip() for prefix in data]
        
        else:
            raise "Wrong ip_type error"

    def is_akamai(self, ip_str: str = "0.0.0.0", ip_type: int = 4):

        if ip_type == 4:
            ip = ipaddress.IPv4Address(ip_str)

            for prefix in self.get_akamai_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(prefix): return True
            return False
        
        elif ip_type==6:
            ip = ipaddress.IPv6Address(ip_str)

            for prefix in self.get_akamai_prefixes(ip_type): 
                if ip in ipaddress.IPv4Network(prefix): return True
            return False
        
        else:
            raise "Unexpected ip_type"


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
        

        ip_family = data.get('family').get('value')
        
        self.log_debug(f"{input_type} input object. IP Address string:{ip_str}, IP type: {ip_family}")

        
        TAGS = []

        if ip_family == 4:
            ip = ipaddress.IPv4Address(ip_str)

        elif ip_family == 6:
            ip = ipaddress.IPv6Address(ip_str)
        else:
            raise AbortScript(f"Unknown IP Family {ip_family}")
        


        if ip.is_global:
            if self.is_akamai(ip_str=ip_str, ip_type=ip_family): TAGS.extend(['cdn', 'akamai'])
            if self.is_aws(ip_str=ip_str, ip_type=ip_family): TAGS.extend(['cloud', 'aws'])
            if self.is_azure(ip_str=ip_str, ip_type=ip_family): TAGS.extend(['cloud', 'azure'])
            if self.is_cloudflare(ip_str=ip_str, ip_type=ip_family): TAGS.extend(['cdn', 'cloudflare'])
            if self.is_google(ip_str=ip_str, ip_type=ip_family): TAGS.extend(['cloud', 'google'])
            if self.is_google_cloud(ip_str=ip_str, ip_type=ip_family): TAGS.extend(['cloud', 'google-cloud'])
            if self.is_ms365(ip_str=ip_str, ip_type=ip_family): TAGS.extend(['cloud', 'ms365'])

            
        if ip.is_private:
            TAGS.append('private')
            if ip.is_link_local: TAGS.append('link-local')
            if ip.is_loopback: TAGS.append('loopback')
        
        if ip.is_multicast: TAGS.append('multicast')
        if ip.is_reserved: TAGS.append('reserved')
        if ip.is_unspecified: TAGS.append('unspecified')

        self.log_success(TAGS)









            
        


