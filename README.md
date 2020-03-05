# ansible-hcloud-inventory
A dynamic inventory script for hetzner cloud.

Usage:
`HCLOUD_TOKEN=example ansible-playbook site.yml -u root -i hcloud.py`
or
`ansible-playbook site.yml -u root -i "hcloud.py cloud_token"`
or
`ansible-playbook site.yml -u root -i "hcloud.py @cloud_token.yml"`

Token yaml file must contain 'hcloud_token' variable with token. This method allows that you use many of token or store token with vault.

Dependencies:
* requests(`apt install python-request`)

The inventory will consist of multiple groups:

Name | Description
---- | ----
all | contains all hosts
hcloud | contains all hosts in Hetzner Cloud
fsn1_dc8 | contains all hosts in datacenter Falkenstein
nbg1_dc3 | contains all hosts in datacenter Nürnberg
label1_value1 | contains all hosts have label "label1"="value1"
label1_value2 | contains all hosts have label "label1"="value2"

The host has the following hostvars:

Name | Description
---- | ----
ansible_host | Public or private IPv4 or IPv6 Address
ansible_public_net | Public IPv4 Address
ansible_private_net | Private IPv4 Address
hcloud_server_type | Servertype eg. CX11
hcloud_image | Name of the used image
hcloud_datacenter | Datacenter the server is running in
hcloud_labels | Instance labels

Check the [hcloud.ini](hcloud.ini) for a short explanation on how to use the ipv6 address of a server as or the private ip address of a server as value for `ansible_host`.

In [hcloud.ini](hcloud.ini) it is also possible to add aliases for the label groups created. So instead of `DNS_true` you can use `dnsservers` as group identifier.
