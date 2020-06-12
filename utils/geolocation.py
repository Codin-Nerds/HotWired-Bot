from fp.fp import FreeProxy
import requests
from contextlib import suppress


def clean_proxy(proxy: str):
    return proxy.split('//')[1]


def get_proxy():
    proxy = clean_proxy(FreeProxy(timeout=1, rand=True).get())

    return proxy

def get_loc_data(ip_addr: str):
    url = f'https://ipapi.co/{ip_addr}/json/'

    while True:
        with suppress(requests.ConnectionError):
            proxy = {"http": get_proxy(), "https": get_proxy()}
            r = requests.get(url, proxies=proxy)

            if r.status_code == 200:
                return r.json()
            else:
                return f"Error Occured! Code {r.status_code}"
