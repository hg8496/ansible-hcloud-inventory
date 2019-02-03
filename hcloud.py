#!/usr/bin/env python

from __future__ import print_function

import json
import requests
import os
import sys
import ipaddress

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


def main():
    config = ConfigParser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'hcloud.ini')
    config.read(config_path)
    if config.has_option('hcloud', 'public_net'):
        public_net = config.get('hcloud', 'public_net')
    else:
        public_net = 'ipv4'
    api_key = os.environ.get('HCLOUD_TOKEN')
    if not api_key:
        try:
            api_key = sys.argv[1]
        except IndexError:
            print(
                "You should set api token, like HCLOUD_TOKEN environment "
                "variable or set like first argument for script"
            )
            exit(1)
    hosts = []
    hostvars = {}
    root = { 'hcloud': {'hosts': hosts}, '_meta': { 'hostvars': hostvars }}
    url = 'https://api.hetzner.cloud/v1/servers'
    headers = {'Authorization': 'Bearer ' + api_key}

    r = requests.get(url, headers=headers)
    for server in r.json()['servers']:
        server_name = server['name']
        hosts.append(server_name)
        hostvars[server_name] = fill_host_vars(server, public_net)
        add_to_datacenter(root, server)
        add_to_labels(root, server)
    print(json.dumps(root))

def fill_host_vars(server, public_net):
    ip = server['public_net'][public_net]['ip']
    # In case op IPv6, set the IP to the first address of the assigned range.
    if public_net == "ipv6":
        ansible_host = str(ipaddress.ip_network(ip)[1])
    else:
        ansible_host = ip
    return {
        'ansible_host': ansible_host,
        'hcloud_server_type': server['server_type'],
        'hcloud_image': getattr(server['image'], 'name', ''),
        'hcloud_datacenter': server['datacenter']['name'],
        'hcloud_labels': server['labels'],
    }

def add_to_datacenter(root, server):
    dc = server['datacenter']['name']
    if dc not in root:
        root[dc] = { 'hosts': [] }
    root[dc]['hosts'].append(server['name'])

def add_to_labels(root, server):
    for label in server['labels']:
      vlabel=label + '-' + server['labels'][label]
      if vlabel not in root:
          root[vlabel] = { 'hosts': [] }
      root[vlabel]['hosts'].append(server['name'])

if __name__ == '__main__':
    main()
