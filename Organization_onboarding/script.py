import csv

from extras.scripts import Script, StringVar, MultiChoiceVar, DateVar, ChoiceVar, ObjectVar
from extras.models import CustomFieldChoiceSet
from tenancy.models import Tenant, ContactGroup, Contact, ContactAssignment, ContactRole
from dcim.models import Region

from netbox_dns.models import (NameServer, Zone)
from netbox_dns.choices import (ZoneStatusChoices)
from django.contrib.contenttypes.models import ContentType 
from utilities.exceptions import AbortScript

class OrganizationOnboarding(Script):

    # Get services custom choice set

    try:  
        services_choices = CustomFieldChoiceSet.objects.get(name="services_choices").choices  
    except CustomFieldChoiceSet.DoesNotExist:  
        services_choices = []

    try:
        edr_vendor_choices = CustomFieldChoiceSet.objects.get(name="edr_vendor_choices").choices
    except CustomFieldChoiceSet.DoesNotExist:
        edr_vendor_choices = []


    try:  
        sector_choices = CustomFieldChoiceSet.objects.get(name="sector_choices").choices  
    except CustomFieldChoiceSet.DoesNotExist:  
        sector_choices = []

    try:  
        sub_sector_choices = CustomFieldChoiceSet.objects.get(name="sub_sector_choices").choices  
    except CustomFieldChoiceSet.DoesNotExist:  
        sub_sector_choices = []

    # Define Meta Script

    class Meta(Script.Meta):
        name = "Створення організації"
        description = "Метод стандартизованого додавання нового Тенанту."
        scheduling_enabled = False
        fieldsets = (  
            ('Загальна інформація про організацію', ('input_edrpou', 'input_short_name', 'input_full_name', 'input_region', 'input_sector', 'input_sub_sector', 'input_dns_zone')),
            ('Інформація про сервіси та активи', ('input_services_list', 'input_edr_service_start_date', 'input_edr_service_vendor')),
            ('Інформація про контактних осіб', ('input_contact_name', 'input_contact_email', 'input_contact_phone', 'input_contact_title')))
        commit_default = True

    # General Information 

    input_edrpou = StringVar(
        label="Код ЄДРПОУ",
        regex=r'^[0-9]{8}$',
        description="Унікальний ідентифікаційний номер юридичної особи в Єдиному державному реєстрі підприємств та організацій України.",  
        required=True,
        min_length=8
    ) 

    input_short_name = StringVar(  
        label="Скорочена назва",
        description="Офіційна абревіатура або скорочкена назва юридичної особи.",  
        required=True  
    )  

    input_full_name = StringVar(
        label="Повне найменування юридичної особи.",
        description="Офіційна повна назва юридичної особи.",  
        required=True  
    )

    input_services_list = MultiChoiceVar(
        label="Сервіси",
        description="Перелік сервісів визначений в services_choices_list, які надаються організації.",
        choices=services_choices,
        required=False,
        )

    input_sector = ChoiceVar(
        label="Сектор",
        description="Галузева приналежність до сектору",
        choices=sector_choices,
        required=False,
        )

    input_sub_sector = ChoiceVar(
        label="Під сектор",
        description="Галузева приналежність до під сектору",
        choices=sub_sector_choices,
        required=False,
        )

    input_region = ObjectVar(
        label="Регіон",
        description="Область України",
        required=False,
        model=Region
    )

    input_edr_service_start_date = DateVar(
        label="Дата початку надання сервісу EDR",
        description="Дата початку надання сервісу EDR",
        required=False
    )

    input_edr_service_vendor = MultiChoiceVar(
        label="Вендор EDR",
        description="Вендор продукту наданого в рамках сервісу EDR та визначеного edr_vendor_choices_list",
        choices=edr_vendor_choices,
        required=False,
        )

    input_dns_zone = StringVar(
        label="Домен",
        description="Кореневий домен, в зоні якого розміщені ресурси організації. Використовується для створення ідентифікатору slug (тому повинен бути унікальний).",
        required=True
    )

    input_contact_name = StringVar(
        label="П.І.Б",
        description="Прізвище Імʼя По батькові контактної особи.",
        required=False
    )

    #input_contact_title = 

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

    input_contact_title = StringVar(
        label="Посада",
        description="Посада, яку займає особа в організації",
        required=False
    )


    def run(self, data, commit):

        # Access the form data
        services = data['input_services_list']
        self.log_debug(f"Extracted services data: {services}")

        edr_start_date = str(data['input_edr_service_start_date'])
        self.log_debug(f"Extracted edr start date data: {edr_start_date}")

        edr_vendors = data['input_edr_service_vendor']
        self.log_debug(f"Extracted edr vendor data: {edr_vendors}")

        edrpou = data['input_edrpou']  
        short_name = data['input_short_name']  
        full_name = data['input_full_name']

        domain_zone = data['input_dns_zone']
        slug = domain_zone.split(".")[0]


        contact_name = data['input_contact_name']
        contact_phone = data['input_contact_phone']
        contact_email = data['input_contact_email']
        contact_title = data['input_contact_title']

        sector = data['input_sector']
        sub_sector = data['input_sub_sector']

        region = data['input_region']



        self.log_debug(f"{edrpou} - {short_name} - {full_name}")


        # Check is Tenant with uniq identificator is not already exist
        if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():
            raise AbortScript(f"Tenant with edrpou { edrpou } alredy exist.")
        
        self.log_debug("Create a Tenant object")

        # Creating tenant 
        # slug=slugify(short_name.replace(" ", "-"), allow_unicode=True), -cant use need domain


        tenant_custom_data = {  
                 'edrpou': edrpou,  
                 'full_name': full_name,
                 'region': region,
                 'sector': sector,
                 'sub_sector': sub_sector,

                 'services': services,

                 'edr_start_date': edr_start_date,
                 'edr_vendor': edr_vendors,

                 'contact_email': contact_email,
                 'contact_name': contact_name
                 
                 }

        tenant = Tenant.objects.create( name=short_name, slug=slug, description=full_name,  
         custom_field_data=tenant_custom_data
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
                                              email=contact_email,
                                              description=contact_title
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
        
        