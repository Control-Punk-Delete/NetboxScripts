import dns.resolver

from extras.scripts import *
from ipam.models import IPAddress
from netbox_dns.models import (Record)
from utilities.exceptions import AbortScript
from tenancy.models import Tenant
from extras.models import Tag 

from network_classifier import NetworkClassifier

class DnsResolve(Script):

    class Meta(Script.Meta):
        name = "DNS Resolver"
        description = "Make an resolve an DNS Record object"
        scheduling_enabled = False

    def resolve_dns_record(self, record):
        try:
            return [answer.to_text() for answer in dns.resolver.resolve(record, 'A')]
        except Exception as e:
            self.log_warning(f"Python DNS raise error: {e}")
            return []


    def run(self, data, commit):
        classifier = NetworkClassifier(auto_update=True)  # тягне дані за DEFAULT_SOURCE_URL

        self.log_info(f"Input data: {data}")
        
        # Отримуємо обʼєкт ДНС запису для подальшого його зміни
        dns_record_object = Record.objects.get(pk=data.get('id', None))
        self.log_debug(f"Input DNS Record object id: {dns_record_object}")

        # Отримуємо рядок ДНС для виконання резолву
        dns_record_str = data.get('fqdn')[:-1]
        self.log_debug(f"Extract Clear DNS Record: {dns_record_str}")
        
        # Отримуємо Ідентифікатор Тенанта, щоб використатит його при створені ІР адрес які не існують
        tenant = None  
        if data['tenant']:  
            tenant = Tenant.objects.get(pk=data['tenant']['id'])
            self.log_debug(f"Extract Tenant: {tenant}")

        # Виконання резолву домена в ІР
        self.log_debug("Try to resolve DNS Record")
        resolved_ips = self.resolve_dns_record(dns_record_str)

        self.log_debug(f"Find {len(resolved_ips)} ip addresses: {resolved_ips}")

        # Ініціалізація переліку ІД ІР обєктів, які необхідно привʼязати до ДНС запису 
        resolved_ips_id = []
        # Ініціалізація категорій для привʼязки до ДНС запису
        dns_record_categories = [ ]
        dns_record_providers = [ ]

        # # Якщо резолв не вийшов - змінюємо статус домена на - inactive.
        if resolved_ips == []:
            dns_record_object.status = "inactive"
            dns_record_object.save()
            self.log_success(f"DNS Record {dns_record_str} has no resolved IP Address")
      
        else:
  
            # Перевірка чи створені обʼєкти ІР, якщо ні - створюємо 
            for ip in resolved_ips:

                # Перевірка IP на належність до класу
                self.log_debug(f"{ip} - class check")
                clusifier_result = classifier.lookup(ip)
                self.log_debug(f"{clusifier_result}")
                
                

                if clusifier_result.categories:
                    dns_record_categories.append(*clusifier_result.categories)
                    dns_record_providers.append(*clusifier_result.providers)
                    self.log_debug(f"{ip} has {clusifier_result.categories} categories")
                    continue

                # Cтворення IP Address з відповідними умовами (якщо він не належить відповідній категорії)
                ipaddr, created = IPAddress.objects.get_or_create(address= ip ,  
                                                                  defaults={ 'status': 'active',
                                                                             'tenant':  tenant, 
                                                                             'description': f"Отримано в наслідок автоматичного резолву домена {dns_record_str}"} )
                
                # Якщо обʼєкт був створений - встановлюємо відповідний source 
                if created:
                  self.log_info(f"Create new IP Address object: {ipaddr}")
                  ipaddr.custom_field_data['source'] = "scanner"
                 
                resolved_ips_id.append(ipaddr.id)
                # Для кожного ІР привʼязуємо домен який виконав резолв
                # Отримуємо перелік вже привʼязаних доменів
                exist_domains = ipaddr.custom_field_data.get('domains')

                # Якщо привʼязані домени відсутні перевизначаємо (чомусь .get [])
                if not exist_domains:
                    exist_domains = []

                self.log_debug(f"Existed domains: {exist_domains}, type: {type(exist_domains)}")

                # Якщо даниого обʼєкта немає в вже наявному переліку додаємо його
                if not dns_record_object.id in exist_domains:
                    self.log_debug(f"Append domain to list of links {dns_record_object.id}")
                    exist_domains.append(dns_record_object.id)

                # Перевизначаємо обʼєкт та зберігаємо його
                ipaddr.custom_field_data['domains'] = exist_domains
                ipaddr.save()

        
        # Отримуємо перелік існуючих повʼязаних обʼєктів ІР адрес
        existed_ips = dns_record_object.custom_field_data.get('ip_address', [])
        self.log_debug(f"Existed IP Address: {existed_ips}")
        
        # Якщо такі обʼєкти відсутні перевизначаємо тип змінної 
        if not existed_ips:
            existed_ips = []

        # Формуємо актуальни перелік ІР адресів (Існуючі + Ті які зарезолвились). Перевизначаємо та зберігаємо обʼєкт
        dns_record_object.custom_field_data['ip_address'] = list(set( existed_ips + resolved_ips_id))
        self.log_debug(f"Update DNS Record : {existed_ips}")

        dns_record_object.save()


        if dns_record_categories:
            self.log_debug(f"Add a categories tags: {dns_record_categories}")
            for t in dns_record_categories:
                tag, created = Tag.objects.get_or_create( name=t.lower(), defaults={'slug': t.lower()})
                dns_record_object.tags.add(tag)

            self.log_debug(f"Add a categories provides tags: {dns_record_categories}")
            for p in dns_record_providers:
                tag, created = Tag.objects.get_or_create( name=p.lower(), defaults={'slug': p.lower()})
                dns_record_object.tags.add(tag )               
