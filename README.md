# ha_cluster
![CI Testing](https://github.com/linux-system-roles/ha_cluster/workflows/tox/badge.svg)

An Ansible role for managing High Availability Clustering.

## Limitations

* Supported OS: RHEL 8.3+, Fedora 31+
* Systems running RHEL are expected to be registered and have High-Availability
  repositories accessible.
* The role replaces the configuration of HA Cluster on specified nodes. Any
  settings not specified in the role variables will be lost.
* For now, the role is capable of configuring a basic corosync cluster and
  pacemaker stonith and resources.

## Role Variables

### Defined in `defaults/main.yml`

#### `ha_cluster_enable_repos`

boolean, default: `yes`

RHEL and CentOS only, enable repositories contaning needed packages

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

#### `ha_cluster_extra_packages`

list of additional packages to be installed, default: no packages

This variable can be used to install additional packages not installed
automatically by the role, for example custom resource agents.

It is possible to specify fence agents here as well. However,
`ha_cluster_fence_agent_packages` is preferred for that, so that its default
value is overriden.

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

#### `ha_cluster_resource_primitives`

Structure, default: no resources

```yaml
ha_cluster_resource_primitives:
  - id: "resource-id"
    agent: "resource-agent"
    instance_attrs:
      - attrs:
          attribute1_name: "attribute1_value"
          attribute2_name: "attribute2_value"
    meta_attrs:
      - attrs:
          meta_attribute1_name: "meta_attribute1_value"
          meta_attribute2_name: "meta_attribute2_value"
    operations:
      - action: "operation1-action"
        attrs:
          operation1_attribute1_name: "operation1_attribute1_value"
          operation1_attribute2_name: "operation1_attribute2_value"
      - action: "operation2-action"
        attrs:
          operation2_attribute1_name: "operation2_attribute1_value"
          operation2_attribute2_name: "operation2_attribute2_value"
```

This variable defines pacemaker resources (including stonith) configured by the
role. The items are as follows:

* `id` (mandatory) -  Id of a resource.
* `agent` (mandatory) - Name of a resource or stonith agent, for example
  `ocf:pacemaker:Dummy` or `stonith:fence_xvm`. It is mandatory to use
  `stonith:` for stonith agents. For resource agents, it is possible to use a
  short name, such as `Dummy` instead of `ocf:pacemaker:Dummy`. However, if
  several agents with the same short name are installed, the role will fail as
  it will be unable to decide which agent should be used. Therefore, it is
  recommended to use full names.
* `instance_attrs` (optional) - List of sets of the resource's instance
  attributes. Currently, only one set is supported. The exact names and values
  of attributes, as well as whether they are mandatory or not, depends on the
  resource or stonith agent.
* `meta_attrs` (optional) - List of sets of the resource's meta attributes.
  Currently, only one set is supported.
* `operations` (optional) - List of the resource's operations.
  * `action` (mandatory) - Operation action as defined by pacemaker and the
    resource or stonith agent.
  * `attrs` (mandatory) - Operation options, at least one option must be
    specified.

You may take a look at [an example](#cluster-with-fencing-and-several-resources).

#### `ha_cluster_resource_groups`

Structure, default: no resource groups

```yaml
ha_cluster_resource_groups:
  - id: "group-id"
    resource_ids:
      - "resource1-id"
      - "resource2-id"
    meta_attrs:
      - attrs:
          group_meta_attribute1_name: "group_meta_attribute1_value"
          group_meta_attribute2_name: "group_meta_attribute2_value"
```

This variable defines resource groups. The items are as follows:

* `id` (mandatory) - Id of a group.
* `resources` (mandatory) - List of the group's resources. Each resource is
  referenced by its id and the resources must be defined in
  [`ha_cluster_resource_primitives`](#ha_cluster_resource_primitives). At least
  one resource must be listed.
* `meta_attrs` (optional) - List of sets of the group's meta attributes.
  Currently, only one set is supported.

You may take a look at [an example](#cluster-with-fencing-and-several-resources).

#### `ha_cluster_resource_clones`

Structure, default: no resource clones

```yaml
ha_cluster_resource_clones:
  - resource_id: "resource-to-be-cloned"
    promotable: yes
    id: "custom-clone-id"
    meta_attrs:
      - attrs:
          clone_meta_attribute1_name: "clone_meta_attribute1_value"
          clone_meta_attribute2_name: "clone_meta_attribute2_value"
```

This variable defines resource clones. The items are as follows:

* `resource_id` (mandatory) - Resource to be cloned. The resource must be
  defined in
  [`ha_cluster_resource_primitives`](#ha_cluster_resource_primitives) or
  [`ha_cluster_resource_groups`](#ha_cluster_resource_groups).
* `promotable` (optional) - Create a promotable clone, yes or no.
* `id` (optional) - Custom id of the clone. If no id is specified, it will be
  generated. Warning will be emitted if this option is not supported by the
  cluster.
* `meta_attrs` (optional) - List of sets of the clone's meta attributes.
  Currently, only one set is supported.

You may take a look at [an example](#cluster-with-fencing-and-several-resources).

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

### Minimalistic example to create a cluster running no resources
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: "my-new-cluster"
    ha_cluster_hacluster_password: "password"

  roles:
    - linux-system-roles.ha_cluster
```

### Cluster with fencing and several resources
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: "my-new-cluster"
    ha_cluster_hacluster_password: "password"
    ha_cluster_resource_primitives:
      - id: "xvm-fencing"
        agent: "stonith:fence_xvm"
        instance_attrs:
          - attrs:
              pcmk_host_list: "node1 node2"
      - id: "simple-resource"
        agent: "ocf:pacemaker:Dummy"
      - id: "resource-with-options"
        agent: "ocf:pacemaker:Dummy"
        instance_attrs:
          - attrs:
              fake: "fake-value"
              passwd: "passwd-value"
        meta_attrs:
          - attrs:
              target-role: "Started"
              is-managed: "true"
        operations:
          - action: "start"
            attrs:
              timeout: "30"
          - action: "monitor"
            attrs:
              timeout: "5"
              interval: "20"
      - id: "dummy-1"
        agent: "ocf:pacemaker:Dummy"
      - id: "dummy-2"
        agent: "ocf:pacemaker:Dummy"
      - id: "dummy-3"
        agent: "ocf:pacemaker:Dummy"
      - id: "simple-clone"
        agent: "ocf:pacemaker:Dummy"
      - id: "clone-with-options"
        agent: "ocf:pacemaker:Dummy"
    ha_cluster_resource_groups:
      - id: "simple-group"
        resource_ids:
          - "dummy-1"
          - "dummy-2"
        meta_attrs:
          - attrs:
              target-role: "Started"
              is-managed: "true"
      - id: "cloned-group"
        resource_ids:
          - "dummy-3"
    ha_cluster_resource_clones:
      - resource_id: "simple-clone"
      - resource_id: "clone-with-options"
        promotable: yes
        id: "custom-clone-id"
        meta_attrs:
          - attrs:
              clone-max: "2"
              clone-node-max: "1"
      - resource_id: "cloned-group"
        promotable: yes

  roles:
    - linux-system-roles.ha_cluster
```

### To purge all cluster configuration, run this
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
