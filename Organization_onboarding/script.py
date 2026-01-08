from extras.scripts import Script, StringVar  
from tenancy.models import Tenant

from utilities.exceptions import AbortScript
from django.utils.text import slugify

    
class OrganizationOnboarding(Script):

    class Meta(Script.Meta):
        name = "Organization onboarding"
        description = "Standartizated customer onboarding"
        # fieldsets = (  
        #     ('Organization Details', ('edrpou', 'short_name', 'full_name', 'dns_zone')),  
        #     ('Contact Information', ('contact_name', 'contact_email', 'contact_phone'))  
        # ) 

    # General Information  
    edrpou = StringVar(  
        description="EDRPOU",  
        required=True,
    ) 

    short_name = StringVar(  
        description="Short name",  
        required=True  
    )  
    full_name = StringVar(  
        description="Full name",  
        required=True  
    ) 
    dns_zone = StringVar(
       description="Organization domain zone",
       required=True
    )

    contact_name = StringVar(
        description="Contact person full name",
        required=True
    )

    contact_phone = StringVar(
        description="Contact person phone",
        required=False
    )

    contact_email = StringVar(
        description="Contact person email",
        required=False
    )


    def run(self, data, commit):  
        # Access the form data  
        edrpou = data['edrpou']  
        short_name = data['short_name']  
        full_name = data['full_name']

        zone = data['dns_zone']
        slug = zone.split(".")[0]

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
