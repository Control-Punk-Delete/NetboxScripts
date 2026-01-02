# NetboxScripts

# DNS Resolver

## Requiroments

- netbox_dns - plugin
- ip_address - custom field | type multiselect object IP Address

## Trigers

Object: IP address 
Actions: Created

## Script input

DNS Record


## Script Logic

1. Make dns resolve of input `DNS Record`

2. Get All IP address that returned  and creat `resolved_ip_list[]`

3. For every `IP Address` in  `resolved_ip_list[]`

3.1 Chek is this `IP Address` already exist in Netbox
    3.1.1 No: Create `IP Address` obejct
        3.1.1.1 Return `IP Address` object `id`
    3.1.2 Yes: Get `IP Address` object `id`

3.2 Create `ids_list[]` of `IP Address` 

4. Update inputed `DNS Record` attribute `custom fields: [ { 'ip_address': ids_list[] }]`
