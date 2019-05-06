import requests

http_proxy = "socks5://127.0.0.1:5689"
https_proxy = "socks5://127.0.0.1:5689"
ftp_proxy = "socks5://127.0.0.1:5689"

proxyDict = {
    "http": http_proxy,
    "https": https_proxy,
    "ftp": ftp_proxy
}

url = 'https://hastebin.com/documents'

data = 'teste|teste|teste'

r = requests.post(url, data=data, proxies=proxyDict, verify=False)

print(111)
