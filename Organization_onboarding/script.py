from extras.scripts import Script, StringVar  
from tenancy.models import Tenant

from utilities.exceptions import AbortScript
from django.utils.text import slugify

    
class OrganizationOnboarding(Script):

    class Meta(Script.Meta):
        name = "Organization onboarding"
        description = "Standartizated customer onboarding"

    # General Information  
    form_edrpou = StringVar(  
        description="EDRPOU",  
        required=True
    ) 

    form_short_name = StringVar(  
        description="Short name",  
        required=True  
    )  
    form_full_name = StringVar(  
        description="Full name",  
        required=True  
    ) 
    form_zone = StringVar(
       description="Organization domain zone",
       required=True
    )

    form_contact_name = StringVar(
        description="Contact person full name",
        required=True
    )

    form_contact_phone = StringVar(
        description="Contact person phone",
        required=False
    )

    form_contact_email = StringVar(
        description="Contact person email",
        required=False
    )


    def run(self, data, commit):  
        # Access the form data  
        edrpou = data['form_edrpou']  
        short_name = data['form_short_name']  
        full_name = data['form_full_name']

        zone = data['form_zone']
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
