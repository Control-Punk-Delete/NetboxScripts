import dns.resolver

from extras.scripts import *
from ipam.models import IPAddress
from netbox_dns.models import (Record)
from utilities.exceptions import AbortScript
from ipam.choices import IPAddressStatusChoices  

 
class DnsResolve(Script):

    def resolve_dns_record(self, record):
        try:
            answers = dns.resolver.resolve(record, 'A')
            ip_addresses = [answer.to_text() for answer in answers]
            return ip_addresses
        except Exception as e:
            raise AbortScript(e)

    def ip_exists(self, ip_address):  
        return IPAddress.objects.filter(address=str(ip_address)).exists() 
    
    def create_ip_address(self, ip_address, commit, **kwargs):  
        """Create new IP address with optional parameters"""  
        ip = IPAddress(  
            address=str(ip_address),  
            status=kwargs.get('status', IPAddressStatusChoices.STATUS_ACTIVE),  
            vrf=kwargs.get('vrf'),  
            tenant=kwargs.get('tenant'),  
            role=kwargs.get('role'),  
            dns_name=kwargs.get('dns_name'),  
            description=kwargs.get('description')  
        )  
        if commit:  
            ip.save()  
        return ip  

    def run(self, data, commit):

        fqdn = data['fqdn'][:-1]
        resolved_ips = self.resolve_dns_record(fqdn)

        # For each resolved IP, chek is it in the database

        ip_address_ids = []


        for ip_to_check in resolved_ips:
            if self.ip_exists(ip_to_check):  
                self.log_success(f"IP {ip_to_check} already exists in database")  
                existing_ip = IPAddress.objects.get(address=str(ip_to_check))
                ip_address_ids.append(existing_ip.id)

            else:  
                self.log_info(f"Creating IP {ip_to_check}")  
                new_ip = self.create_ip_address(ip_to_check, commit=commit)  
                if commit:  
                    self.log_success(f"Created IP {new_ip.address} (ID: {new_ip.id})")
                    ip_address_ids.append(new_ip.id)
                else:  
                    self.log_info(f"Would create IP {new_ip.address} (dry run)") 


        # Get the DNS record  
        dns_record = Record.objects.get(pk=data['id'])  

        current_ips = []

        if  data['custom_fields']['ip_address']:
            for ip in data['custom_fields']['ip_address']:
                current_ips.append(ip.id)

        list_of_new_ips =  set(current_ips + ip_address_ids)
          
        # Update the custom field  
        dns_record.custom_field_data['ip_addresses'] = list_of_new_ips  
          
        if commit:  
            dns_record.save()  
            self.log_success(f"Updated DNS record {dns_record.name} with IP addresses")  
    
        self.log_success(f"Work completed.")
