from extras.scripts import Script, StringVar  
from tenancy.models import Tenant
from netbox_dns.models import (NameServer, Zone)
from netbox_dns.choices import (ZoneStatusChoices)

from utilities.exceptions import AbortScript
from django.utils.text import slugify

    
class OrganizationOnboarding(Script):

    class Meta(Script.Meta):
        name = "Organization onboarding"
        description = "Standartizated customer onboarding"
        fieldsets = (  
            ('Organization Details', ('input_edrpou', 'input_short_name', 'input_full_name', 'input_dns_zone')),  
            ('Contact Information', ('input_contact_name', 'input_contact_email', 'input_contact_phone')))

    # General Information  
    input_edrpou = StringVar(  
        description="EDRPOU",  
        required=True,
    ) 

    input_short_name = StringVar(  
        description="Short name",  
        required=True  
    )  

    input_full_name = StringVar(  
        description="Full name",  
        required=True  
    )

    input_dns_zone = StringVar(
       description="Organization domain zone",
       required=True
    )

    input_contact_name = StringVar(
        description="Contact person full name",
        required=True
    )

    input_contact_phone = StringVar(
        description="Contact person phone",
        required=False
    )

    input_contact_email = StringVar(
        description="Contact person email",
        required=False
    )


    def run(self, data, commit):  
        # Access the form data  
        edrpou = data['input_edrpou']  
        short_name = data['input_short_name']  
        full_name = data['input_full_name']

        domain_zone = data['input_dns_zone']
        slug = domain_zone.split(".")[0]

        self.log_debug(f"{edrpou} - {short_name} - {full_name}")


        # Check is Tenant with uniq identificator is not already exist
        if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():
            raise AbortScript(f"Tenant with edrpou { edrpou } alredy exist.")
        
        self.log_debug("Create a Tenant object")

        #Creating tenant 
        # slug=slugify(short_name.replace(" ", "-"), allow_unicode=True), -cant use need domain
        tenant = Tenant.objects.create( name=short_name, slug=slug,   
         custom_field_data={  
                 'edrpou': edrpou,  
                 'full_name': full_name  
                 }  
             )
        
        tenant.save()
        self.log_debug(f"Createed Tenant {tenant}")

        # Creating Contact Group
        # Creating Contacts from input
        # Add links Tenant - Contacts

        # Create DNS Zone

        self.log_debug(f"Get NS server")
        ns = NameServer.objects.get(pk=1)
        self.log_debug(f"Get NS server - { ns }")

        try:

            zone = Zone.objects.create(name=domain_zone,
                                    status=ZoneStatusChoices.STATUS_ACTIVE,
                                    tenant=tenant,
                                    soa_rname=domain_zone
                                    )
            zone.nameservers.set(ns)
            zone.soa_mname.set(ns)


        
            self.log_debug(f"Creating zone - { zone }")
            zone.save()
        except Exception as e:
            raise AbortScript(f"Fail to create a zone due error: {e}")
