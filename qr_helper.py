from base64 import b64encode
from datetime import datetime
from signing_helper import get_invoice_hash

def generate_qr(invoice_xml, digital_signature, public_key, certificate_signature):
    invoice_hash = get_invoice_hash(invoice_xml)
    seller_name = invoice_xml.get("Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName")[0]
    VAT_number = str(invoice_xml.get("Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID")[0])
    invoice_total = str(invoice_xml.get("Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount")[0]["#text"])
    VAT_total = str(invoice_xml.get("Invoice/cac:TaxTotal")[0]["cbc:TaxAmount"]["#text"])
    issue_date = invoice_xml.get("Invoice/cbc:IssueDate")[0]
    issue_time = invoice_xml.get("Invoice/cbc:IssueTime")[0]
    datetime_str = f"{issue_date} {issue_time}"
    formatted_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%SZ")
    
    qr_tlv = tlv([
        seller_name,
        VAT_number,
        formatted_datetime,
        invoice_total,
        VAT_total,
        invoice_hash,
        digital_signature,
        public_key,
        certificate_signature
    ])
    return b64encode(qr_tlv).decode()

def generate_phase_one_qr(invoice_xml):
    seller_name = invoice_xml.get("Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName")[0]
    VAT_number = str(invoice_xml.get("Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID")[0])
    invoice_total = str(invoice_xml.get("Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount")[0]["#text"])
    VAT_total = str(invoice_xml.get("Invoice/cac:TaxTotal")[0]["cbc:TaxAmount"]["#text"])
    issue_date = invoice_xml.get("Invoice/cbc:IssueDate")[0]
    issue_time = invoice_xml.get("Invoice/cbc:IssueTime")[0]
    datetime_str = f"{issue_date} {issue_time}"
    formatted_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%SZ")
    
    qr_tlv = tlv([
        seller_name,
        VAT_number,
        formatted_datetime,
        invoice_total,
        VAT_total
    ])
    return b64encode(qr_tlv).decode()

def tlv(tags):
    tlv_tags = []
    for i, tag in enumerate(tags):
        tag_value_buffer = tag.encode()
        current_tlv_value = bytes([i + 1, len(tag_value_buffer)]) + tag_value_buffer
        tlv_tags.append(current_tlv_value)
    return b''.join(tlv_tags)