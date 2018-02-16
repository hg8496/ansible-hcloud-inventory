#!/usr/bin/env python

import json
import requests
import os

def main():
    api_key = os.environ.get('HCLOUD_TOKEN')
    hosts = []
    hostvars = {}
    root = { 'hcloud': {'hosts': hosts}, '_meta': { 'hostvars': hostvars }}
    url = 'https://api.hetzner.cloud/v1/servers'
    headers = {'Authorization': 'Bearer ' + api_key}

    r = requests.get(url, headers=headers)
    for server in r.json()['servers']:
        server_name = server['name']
        hosts.append(server_name)
        hostvars[server_name] = fill_host_vars(server)
        add_to_datacenter(root, server)
    print json.dumps(root)

def fill_host_vars(server):
    return {
        'ansible_host': server['public_net']['ipv4']['ip'],
        'hcloud_server_type': server['server_type'],
        'hcloud_image': server['image']['name'],
        'hcloud_datacenter': server['datacenter']['name'],
    }

def add_to_datacenter(root, server):
    dc = server['datacenter']['name']
    if not root.has_key(dc):
        root[dc] = []
    root[dc].append(server['name'])

if __name__ == '__main__':
    main()
