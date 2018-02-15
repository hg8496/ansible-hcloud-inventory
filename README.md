# ansible-hcloud-inventory
An dynamic inventory script for hetzner cloud

Usage:
`HCLOUD_TOKEN=example ansible-playbook site.yml -u root -i hcloud.py`

Dependencies:
* requests(`apt install python-request`)

The inventory will consist of multiple groups:

Name | Description
---- | ----
all | contains all hosts
hcloud | contains all hosts in Hetzner Cloud
fsn1-dc8 | contains all hosts in datacenter Falkenstein
nbg1-dc3 | contains all hosts in datacenter Nürnberg

The host have the following hostvars 

Name | Description
---- | ----
ansible_host | Public IPv4 Adress
hcloud_server_type | Servertype eg. CX11
hcloud_image | Name of the used image
hcloud_datacenter | Datacenter the server is running in