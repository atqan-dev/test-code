import os
import base64
from typing import Dict, Tuple

import requests

from ..signing import clean_up_certificate_string

class Settings:
    API_VERSION = "V2"
    SANDBOX_BASEURL = "https://gw-apic-gov.gazt.gov.sa/e-invoicing/developer-portal"
    SIMULATION_BASEURL = "https://gw-apic-gov.gazt.gov.sa/e-invoicing/simulation"
    PRODUCTION_BASEURL = "https://gw-apic-gov.gazt.gov.sa/e-invoicing/core"

class API:
    def __init__(self):
        self.apiurl = Settings.SANDBOX_BASEURL
        
        zatca_mode = os.environ.get('ZATCA_MODE')
        if zatca_mode == 'simulation':
            self.apiurl = Settings.SIMULATION_BASEURL
        elif zatca_mode == 'developer':
            self.apiurl = Settings.SANDBOX_BASEURL
        elif zatca_mode == 'production':
            self.apiurl = Settings.PRODUCTION_BASEURL

    def get_auth_headers(self, certificate: str, secret: str) -> Dict[str, str]:
        if certificate and secret:
            certificate_stripped = clean_up_certificate_string(certificate)
            basic = base64.b64encode(f"{base64.b64encode(certificate_stripped.encode()).decode()}:{secret}".encode()).decode()
            return {
                "Authorization": f"Basic {basic}"
            }
        return {}

    def compliance(self, certificate: str, secret: str):
        auth_headers = self.get_auth_headers(certificate, secret)

        async def issue_certificate(csr: str, otp: str) -> Tuple[str, str, str]:
            headers = {
                "Accept-Version": Settings.API_VERSION,
                "OTP": otp
            }
            response = requests.post(
                f"{self.apiurl}/compliance",
                json={"csr": base64.b64encode(csr.encode()).decode()},
                headers={**auth_headers, **headers}
            )
            if response.status_code != 200:
                raise Exception("Error issuing a compliance certificate.")
            
            issued_certificate = base64.b64decode(response.json()["binarySecurityToken"]).decode()
            issued_certificate = f"-----BEGIN CERTIFICATE-----\n{issued_certificate}\n-----END CERTIFICATE-----"
            api_secret = response.json()["secret"]
            return issued_certificate, api_secret, response.json()["requestID"]

        async def check_invoice_compliance(signed_xml_string: str, invoice_hash: str, egs_uuid: str) -> Dict:
            headers = {
                "Accept-Version": Settings.API_VERSION,
                "Accept-Language": "en",
            }
            response = requests.post(
                f"{self.apiurl}/compliance/invoices",
                json={
                    "invoiceHash": invoice_hash,
                    "uuid": egs_uuid,
                    "invoice": base64.b64encode(signed_xml_string.encode()).decode()
                },
                headers={**auth_headers, **headers}
            )
            if response.status_code != 200:
                raise Exception("Error in compliance check.")
            return response.json()

        return {
            "issue_certificate": issue_certificate,
            "check_invoice_compliance": check_invoice_compliance
        }

    def production(self, certificate: str, secret: str):
        auth_headers = self.get_auth_headers(certificate, secret)

        async def issue_certificate(compliance_request_id: str) -> Tuple[str, str, str]:
            headers = {
                "Accept-Version": Settings.API_VERSION
            }
            response = requests.post(
                f"{self.apiurl}/production/csids",
                json={"compliance_request_id": compliance_request_id},
                headers={**auth_headers, **headers}
            )
            if response.status_code != 200:
                raise Exception("Error issuing a production certificate.")
            
            issued_certificate = base64.b64decode(response.json()["binarySecurityToken"]).decode()
            issued_certificate = f"-----BEGIN CERTIFICATE-----\n{issued_certificate}\n-----END CERTIFICATE-----"
            api_secret = response.json()["secret"]
            return issued_certificate, api_secret, response.json()["requestID"]

        async def report_invoice(signed_xml_string: str, invoice_hash: str, egs_uuid: str) -> Dict:
            headers = {
                "Accept-Version": Settings.API_VERSION,
                "Accept-Language": "en",
                "Clearance-Status": "0"
            }
            response = requests.post(
                f"{self.apiurl}/invoices/reporting/single",
                json={
                    "invoiceHash": invoice_hash,
                    "uuid": egs_uuid,
                    "invoice": base64.b64encode(signed_xml_string.encode()).decode()
                },
                headers={**auth_headers, **headers}
            )
            if response.status_code != 200:
                raise Exception("Error in reporting invoice.")
            return response.json()

        return {
            "issue_certificate": issue_certificate,
            "report_invoice": report_invoice
        }

