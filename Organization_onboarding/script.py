from extras.scripts import Script, StringVar  
from tenancy.models import Tenant
from django.utils.text import slugify
from utilities.exceptions import AbortScript

    
class OrganizationOnboarding(Script):  
    class Meta(Script.Meta):  
        name = "Organization Information"  
        description = "Collect organization general information and contact details"  
        fieldsets = (  
            ('General Information', ('edrpou', 'short_name', 'full_name', 'root_domain')),  
            ('Contact Information', ('contact_name', 'email', 'phone')),  
        )  
      
    # General Information  
    edrpou = StringVar(  
        description="EDRPOU",  
        required=True,
        min_length=8,  
        max_length=8 
    )  
    short_name = StringVar(  
        description="Short name",  
        required=True  
    )  
    full_name = StringVar(  
        description="Full name",  
        required=True  
    )  
    root_domain = StringVar(  
        description="Root domain",  
        required=False  
    )  
      
    # Contact Information  
    contact_name = StringVar(  
        description="Contact name",  
        required=False  
    )  
    email = StringVar(  
        description="Email address",  
        required=False  
    )  
    phone = StringVar(  
        description="Phone number",  
        required=False  
    )
  
  

    def run(self, data, commit):  
        # Access the form data  
        edrpou = data['edrpou']  
        short_name = data['short_name']  
        full_name = data['full_name']  
        root_domain = data['root_domain']  
        contact_name = data['contact_name']  
        email = data.get('email', '')  
        phone = data.get('phone', '')

        
        if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():
            raise AbortScript(f"Tenant with edrpou { edrpou } alredy exist.")
                
        self.log_debug("Create a Tenant object")

        # Full tenant creation with all fields  
        tenant = Tenant.objects.create(  
                                        name=short_name,  
                                        slug=slugify(short_name),   
                                        custom_field_data={  
                                                'edrpou': edrpou,  
                                                'full_name': full_name  
                                                })
        tenant.save()
        self.log_info(f"Tenant created. { tenant }")


            
        

            

 



