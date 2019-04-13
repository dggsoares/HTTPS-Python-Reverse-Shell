from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"


def create_self_signed_cert():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # create a self-signed cert
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')
    ])
    now = datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .serial_number(1000)
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=10 * 365))
            .public_key(key.public_key())
            .sign(key, hashes.SHA256(), default_backend())
    )

    with open(CERT_FILE, "wb") as output_cert:
        output_cert.write(cert.public_bytes(encoding=serialization.Encoding.PEM))
    with open(KEY_FILE, "wb") as output_key:
        output_key.write(key.private_bytes(encoding=serialization.Encoding.PEM,
                                           format=serialization.PrivateFormat.TraditionalOpenSSL,
                                           encryption_algorithm=serialization.NoEncryption())
                         )


create_self_signed_cert()
