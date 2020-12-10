# ha_cluster
![CI Testing](https://github.com/linux-system-roles/ha_cluster/workflows/tox/badge.svg)

An Ansible role for managing High Availability Clustering.

## Limitations

* Supported OS: RHEL 8.3+, Fedora 31+
* The role expects High-Availability Add-on repositories to be enabled on
  systems running RHEL.
* The role replaces the configuration of HA Cluster on specified nodes. Any
  settings not specified in the role variables will be lost.
* For now, the role is only capable of configuring a basic corosync cluster.

## Role Variables

### Defined in `defaults/main.yml`

#### `ha_cluster_cluster_present`

boolean, default: `yes`

If set to `yes`, HA cluster will be configured on the hosts according to other
variables. If set to `no`, all HA Cluster configuration will be purged from
target hosts.

#### `ha_cluster_start_on_boot`

values: `yes`, `no`, `'nochange'`, default: `yes`

If set to `yes`, cluster services will be configured to start on boot. If set
to `no`, cluster services will be configured not to start on boot. If set to
`'nochange'`, current settings will be kept.

#### `ha_cluster_fence_agent_packages`

list of fence agent packages to install, default: fence-agents-all, fence-virt

#### `ha_cluster_hacluster_password`

string, no default - must be specified

Password of the `hacluster` user. This user has full access to a cluster.

#### `ha_cluster_authkey_corosync`

256 bytes of random data, no default - must be specified

Authentication and encryption key for Corosync communication. It is highly
recommended to have a unique value for each cluster.

#### `ha_cluster_authkey_pacemaker`

256 bytes of random data, no default - must be specified

Authentication and encryption key for Pacemaker communication. It is highly
recommended to have a unique value for each cluster.

#### `ha_cluster_authkey_fence_virt_path`

Path to an authentication key for fence-virt or fence-xvm fence agent. This is
mandatory if you intend to install and use those fence agents.

#### `ha_cluster_pcsd_SSL_cert`

Structure and default value:
```yaml
ha_cluster_pcsd_SSL_cert:
  public: ''
  private: ''
```

Filepaths to SSL certificate and private key pair for pcsd. If this is not
specified, a certificate - key pair already present on a node will be used or a
random new one will be generated.

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

string, default: `'my-cluster'`

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
    ha_cluster_authkey_corosync: "corosync key, 256 bytes of random data"
    ha_cluster_authkey_pacemaker: "pacemaker key, 256 bytes of random data"
    ha_cluster_authkey_fence_virt_path: "./fence_xvm.key"

  roles:
    - linux-system-roles.ha-cluster
```

To purge all cluster configuration, run this:
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_present: no

  roles:
    - linux-system-roles.ha-cluster
```

## License

MIT

## Author Information

Tomas Jelinek
