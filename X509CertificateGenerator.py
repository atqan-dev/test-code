from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.x509.oid import NameOID
from OpenSSL import crypto
import base64

class EnvironmentType:
    Production = "Production"
    Simulation = "Simulation"
    NonProduction = "NonProduction"

class X509CertificateGenerator:
    def create_certificate(self, dto, ec_key_pair, is_pem_format, environment):
        subject = self.create_certificate_subject_name(dto)
        san = self.create_certificate_other_attributes(dto)
        csr = x509.CertificateSigningRequestBuilder().subject_name(subject).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(san)]), critical=False
        ).sign(ec_key_pair.private_key, hashes.SHA256())

        if is_pem_format:
            pem = csr.public_bytes(Encoding.PEM).decode()
            return pem
        else:
            der = csr.public_bytes(Encoding.DER)
            base64_encoded_csr = base64.b64encode(der).decode()
            return base64_encoded_csr

    def create_certificate_subject_name(self, dto):
        return x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, dto.country_name),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, dto.organization_unit_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, dto.organization_name),
            x509.NameAttribute(NameOID.COMMON_NAME, dto.common_name),
        ])

    def create_certificate_other_attributes(self, dto):
        return x509.Name([
            x509.NameAttribute(NameOID.SURNAME, dto.serial_number),
            x509.NameAttribute(NameOID.USER_ID, dto.organization_identifier),
            x509.NameAttribute(NameOID.TITLE, dto.invoice_type),
            x509.NameAttribute(NameOID.STREET_ADDRESS, dto.location_address),
            x509.NameAttribute(NameOID.BUSINESS_CATEGORY, dto.industry_business_category),
        ])

    def get_certificate_template_name(self, environment):
        template_names = {
            EnvironmentType.Production: "ZATCA-Code-Signing",
            EnvironmentType.Simulation: "PREZATCA-Code-Signing",
            EnvironmentType.NonProduction: "TSTZATCA-Code-Signing",
        }
        return template_names.get(environment, "ZATCA-Code-Signing")

# Example usage:
# generator = X509CertificateGenerator()
# dto = CsrGenerationDto(...)  # Define DTO with necessary attributes
# ec_key_pair = generate_ec_key_pair()  # Define a method to generate EC key pair
# certificate = generator.create_certificate(dto, ec_key_pair, True, EnvironmentType.Production)
