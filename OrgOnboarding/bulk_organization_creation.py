import csv

from extras.scripts import Script, StringVar, MultiChoiceVar, DateVar, FileVar
from extras.models import CustomFieldChoiceSet
from tenancy.models import Tenant, ContactGroup, Contact, ContactAssignment, ContactRole

from netbox_dns.models import (NameServer, Zone)
from netbox_dns.choices import (ZoneStatusChoices)
from django.contrib.contenttypes.models import ContentType 
from utilities.exceptions import AbortScript

class BulkOrganizationImport(Script):
    class Meta(Script.Meta):
        name = "Додавання багатьох організацій"
        description = "Метод стандартизованого додавання багатьох Тенантів."
        scheduling_enabled = False
        #fieldsets = ('Перелік організацій', ('input_csv_file'))


    
    input_csv_file = FileVar(  
        label="Перелік організацій",  
        description="Завантаж CSV з наступними колонками: name*, full_name*, edrpou*, zone*, services (Sensor, Endpoint, Vulnerability, MDR), edr_start_date (YYYY-MM-DD), edr_vendor (Crowdstrike, Cisco Secure Endpoint (AMP), Cisco Secure Endpoint (AMP Private Cloud), Elastic EDR)",  
        required=False  
    ) 

    def run(self, data, commit):
        self.log_debug(f"{data}")

        if not data['input_csv_file']:
            self.log_debug("No file privided, run single")
            pass
        else:

            file = data['input_csv_file']  
            reader = csv.DictReader(file.read().decode('utf-8').splitlines())  
            created = 0  
            for row in reader:  
                self.log_debug(f"{row}")