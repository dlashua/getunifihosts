#!/usr/bin/env python3
import os
import re
import sys

import requests

baseurl = os.environ.get('UNIFI_BASEURL')
username = os.environ.get('UNIFI_USERNAME')
password = os.environ.get('UNIFI_PASSWORD')
site = os.environ.get('UNIFI_SITE', 'default')
fixed_only = os.environ.get('FIXED_ONLY', False)
udm = os.environ.get('UNIFI_UDM', True)

if udm:
    url_prefix = "/proxy/network"
    url_login = "/api/auth/login"
else:
    url_prefix = ""
    url_login = "/api/login"



def get_configured_clients(session):
    # Get configured clients
    r = session.get(baseurl + url_prefix + '/api/s/' + site + '/list/user', verify=False)
    r.raise_for_status()
    return r.json()['data']


def get_active_clients(session):
    # Get active clients
    r = session.get(baseurl + url_prefix + '/api/s/' + site + '/stat/sta', verify=False)
    r.raise_for_status()
    return r.json()['data']

def prettify(name):
    return re.sub(r'[^a-zA-Z0-9-]', "", name) + ".local"
    #if re.search('^[a-zA-Z0-9-]+$', c['name'])


def get_clients():
    session = requests.Session()
    # Log in to controller
    r = session.post(baseurl + url_login, json={'username': username, 'password': password}, verify=False)
    r.raise_for_status()
    
    clients = {}
    # Add clients with alias and reserved IP
    for c in get_configured_clients(session):
        if 'name' in c and 'fixed_ip' in c:
            clients[c['mac']] = {'name': prettify(c['name']), 'ip': c['fixed_ip']}
        elif 'hostname' in c and 'fixed_ip' in c:
            clients[c['mac']] = {'name': prettify(c['hostname']), 'ip': c['fixed_ip']}
    if fixed_only is False:
        # Add active clients with alias
        # Active client IP overrides the reserved one (the actual IP is what matters most)
        for c in get_active_clients(session):
            if 'name' in c and 'ip' in c:
                clients[c['mac']] = {'name': prettify(c['name']), 'ip': c['ip']}
            elif 'hostname' in c and 'ip' in c:
                clients[c['mac']] = {'name': prettify(c['hostname']), 'ip': c['ip']}
    
    # Return a list of clients filtered on dns-friendly names and sorted by IP
    friendly_clients = [c for c in clients.values()] 
    return sorted(friendly_clients, key=lambda i: i['name'])


if __name__ == '__main__':
    try:
        for c in get_clients():
            print(c['ip'], c['name'])
    except requests.exceptions.ConnectionError:
        print('Could not connect to unifi controller at {baseurl}', file=sys.stderr)
        exit(1)


