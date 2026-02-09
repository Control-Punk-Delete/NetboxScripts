import dns.resolver

from extras.scripts import *
from ipam.models import IPAddress
from netbox_dns.models import (Record)
from utilities.exceptions import AbortScript
from ipam.choices import IPAddressStatusChoices
from tenancy.models import Tenant  

 
class DnsResolve(Script):

    def resolve_dns_record(self, record):
        self.log_debug(f"Start resolving {record}.")
        try:
            answers = dns.resolver.resolve(record, 'A')
            self.log_debug(f"Resolving success.")
            ip_addresses = [answer.to_text() for answer in answers]
            self.log_debug(f"Resolving return {len(ip_addresses)} ip addresses.")
            return ip_addresses
        except Exception as e:
            self.log_debug(f"Resolving raise error {e}. Return empty list.")
            return []


    def run(self, data, commit):

        self.log_debug(f"Start script with {data}.")
        
        if data['type'] != "A":
            raise AbortScript("Only A Record is need to be cheked.")
    
        fqdn = data['fqdn'][:-1]
        self.log_debug(f"Extracted fqdn: {fqdn}")

        resolved_ips = self.resolve_dns_record(fqdn)

        self.log_debug(f"Resolving fqdn returned {len(resolved_ips)}. 0 - Inactive, > 1 - start IP validate.")


        if len(resolved_ips) == 0:
            self.log_debug(f"0 ip address is returned - domain is inactive.")
            dns_record = Record.objects.get(pk=data['id'])
            self.log_debug(f"Status changing form {dns_record.status} to inactive")
            dns_record.status = "inactive"
            dns_record.save()
            self.log_success(f"Domain resolving script ended. Inactive domain")
        else:

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
