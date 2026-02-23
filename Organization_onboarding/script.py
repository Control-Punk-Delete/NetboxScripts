from extras.scripts import Script, StringVar, MultiChoiceVar
from extras.models import CustomFieldChoiceSet
from tenancy.models import Tenant, ContactGroup, Contact, ContactAssignment, ContactRole

from netbox_dns.models import (NameServer, Zone)
from netbox_dns.choices import (ZoneStatusChoices)
from django.contrib.contenttypes.models import ContentType 
from utilities.exceptions import AbortScript
    
class OrganizationOnboarding(Script):


    class Meta(Script.Meta):
        name = "Створення організації"
        description = "Метод стандартизованого додавання нового Тенанту."
        scheduling_enabled = False
        fieldsets = (  
            ('Organization Details', ('input_edrpou', 'input_short_name', 'input_full_name', 'input_dns_zone')),
            ('Services',('input_services')),
            ('Contact Information', ('input_contact_name', 'input_contact_email', 'input_contact_phone')))

    # General Information 
    # Get the choice set and extract choices 



    try:  
        choice_set = CustomFieldChoiceSet.objects.get(name='services_choice_list')  
        services_choices = choice_set.choices  
    except CustomFieldChoiceSet.DoesNotExist:  
        services_choices = [['a','A'],['b','B']]



    try:
        input_services = MultiChoiceVar(
            label="Сервіси", 
            choices= services_choices,
            description="Перелік сервісів, які надані для огранізації",
            required=False  
        )
    except AttributeError as e:
        pass

    input_edrpou = StringVar(
        label="Код ЄДРПОУ",
        regex=r'^[0-9]{8}$',
        description="Унікальний ідентифікаційний номер юридичної особи в Єдиному державному реєстрі підприємств та організацій України.",  
        required=True,
        min_length=8
    ) 

    input_short_name = StringVar(  
        label="Скорочена назва",
        description="Офіційна абривіатура чи скорочкена назва юридичної особи.",  
        required=True  
    )  

    input_full_name = StringVar(
        label="Повне найменування юридичної особи.",
        description="Full name",  
        required=True  
    )

    input_dns_zone = StringVar(
        label="Домен",
        description="Кореневий домен, в зоні якого розміщені ресурси організації. Використовується для створення ідентифікатору slug (тому повинен бути унікальний).",
        required=True
    )

    input_contact_name = StringVar(
        label="П.І.Б",
        description="Прізвище Імʼя По батькові контактної особи.",
        required=True
    )

    input_contact_phone = StringVar(
        label="Телефон",
        description="Контактний номер телефону.",
        required=False
    )

    input_contact_email = StringVar(
        label="Email",
        description="Персональна або корпоративна електронна адреса.",
        required=False
    )


    def run(self, data, commit):  
        # Access the form data

        selected_services = data['input_services']
        self.log_debug(f"Extracted services data: {selected_services}")


        edrpou = data['input_edrpou']  
        short_name = data['input_short_name']  
        full_name = data['input_full_name']

        domain_zone = data['input_dns_zone']
        slug = domain_zone.split(".")[0]


        contact_name = data['input_contact_name']
        contact_phone = data['input_contact_phone']
        contact_email = data['input_contact_email']


        self.log_debug(f"{edrpou} - {short_name} - {full_name}")


        # Check is Tenant with uniq identificator is not already exist
        if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():
            raise AbortScript(f"Tenant with edrpou { edrpou } alredy exist.")
        
        self.log_debug("Create a Tenant object")

        #Creating tenant 
        # Продумати час початку надання сервісу.
        # slug=slugify(short_name.replace(" ", "-"), allow_unicode=True), -cant use need domain
        tenant = Tenant.objects.create( name=short_name, slug=slug,   
         custom_field_data={  
                 'edrpou': edrpou,  
                 'full_name': full_name,
                 'services': selected_services  
                 }  
             )
        
        tenant.save()
        self.log_success(f"Createed Tenant: {tenant}")

        # Creating Contact Group
        self.log_debug("Contact Contact Group creation: Started")
        try:
            contact_group = ContactGroup.objects.create( name=short_name )  
            self.log_success(f"Created Contact Group: {contact_group}")
            contact_group.save()  
        
        except Exception as e: 
            raise AbortScript(f"Error: { e }")


        # Creating Contacts from input
        self.log_debug("Contact Contact creation: Started")
        try:
            contact = Contact.objects.create( name=contact_name,
                                              phone=contact_phone,
                                              email=contact_email
                                            )
            
            contact.groups.add(contact_group)
            contact.save()
            self.log_success(f"Created Contact: {contact}")
        
        except Exception as e: 
            raise AbortScript(f"Error during contact creation: { e }")



        # Add links Tenant - Contacts

        content_type = ContentType.objects.get_for_model(Tenant)
        role = ContactRole.objects.get(pk=1)
        self.log_debug("Contact asigment creation: Started")
        try:
            
            assignment = ContactAssignment.objects.create(  
                object_type=content_type,  
                object_id=tenant.pk,  
                contact=contact,  
                role=role
            )
            
            assignment.save()
            self.log_success(f"Contact { contact } is asigned to Tenant { tenant }")

        except Exception as e: 
            raise AbortScript(f"Error during contact asigment creation: { e }")
        



        # Create DNS Zone
        self.log_debug("DNS Zone creation: Started")
        ns = NameServer.objects.get(name="ns.gov.ua")

        try:  
            self.log_debug(f"Creating zone")  
            zone = Zone.objects.create(name=domain_zone,  
                                    status=ZoneStatusChoices.STATUS_ACTIVE,  
                                    tenant=tenant,  
                                    soa_mname=ns,
                                    soa_rname=domain_zone,
                                    **Zone.get_defaults()
                                    )
              
            zone.nameservers.add(ns)  
            self.log_debug("Nameservers set successfully")  
            zone.save()  
            self.log_success(f"Created Zone: {zone}")
            
        except Exception as e:  
            raise AbortScript(f"Error during zone creation: {e}")