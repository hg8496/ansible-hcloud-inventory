#!/usr/bin/env python3

from __future__ import print_function

import json
import requests
import os
import sys
import ipaddress
import yaml

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


def main():
    config = ConfigParser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'hcloud.ini')
    config.read(config_path)

    # parse config
    public_net_type = config.get('hcloud', 'public_net', fallback="ipv4")
    use_private_ip = config.getboolean('hcloud', 'use_private_ip', fallback=False)
    private_net_index = config.getint('hcloud', 'private_net_index', fallback=0)
    per_page = config.getint('hcloud', 'per_page', fallback=25)
    if per_page > 50:
        print("The per_page config option must not be greater than 50.")
        exit(1)

    # get api token
    if len(sys.argv) > 1 and sys.argv[1].find('@') > -1:
        with open(sys.argv[1].replace('@', ''), 'r') as stream:
            try:
                varfile = yaml.safe_load(stream)
                api_key = varfile['hcloud_token']
            except yaml.YAMLError as exc:
                print(exc)
    else:
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

    # get servers
    hosts = []
    hostvars = {}
    page = 1
    root = {'hcloud': {'hosts': hosts}, '_meta': {'hostvars': hostvars}}
    url = 'https://api.hetzner.cloud/v1/'
    headers = {'Authorization': 'Bearer ' + api_key}
    while True:
        r = requests.get(url + "servers?page=" + str(page) + "&per_page=" + str(per_page), headers=headers)
        for server in r.json()['servers']:
            server_name = server['name']
            hosts.append(server_name)
            hostvars[server_name] = fill_host_vars(server, public_net_type, use_private_ip, private_net_index, url,
                                                   headers)
            add_to_datacenter(root, server)
            add_to_labels(root, server)
        if r.json()['meta']['pagination']['next_page'] is None:
            break
        else:
            page += 1
    
    if config.has_section('hcloud.groupaliases'):
        for groupalias, label_value in config.items('hcloud.groupaliases'):
            if label_value in root:
                root[groupalias] = root[label_value]

    print(json.dumps(root))


def fill_host_vars(server, public_net_type, use_private_ip, private_net_index, url, headers):
    if use_private_ip:
        ip = server['private_net'][private_net_index]['ip']
    else:
        ip = server['public_net'][public_net_type]['ip']
    # In case of IPv6, set the IP to the first address of the assigned range.
    if public_net_type == "ipv6":
        ansible_host = str(ipaddress.ip_network(ip)[1])
    else:
        ansible_host = ip

    public_net = server['public_net']
    private_net = server['private_net']
    floating_ips_ids = public_net['floating_ips']
    public_net['floating_ips'] = {'ipv4': [], 'ipv6': []}
    for ip_id in floating_ips_ids:
        r = requests.get(url + "floating_ips/{}".format(ip_id), headers=headers)
        floating_ip = r.json()['floating_ip']
        ip_type = floating_ip['type']
        ip = floating_ip['ip']
        public_net['floating_ips'][ip_type].append(ip)

    return {
        'ansible_host': ansible_host,
        'hcloud_public_net': public_net,
        'hcloud_private_net': private_net,
        'hcloud_server_type': server['server_type'],
        'hcloud_image': getattr(server['image'], 'name', ''),
        'hcloud_datacenter': server['datacenter']['name'],
        'hcloud_labels': server['labels'],
    }


def add_to_datacenter(root, server):
    dc = server['datacenter']['name'].replace("-", "_")
    if dc not in root:
        root[dc] = {'hosts': []}
    root[dc]['hosts'].append(server['name'])


def add_to_labels(root, server):
    for label in server['labels']:
      vlabel = label + '_' + server['labels'][label]
      if vlabel not in root:
          root[vlabel] = { 'hosts': [] }
      root[vlabel]['hosts'].append(server['name'])


if __name__ == '__main__':
    main()
