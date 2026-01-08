from extras.scripts import Script, StringVar  
from tenancy.models import Tenant

from utilities.exceptions import AbortScript
from django.utils.text import slugify

    
class OrganizationOnboarding(Script):  


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
  
  

    def run(self, data, commit):  
        # Access the form data  
        edrpou = data['form_edrpou']  
        short_name = data['form_short_name']  
        full_name = data['form_full_name']

        self.log_debug(f"{edrpou} - {short_name} - {full_name}")


        
        if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():
            raise AbortScript(f"Tenant with edrpou { edrpou } alredy exist.")
        

            
        self.log_debug("Create a Tenant object")

        # # Full tenant creation with all fields  
        tenant = Tenant.objects.create( name=short_name, slug=slugify(short_name),   
         custom_field_data={  
                 'edrpou': edrpou,  
                 'full_name': full_name  
                 }  
             )
        
        tenant.save()
        
        self.log_debug(f"Createed Tenant {tenant}")
