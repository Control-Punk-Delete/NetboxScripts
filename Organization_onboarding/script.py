from extras.scripts import Script, StringVar  
from tenancy.models import Tenant
from django.utils.text import slugify  

from utilities.exceptions import AbortScript

    
class OrganizationOnboarding(Script):  
    class Meta(Script.Meta):  
        name = "Organization Information"  
        description = "Collect organization general information and contact details"  

    # General Information  
    edrpou = StringVar(  
        description="EDRPOU",  
        required=True
    )  
    short_name = StringVar(  
        description="Short name",  
        required=True  
    )  
    full_name = StringVar(  
        description="Full name",  
        required=True  
    )  
  
  

    def run(self, data, commit):  
        # Access the form data  
        edrpou = data['edrpou']  
        short_name = data['short_name']  
        full_name = data['full_name']  
        self.log_debug(f"{edrpou} - {short_name} - {full_name}")


        
        # if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():
        #     raise AbortScript(f"Tenant with edrpou { edrpou } alredy exist.")

            
        # self.log_debug("Create a Tenant object")

        # # Full tenant creation with all fields  
        # tenant = Tenant.objects.create(  
        # name=short_name,  
        # slug=slugify(short_name),   
        # custom_field_data={  
        #         'edrpou': edrpou,  
        #         'full_name': full_name  
        #         }  
        #     )
        # self.log_debug(f"Createed Tenant {tenant}")
