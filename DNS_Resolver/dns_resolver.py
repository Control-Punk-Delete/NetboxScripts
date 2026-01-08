import dns.resolver

from extras.scripts import *
from ipam.models import IPAddress
from netbox_dns.models import (Record)
from utilities.exceptions import AbortScript
from ipam.choices import IPAddressStatusChoices
from tenancy.models import Tenant  

 
class DnsResolve(Script):

    def resolve_dns_record(self, record):
        try:
            answers = dns.resolver.resolve(record, 'A')
            ip_addresses = [answer.to_text() for answer in answers]
            return ip_addresses
        except Exception as e:
            raise AbortScript(e)

    def run(self, data, commit):
        self.log_debug(f"Starting DNS resolution for {data}")

        fqdn = data['fqdn'][:-1]
        resolved_ips = self.resolve_dns_record(fqdn)

        self.log_debug(f"Resolved IPs: {resolved_ips}")

        ip_address_ids = []

        for ip_to_check in resolved_ips:
            self.log_debug(f"Processing IP: {ip_to_check}")

            if IPAddress.objects.filter(address=str(ip_to_check)).exists():  
                self.log_info(f"IP {ip_to_check} already exists in database")
                existing_ip = IPAddress.objects.get(address=str(ip_to_check))

                ip_address_ids.append(existing_ip.id)
                self.log_debug(f"Appended existing IP ID {existing_ip.id} for IP {ip_to_check}")

            else:
                self.log_info(f"IP Address creating {ip_to_check} - started")

                if data['tenant']:
                    self.log_debug(f"Search for tenant asign - {data['tenant']['display']}")
                    tenant = Tenant.objects.get(pk = data['tenant']['id'])

                    self.log_debug(f"Find tenant - {tenant}: {type(tenant)}")
                else:
                    self.log_debug("Record not asign to any tenant")
                    tenant = None

                ip = IPAddress( address = ip_to_check,
                                tenant = tenant,
                                status = IPAddressStatusChoices.STATUS_ACTIVE )
                
                self.log_debug(f"IP object created for {ip}, validating and saving.")
                ip.full_clean()
                ip.save()

                ip_address_ids.append(ip.id)
                self.log_debug(f"Appended new created ip {ip.id} ")

        self.log_info(f"Final list of IP address IDs to associate: {ip_address_ids}")
        # Get the DNS record  
        dns_record = Record.objects.get(pk=data['id'])  

        current_ips = []

        if  data['custom_fields']['ip_address']:
            for ip in data['custom_fields']['ip_address']:
                current_ips.append(ip.id)

        list_of_new_ips =  list(set(current_ips + ip_address_ids))
          
        # Update the custom field  
        dns_record.custom_field_data['ip_address'] =  list_of_new_ips  
          
        if commit:  
            dns_record.save()  
            self.log_success(f"Updated DNS record {dns_record.name} with IP addresses")  
    
        self.log_success(f"Work completed.")
