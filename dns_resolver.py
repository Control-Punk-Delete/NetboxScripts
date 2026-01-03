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

    def run(self, data, commit):

        fqdn = data['fqdn'][:-1]
        resolved_ips = self.resolve_dns_record(fqdn)

        # For each resolved IP, chek is it in the database

        ip_address_ids = []


        for ip_to_check in resolved_ips:
            if IPAddress.objects.filter(ip_to_check).exists():  
                self.log_success(f"IP {ip_to_check} already exists in database")  
                existing_ip = IPAddress.objects.get(address=str(ip_to_check))
                ip_address_ids.append(existing_ip.id)

            else:  
                self.log_info(f"Creating IP {ip_to_check}")

                ip = IPAddress( address=ip_to_check,  
                                status=IPAddressStatusChoices.STATUS_ACTIVE)
                ip.full_clean()
                ip.save()
                ip_address_ids.append(ip.id)
                self.log_success(f"Created IP {ip_to_check} with ID {ip.id}")


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
