import csv  
from extras.scripts import Script, FileVar  
from extras.models import CustomField, CustomFieldChoiceSet  
from tenancy.models import Tenant, ContactGroup, Contact, ContactAssignment, ContactRole  
from netbox_dns.models import NameServer, Zone  
from netbox_dns.choices import ZoneStatusChoices  
from django.contrib.contenttypes.models import ContentType  
from utilities.exceptions import AbortScript  
  
class BulkOrganizationOnboarding(Script):  
    class Meta(Script.Meta):  
        name = "Bulk Organization Onboarding"  
        description = "Create tenants, contacts, and DNS zones from a CSV file."  
        scheduling_enabled = False  
        commit_default = True  
  
    csv_file = FileVar(  
        label="CSV file",  
        description=(  
            "Upload a CSV with headers: edrpou,short_name,full_name,dns_zone,"  
            "services,edr_start_date,edr_vendor,contact_name,contact_phone,contact_email"  
        ),  
        required=True  
    )  
  
    def run(self, data, commit):  
        file = data['csv_file']  
        if not file:  
            raise AbortScript("No file uploaded.")  
  
        reader = csv.DictReader(file.read().decode('utf-8').splitlines())  
        created_tenants = 0  
        for row in reader:  
            try:  
                self._process_row(row, commit)  
                created_tenants += 1  
            except AbortScript as e:  
                self.log_failure(f"Row skipped: {e}")  
                continue  # Continue to next row  
        self.log_info(f"Processed {created_tenants} tenants.")  
  
    def _process_row(self, row, commit):  
        edrpou = row['edrpou'].strip()  
        short_name = row['short_name'].strip()  
        full_name = row['full_name'].strip()  
        dns_zone = row['dns_zone'].strip()  
        slug = dns_zone.split('.')[0]  
        services = [v.strip() for v in row['services'].split('|') if v.strip()] if row.get('services') else []  
        edr_start_date = row['edr_start_date'].strip() or None  
        edr_vendor = [v.strip() for v in row['edr_vendor'].split('|') if v.strip()] if row.get('edr_vendor') else []  
        contact_name = row['contact_name'].strip() or None  
        contact_phone = row['contact_phone'].strip() or None  
        contact_email = row['contact_email'].strip() or None  
  
        if Tenant.objects.filter(custom_field_data__edrpou=edrpou).exists():  
            raise AbortScript(f"Tenant with edrpou {edrpou} already exists.")  
  
        # Prepare custom fields via cf proxy to handle serialization  
        tenant = Tenant(name=short_name, slug=slug)  
        tenant.cf.edrpou = edrpou  
        tenant.cf.full_name = full_name  
        tenant.cf.services = services  
        tenant.cf.edr_start_date = edr_start_date  
        tenant.cf.edr_vendor = edr_vendor  
        if commit:  
            tenant.save()  
        self.log_success(f"Created Tenant: {tenant}", tenant)  
  
        # Contact Group  
        contact_group = ContactGroup(name=short_name)  
        if commit:  
            contact_group.save()  
        self.log_success(f"Created ContactGroup: {contact_group}", contact_group)  
  
        # Contact (only if contact_name provided)  
        if contact_name:  
            contact = Contact(name=contact_name, phone=contact_phone, email=contact_email)  
            if commit:  
                contact.save()  
                contact.groups.add(contact_group)  
            self.log_success(f"Created Contact: {contact}", contact)  
  
            # Assignment  
            content_type = ContentType.objects.get_for_model(Tenant)  
            role = ContactRole.objects.get(pk=1)  # Ensure this role exists  
            assignment = ContactAssignment(  
                object_type=content_type,  
                object_id=tenant.pk,  
                contact=contact,  
                role=role  
            )  
            if commit:  
                assignment.save()  
            self.log_success(f"Assigned Contact {contact} to Tenant {tenant}", assignment)  
  
        # DNS Zone  
        ns = NameServer.objects.get(name="ns.gov.ua")  # Adjust or make configurable  
        zone = Zone(  
            name=dns_zone,  
            status=ZoneStatusChoices.STATUS_ACTIVE,  
            tenant=tenant,  
            soa_mname=ns,  
            soa_rname=dns_zone,  
            **Zone.get_defaults()  
        )  
        if commit:  
            zone.save()  
            zone.nameservers.add(ns)  
        self.log_success(f"Created Zone: {zone}", zone)