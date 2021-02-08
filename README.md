# ha_cluster
![CI Testing](https://github.com/linux-system-roles/ha_cluster/workflows/tox/badge.svg)

An Ansible role for managing High Availability Clustering.

## Limitations

* Supported OS: RHEL 8.3+, Fedora 31+
* Systems running RHEL are expected to be registered and have High-Availability
  repositories accessible.
* The role replaces the configuration of HA Cluster on specified nodes. Any
  settings not specified in the role variables will be lost.
* For now, the role is only capable of configuring a basic corosync cluster.

## Role Variables

### Defined in `defaults/main.yml`

#### `ha_cluster_enable_repos`

boolean, default: `yes`

RHEL only, enable standard repositories contaning needed packages

#### `ha_cluster_enable_repos_eus`

boolean, default: `no`

RHEL only, enable EUS repositories contaning needed packages

#### `ha_cluster_enable_repos_e4s`

boolean, default: `no`

RHEL only, enable E4S repositories contaning needed packages

#### `ha_cluster_enable_repos_tus`

boolean, default: `no`

RHEL only, enable TUS repositories contaning needed packages

#### `ha_cluster_cluster_present`

boolean, default: `yes`

If set to `yes`, HA cluster will be configured on the hosts according to other
variables. If set to `no`, all HA Cluster configuration will be purged from
target hosts.

#### `ha_cluster_start_on_boot`

boolean, default: `yes`

If set to `yes`, cluster services will be configured to start on boot. If set
to `no`, cluster services will be configured not to start on boot.

#### `ha_cluster_fence_agent_packages`

list of fence agent packages to install, default: fence-agents-all, fence-virt

#### `ha_cluster_hacluster_password`

string, no default - must be specified

Password of the `hacluster` user. This user has full access to a cluster. It is
recommended to vault encrypt the value, see
https://docs.ansible.com/ansible/latest/user_guide/vault.html for details.

#### `ha_cluster_corosync_key_src`

path to corosync authkey file, default: `null`

Authentication and encryption key for Corosync communication. It is highly
recommended to have a unique value for each cluster. The key should be 256
bytes of random data.

If value is provided, it is recommended to vault encrypt it. See
https://docs.ansible.com/ansible/latest/user_guide/vault.html for details.

If no key is specified, a key already present on the nodes will be used. If
nodes don't have the same key, a key from one node will be distributed to other
nodes so that all nodes have the same key. If no node has a key, a new key will
be generated and distributed to the nodes.

If this variable is set, `ha_cluster_regenerate_keys` is ignored for this key.

#### `ha_cluster_pacemaker_key_src`

path to pacemaker authkey file, default: `null`

Authentication and encryption key for Pacemaker communication. It is highly
recommended to have a unique value for each cluster. The key should be 256
bytes of random data.

If value is provided, it is recommended to vault encrypt it. See
https://docs.ansible.com/ansible/latest/user_guide/vault.html for details.

If no key is specified, a key already present on the nodes will be used. If
nodes don't have the same key, a key from one node will be distributed to other
nodes so that all nodes have the same key. If no node has a key, a new key will
be generated and distributed to the nodes.

If this variable is set, `ha_cluster_regenerate_keys` is ignored for this key.

#### `ha_cluster_fence_virt_key_src`

path to fence-virt or fence-xvm pre-shared key file, default: `null`

Authentication key for fence-virt or fence-xvm fence agent.

If value is provided, it is recommended to vault encrypt it. See
https://docs.ansible.com/ansible/latest/user_guide/vault.html for details.

If no key is specified, a key already present on the nodes will be used. If
nodes don't have the same key, a key from one node will be distributed to other
nodes so that all nodes have the same key. If no node has a key, a new key will
be generated and distributed to the nodes.

If this variable is set, `ha_cluster_regenerate_keys` is ignored for this key.

If you let the role to generate new key, you are supposed to copy the key to
your nodes' hypervisor to ensure that fencing works.

#### `ha_cluster_pcsd_public_key_src`, `ha_cluster_pcsd_private_key_src`

path to pcsd TLS certificate and key, default: `null`

TLS certificate and private key for pcsd. If this is not specified, a
certificate - key pair already present on the nodes will be used. If
certificate - key pair is not present, a random new one will be generated.

If private key value is provided, it is recommended to vault encrypt it. See
https://docs.ansible.com/ansible/latest/user_guide/vault.html for details.

If these variables are set, `ha_cluster_regenerate_keys` is ignored for this
certificate - key pair.

#### `ha_cluster_regenerate_keys`

boolean, default: `no`

If this is set to `yes`, pre-shared keys and TLS certificates will be
regenerated.
See also:
[`ha_cluster_corosync_key_src`](#ha_cluster_corosync_key_src),
[`ha_cluster_pacemaker_key_src`](#ha_cluster_pacemaker_key_src),
[`ha_cluster_fence_virt_key_src`](#ha_cluster_fence_virt_key_src),
[`ha_cluster_pcsd_public_key_src`](#ha_cluster_pcsd_public_key_src-ha_cluster_pcsd_private_key_src),
[`ha_cluster_pcsd_private_key_src`](#ha_cluster_pcsd_public_key_src-ha_cluster_pcsd_private_key_src)

#### `ha_cluster_pcs_permission_list`

Structure and default value:
```yaml
ha_cluster_pcs_permission_list:
  - type: "group"
    name: "hacluster"
    allow_list:
      - "grant"
      - "read"
      - "write"
```

This configures permissions to manage a cluster using pcsd. The items are as
follows:

* `type` - `user` or `group`
* `name` - user or group name
* `allow_list` - Allowed actions for the specified user or group: `read` -
  allows to view cluster status and settings, `write` - allows to modify
  cluster settings except permissions and ACLs, `grant` - allows to modify
  cluster permissions and ACLs, `full` - allows unrestricted access to a
  cluster including adding and removing nodes and access to keys and
  certificates

#### `ha_cluster_cluster_name`

string, default: `my-cluster`

Name of the cluster.

### Inventory

Nodes' names and addresses can be configured in inventory. This is optional. If
no names or addresses are configured, play's targets will be used.

Example inventory with targets `node1` and `node2`:
```yaml
all:
  hosts:
    node1:
      ha_cluster:
        node_name: node-A
        pcs_address: node1-address
        corosync_addresses:
          - 192.168.1.11
          - 192.168.2.11
    node2:
      ha_cluster:
        node_name: node-B
        pcs_address: node2-address:2224
        corosync_addresses:
          - 192.168.1.12
          - 192.168.2.12
```

* `node_name` - the name of a node in a cluster
* `pcs_address` - an address used by pcs to communicate with the node, it can
  be a name, FQDN or an IP address and it can contain port
* `corosync_addresses` - list of addresses used by Corosync, all nodes must
  have the same number of addresses and the order of the addresses matters


## Example Playbook

Minimalistic example to create a cluster running no resources:
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: "my-new-cluster"
    ha_cluster_hacluster_password: "password"

  roles:
    - linux-system-roles.ha_cluster
```

To purge all cluster configuration, run this:
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_present: no

  roles:
    - linux-system-roles.ha_cluster
```

## License

MIT

## Author Information

Tomas Jelinek
