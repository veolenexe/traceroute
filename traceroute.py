import subprocess
import threading
import re
import sys
from urllib.request import urlopen, Request
from urllib.parse import quote, unquote
from urllib.error import URLError, HTTPError

RE_IP_AND_NUMBER = re.compile(r'\s(\d+?)\s .+?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) ', flags=re.X)
RE_AS_NUMBER = re.compile(r'AS(\d+)')
RE_DESCR_INFO = re.compile(r'descr:\s*(.+?)\n')
RE_COUNTRY_INFO = re.compile(r'country:\s*(.+?)\n')
RE_STARS =re.compile(r'(\d*)\s*(\*)\s*(\*)\s*(\*)')
GRAY_ADDRESS = ('192.168.','172.16.','10.','127.','169.254.')
WHOIS = 'http://www.nic.ru/whois/?query='

def TraceRoute(hostname):
    print(hostname)
    traceroute = subprocess.Popen(["tracert", hostname],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
    print('№\tIP\t\tASN\t\tadditional info')
    while (True):
        hop = traceroute.stdout.readline()
        if not hop:
            break
        info = re.search(RE_IP_AND_NUMBER, hop.decode('windows-1251',errors='ignore'))
        if info:
            ip = info.groups()[1]
            number = info.groups()[0]
            result = f'{number}\t{ip}'
            if ip.startswith(GRAY_ADDRESS):
                result+=f'\tGRAY'
            else:
                as_info, country, descr= GetAS(ip)
                result+=f'\t{as_info}\t\t{country} {descr}'
            print(result)
        stars = re.search(RE_STARS,hop.decode('windows-1251',errors='ignore'))
        if stars:
            print(f'{stars.group(1)}\t***')
            break

def GetAS(ip):
    url = WHOIS + ip
    info = OpenUrl(url)
    if info:
        as_number = re.search(RE_AS_NUMBER,info)
        if as_number:
            as_number =as_number.group(1)
        country = re.search(RE_COUNTRY_INFO,info)
        if country:
            country= country.group(1)
        descr = re.search(RE_DESCR_INFO,info)
        if descr:
            descr = descr.group(1)
        return (as_number, country,descr)

def OpenUrl(url):
    try:
        with urlopen(url) as page:
            return page.read().decode('utf-8', errors='ignore')
    except (URLError, HTTPError):
        return None


if __name__ == '__main__':
    address = sys.argv[1]
    if address and address!='-h':
        TraceRoute(address)
    else:
        print(' пример запуска : py traceroute.py АДРЕС')