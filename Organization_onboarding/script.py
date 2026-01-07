from extras.scripts import *
from tenancy.models import Tenant  
from django.utils.text import slugify  
from utilities.exceptions import AbortScript  
  
class OrganizationOnboarding(Script):  
    # class Meta(Script.Meta):  
    #     name = "Organization Information"  
    #     description = "Collect organization general information and contact details"
    #     fieldsets = (    
    #         ('General Information', ('edrpou', 'short_name', 'full_name', 'root_domain')),        
    #     )
    class Meta(Script.Meta):
        name = "Organization Information"
        description = "Collect organization general information and contact details"

    # General Information  
    edrpou = StringVar(
        description="Name of the new site"
    ) 
    # short_name = StringVar(  
    #     description="Short name",  
    #     required=True  
    # )  
    # full_name = StringVar(  
    #     description="Full name",  
    #     required=True  
    # )
    
    # root_domain = StringVar(  
    #     description="Root domain",  
    #     required=False  
    # )  
      
    # # Contact Information  
    # contact_name = StringVar(  
    #     description="Contact name",  
    #     required=False  
    # )  
    # email = StringVar(  
    #     description="Email address",  
    #     required=False  
    # )  
    # phone = StringVar(  
    #     description="Phone number",  
    #     required=False  
    # )  
  
    def run(self, data, commit):  
        edrpou = data['edrpou']  
        #short_name = data['short_name']  
        #full_name = data['full_name']

        self.log_debug(f"Edrpou {edrpou}")
          
        # if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():  
        #     raise AbortScript(f"Tenant with edrpou {edrpou} already exist.")  
          
        # tenant = Tenant.objects.create(  
        #     name=short_name,  
        #     slug=slugify(short_name),  
        #     custom_field_data={  
        #         'edrpou': edrpou,  
        #         'full_name': full_name  
        #     }  
        # )  
          
        # if commit:  
        #     tenant.save()  
        #     self.log_success(f"Tenant created: {tenant}")  
          
        # return tenant