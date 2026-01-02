import dns.resolver
from utilities.exceptions import AbortScript

def resolve_dns_record(record):
    try:
        answers = dns.resolver.resolve(record, 'A')
        ip_addresses = [answer.to_text() for answer in answers]
        return ip_addresses
    except Exception as e:
        raise AbortScript(e)


# Приклад використання:
if __name__ == "__main__":
    result = resolve_dns_record("mail.cip.gov.ua")
    print(f"IP адреси для example.com: {result}")