# ha_cluster
![CI Testing](https://github.com/linux-system-roles/ha_cluster/workflows/tox/badge.svg)

An Ansible role for managing High Availability Clustering.

## Limitations

* Supported OS: RHEL 8.3+, Fedora 31+
* Systems running RHEL are expected to be registered and have High-Availability
  repositories accessible.
* The role replaces the configuration of HA Cluster on specified nodes. Any
  settings not specified in the role variables will be lost.
* The role is capable of configuring:
  * single-link or multi-link cluster
  * Corosync transport options including compression and encryption
  * Corosync totem options
  * Corosync quorum options
  * Corosync quorum device (both qnetd and qdevice)
  * SBD
  * Pacemaker cluster properties
  * stonith and resources
  * resource constraints

## Requirements

The role requires the `firewall` role and the `selinux` role from the
`fedora.linux_system_roles` collection, if `ha_cluster_manage_firewall`
and `ha_cluster_manage_selinux` is set to true, respectively.
Please see also [`ha_cluster_manage_firewall`](#ha_cluster_manage_firewall)
 and [`ha_cluster_manage_selinux`](#ha_cluster_manage_selinux).

If the `ha_cluster` is a role from the `fedora.linux_system_roles`
collection or from the Fedora RPM package, the requirement is already
satisfied.

Otherwise, please run the following command line to install the collection.
```
ansible-galaxy collection install -r meta/collection-requirements.yml
```

## Role Variables

### Defined in `defaults/main.yml`

#### `ha_cluster_enable_repos`

boolean, default: `true`

RHEL and CentOS only, enable repositories containing needed packages

#### `ha_cluster_manage_firewall`

boolean, default: false

Manage the `firewall high-availability service` as well as the `fence-virt port`.
When `ha_cluster_manage_firewall` is `true`, the `firewall high-availability
service` and `fence-virt port` are enabled.
When `ha_cluster_manage_firewall` is `false`, the `ha_cluster role` does not
manage the firewall.

NOTE: `ha_cluster_manage_firewall` is limited to *adding* ports.
It cannot be used for *removing* ports.
If you want to remove ports, you will need to use the firewall system
role directly.

NOTE: The version of the `ha_cluster` role is 1.7.5 or older,
the firewall was configured by default if the firewalld was available
when the `ha_cluster` role was executed. In the newer version,
it does not happen unless `ha_cluster_manage_firewall` is set to `true`.

#### `ha_cluster_manage_selinux`

boolean, default: false

Manage the ports belonging to the `firewall high-availability service` using
the selinux role.
When `ha_cluster_manage_selinux` is `true`, the ports belonging to the
`firewall high-availability service` are associated with the selinux port type
`cluster_port_t`.
When `ha_cluster_manage_selinux` is `false`, the `ha_cluster role` does not
manage the selinux.

NOTE: The firewall configuration is prerequisite for managing selinux. If the
firewall is not installed, managing selinux policy is skipped.

NOTE: `ha_cluster_manage_selinux` is limited to *adding* policy.
It cannot be used for *removing* policy.
If you want to remove policy, you will need to use the selinux system
role directly.

#### `ha_cluster_cluster_present`

boolean, default: `true`

If set to `true`, HA cluster will be configured on the hosts according to other
variables. If set to `false`, all HA Cluster configuration will be purged from
target hosts.

#### `ha_cluster_start_on_boot`

boolean, default: `true`

If set to `true`, cluster services will be configured to start on boot. If set
to `false`, cluster services will be configured not to start on boot.

#### `ha_cluster_fence_agent_packages`

list of fence agent packages to install, default: fence-agents-all, fence-virt

#### `ha_cluster_extra_packages`

list of additional packages to be installed, default: no packages

This variable can be used to install additional packages not installed
automatically by the role, for example custom resource agents.

It is possible to specify fence agents here as well. However,
`ha_cluster_fence_agent_packages` is preferred for that, so that its default
value is overridden.

#### `ha_cluster_hacluster_password`

string, no default - must be specified

Password of the `hacluster` user. This user has full access to a cluster. It is
recommended to vault encrypt the value, see
https://docs.ansible.com/ansible/latest/user_guide/vault.html for details.

#### `ha_cluster_corosync_key_src`

path to Corosync authkey file, default: `null`

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

path to Pacemaker authkey file, default: `null`

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

#### `ha_cluster_pcsd_certificates`

If there is no pcsd private key and certificate, there are two ways to create them.

One way is by setting `ha_cluster_pcsd_certificates` variable.
Another way is by setting none of
[`ha_cluster_pcsd_public_key_src` and `ha_cluster_pcsd_private_key_src`](#ha_cluster_pcsd_public_key_src-ha_cluster_pcsd_private_key_src) and `ha_cluster_pcsd_certificates`.

If `ha_cluster_pcsd_certificates` is provided, the `certificate` role is internally
used and it creates the private key and certificate for pcsd as defined.
If none of the variables are provided, the `ha_cluster` role will create pcsd
certificates via pcsd itself. 

The value of `ha_cluster_pcsd_certificates` is set to the variable `certificate_requests`
in the `certificate` role.
For more information, see the `certificate_requests` section in the `certificate`
role documentation.

The default value is `[]`.

NOTE: The `certificate` role, unless using IPA and joining the systems to an IPA domain,
creates self-signed certificates, so you will need to explicitly configure trust,
which is not currently supported by the system roles.

NOTE: When you set `ha_cluster_pcsd_certificates`, you must not set
`ha_cluster_pcsd_public_key_src` and `ha_cluster_pcsd_private_key_src` variables.

NOTE: When you set `ha_cluster_pcsd_certificates`, `ha_cluster_regenerate_keys` is
ignored for this certificate - key pair.

#### `ha_cluster_regenerate_keys`

boolean, default: `false`

If this is set to `true`, pre-shared keys and TLS certificates will be
regenerated.
See also:
[`ha_cluster_corosync_key_src`](#ha_cluster_corosync_key_src),
[`ha_cluster_pacemaker_key_src`](#ha_cluster_pacemaker_key_src),
[`ha_cluster_fence_virt_key_src`](#ha_cluster_fence_virt_key_src),
[`ha_cluster_pcsd_public_key_src`](#ha_cluster_pcsd_public_key_src-ha_cluster_pcsd_private_key_src),
[`ha_cluster_pcsd_private_key_src`](#ha_cluster_pcsd_public_key_src-ha_cluster_pcsd_private_key_src)
[`ha_cluster_pcsd_certificates`](#ha_cluster_pcsd_certificates)

#### `ha_cluster_pcs_permission_list`

structure and default value:
```yaml
ha_cluster_pcs_permission_list:
  - type: group
    name: haclient
    allow_list:
      - grant
      - read
      - write
```

This configures permissions to manage a cluster using pcsd. The items are as
follows:

* `type` - `user` or `group`
* `name` - user or group name
* `allow_list` - Allowed actions for the specified user or group:
  * `read` - allows to view cluster status and settings
  * `write` - allows to modify cluster settings except permissions and ACLs
  * `grant` - allows to modify cluster permissions and ACLs
  * `full` - allows unrestricted access to a cluster including adding and
    removing nodes and access to keys and certificates

#### `ha_cluster_cluster_name`

string, default: `my-cluster`

Name of the cluster.

#### `ha_cluster_transport`

structure, default: no settings

```yaml
ha_cluster_transport:
  type: knet
  options:
    - name: option1_name
      value: option1_value
    - name: option2_name
      value: option2_value
  links:
    -
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
    -
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
  compression:
    - name: option1_name
      value: option1_value
    - name: option2_name
      value: option2_value
  crypto:
    - name: option1_name
      value: option1_value
    - name: option2_name
      value: option2_value
```

* `type` (optional) - Transport type: `knet`, `udp` or `udpu`. Defaults to
  `knet` if not specified.
* `options` (optional) - List of name-value dictionaries with transport options.
* `links` (optional) - List of lists of name-value dictionaries. Each list of
  name-value dictionaries holds options for one Corosync link. It is
  recommended to set `linknumber` value for each link. Otherwise, the first
  list of dictionaries is assigned to the first link, the second one to the
  second link and so on. Only one link is supported with `udp` and `udpu`
  transports.
* `compression` (optional) - List of name-value dictionaries configuring
  transport compression. Only available for `knet` transport.
* `crypto` (optional) - List of name-value dictionaries configuring transport
  encryption. Only available for `knet` transport, where encryption is enabled
  by default. Encryption is always disabled with `udp` and `udpu` transports.

For a list of allowed options, see `pcs -h cluster setup` or `pcs(8)` man page,
section 'cluster', command 'setup'. For a detailed description, see
`corosync.conf(5)` man page.

You may take a look at [an example](#advanced-corosync-configuration).

#### `ha_cluster_totem`

structure, default: no totem settings

```yaml
ha_cluster_totem:
  options:
    - name: option1_name
      value: option1_value
    - name: option2_name
      value: option2_value
```

Corosync totem configuration. For a list of allowed options, see `pcs -h
cluster setup` or `pcs(8)` man page, section 'cluster', command 'setup'. For a
detailed description, see `corosync.conf(5)` man page.

You may take a look at [an example](#advanced-corosync-configuration).

#### `ha_cluster_quorum`

structure, default: no quorum settings

```yaml
ha_cluster_quorum:
  options:
    - name: option1_name
      value: option1_value
    - name: option2_name
      value: option2_value
  device:
    model: string
    model_options:
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
    generic_options:
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
    heuristics_options:
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
```

Cluster quorum configuration. The items are as follows:

* `options` (optional) - List of name-value dictionaries configuring quorum.
  Allowed options are: `auto_tie_breaker`, `last_man_standing`,
  `last_man_standing_window`, `wait_for_all`. They are documented in
  `votequorum(5)` man page.
* `device` (optional) - Configures the cluster to use a quorum device. By
  default, no quorum device is used.
  * `model` (mandatory) - Specifies a type of the quorum device. Currently, only
    `net` is supported.
  * `model_options` (optional) - List of name-value dictionaries configuring
    the specified quorum device model. For model `net`, options `host` and
    `algorithm` must be specified.
    * You may use the `pcs-address` option to set a custom pcsd address and
      port to connect to the qnetd host. Otherwise, the role connects to
      default pcsd port on the value of `host`.
  * `generic_options` (optional) - List of name-value dictionaries setting
    quorum device options which are not model specific.
  * `heuristics_options` (optional) - List of name-value dictionaries
    configuring quorum device heuristics.

Quorum device options are documented in `corosync-qdevice(8)` man page; generic
options are `sync_timeout` and `timeout`, for model net options check the
`quorum.device.net` section, for heuristics options see the
`quorum.device.heuristics` section.

To regenerate quorum device TLS certificate, set the
[`ha_cluster_regenerate_keys`](#ha_cluster_regenerate_keys) variable to `true`.

You may take a look at [a quorum example](#advanced-corosync-configuration) and
[a quorum device example](#configuring-a-cluster-using-a-quorum-device).

#### `ha_cluster_sbd_enabled`

boolean, default: `false`

Defines whether to use SBD.

You may take a look at [an example](#configuring-cluster-to-use-sbd).

#### `ha_cluster_sbd_options`

list, default: `[]`

List of name-value dictionaries specifying SBD options. Supported options are:
`delay-start` (defaults to `false`), `startmode` (defaults to `always`),
`timeout-action` (defaults to `flush,reboot`) and `watchdog-timeout` (defaults
to `5`). See `sbd(8)` man page, section 'Configuration via environment' for
their description.

You may take a look at [an example](#configuring-cluster-to-use-sbd).

Watchdog and SBD devices are configured on a node to node basis in
[inventory](#sbd-watchdog-and-devices).

#### `ha_cluster_cluster_properties`

structure, default: no properties

```yaml
ha_cluster_cluster_properties:
  - attrs:
      - name: property1_name
        value: property1_value
      - name: property2_name
        value: property2_value
```

List of sets of cluster properties - Pacemaker cluster-wide configuration.
Currently, only one set is supported.

You may take a look at [an example](#configuring-cluster-properties).

#### `ha_cluster_resource_primitives`

structure, default: no resources

```yaml
ha_cluster_resource_primitives:
  - id: resource-id
    agent: resource-agent
    instance_attrs:
      - attrs:
          - name: attribute1_name
            value: attribute1_value
          - name: attribute2_name
            value: attribute2_value
    meta_attrs:
      - attrs:
          - name: meta_attribute1_name
            value: meta_attribute1_value
          - name: meta_attribute2_name
            value: meta_attribute2_value
    operations:
      - action: operation1-action
        attrs:
          - name: operation1_attribute1_name
            value: operation1_attribute1_value
          - name: operation1_attribute2_name
            value: operation1_attribute2_value
      - action: operation2-action
        attrs:
          - name: operation2_attribute1_name
            value: operation2_attribute1_value
          - name: operation2_attribute2_name
            value: operation2_attribute2_value
```

This variable defines Pacemaker resources (including stonith) configured by the
role. The items are as follows:

* `id` (mandatory) - ID of a resource.
* `agent` (mandatory) - Name of a resource or stonith agent, for example
  <!--- wokeignore:rule=dummy -->
  `ocf:pacemaker:Dummy` or `stonith:fence_xvm`. It is mandatory to use
  `stonith:` for stonith agents. For resource agents, it is possible to use a
  <!--- wokeignore:rule=dummy -->
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
  * `action` (mandatory) - Operation action as defined by Pacemaker and the
    resource or stonith agent.
  * `attrs` (mandatory) - Operation options, at least one option must be
    specified.

You may take a look at
[an example](#creating-a-cluster-with-fencing-and-several-resources).

#### `ha_cluster_resource_groups`

structure, default: no resource groups

```yaml
ha_cluster_resource_groups:
  - id: group-id
    resource_ids:
      - resource1-id
      - resource2-id
    meta_attrs:
      - attrs:
          - name: group_meta_attribute1_name
            value: group_meta_attribute1_value
          - name: group_meta_attribute2_name
            value: group_meta_attribute2_value
```

This variable defines resource groups. The items are as follows:

* `id` (mandatory) - ID of a group.
* `resources` (mandatory) - List of the group's resources. Each resource is
  referenced by its ID and the resources must be defined in
  [`ha_cluster_resource_primitives`](#ha_cluster_resource_primitives). At least
  one resource must be listed.
* `meta_attrs` (optional) - List of sets of the group's meta attributes.
  Currently, only one set is supported.

You may take a look at
[an example](#creating-a-cluster-with-fencing-and-several-resources).

#### `ha_cluster_resource_clones`

structure, default: no resource clones

```yaml
ha_cluster_resource_clones:
  - resource_id: resource-to-be-cloned
    promotable: true
    id: custom-clone-id
    meta_attrs:
      - attrs:
          - name: clone_meta_attribute1_name
            value: clone_meta_attribute1_value
          - name: clone_meta_attribute2_name
            value: clone_meta_attribute2_value
```

This variable defines resource clones. The items are as follows:

* `resource_id` (mandatory) - Resource to be cloned. The resource must be
  defined in
  [`ha_cluster_resource_primitives`](#ha_cluster_resource_primitives) or
  [`ha_cluster_resource_groups`](#ha_cluster_resource_groups).
* `promotable` (optional) - Create a promotable clone, `true` or `false`.
* `id` (optional) - Custom ID of the clone. If no ID is specified, it will be
  generated. Warning will be emitted if this option is not supported by the
  cluster.
* `meta_attrs` (optional) - List of sets of the clone's meta attributes.
  Currently, only one set is supported.

You may take a look at
[an example](#creating-a-cluster-with-fencing-and-several-resources).

#### `ha_cluster_resource_bundles`

structure, default: no bundle resources

```yaml
- id: bundle-id
  resource_id: resource-id
  container:
    type: container-type
    options:
      - name: container_option1_name
        value: container_option1_value
      - name: container_option2_name
        value: container_option2_value
  network_options:
      - name: network_option1_name
        value: network_option1_value
      - name: network_option2_name
        value: network_option2_value
  port_map:
    -
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
    -
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
  storage_map:
    -
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
    -
      - name: option1_name
        value: option1_value
      - name: option2_name
        value: option2_value
    meta_attrs:
      - attrs:
          - name: bundle_meta_attribute1_name
            value: bundle_meta_attribute1_value
          - name: bundle_meta_attribute2_name
            value: bundle_meta_attribute2_value
```

This variable defines resource bundles. The items are as follows:

* `id` (mandatory) - ID of a bundle.
* `resource_id` (optional) - Resource to be placed into the bundle. The
  resource must be defined in
  [`ha_cluster_resource_primitives`](#ha_cluster_resource_primitives).
* `container.type` (mandatory) - Container technology, such as `docker`,
  `podman` or `rkt`.
* `container.options` (optional) - List of name-value dictionaries. Depending
  on the selected `container.type`, certain options may be required to be
  specified, such as `image`.
* `network_options` (optional) - List of name-value dictionaries. When a
  resource is placed into a bundle, some `network_options` may be required to
  be specified, such as `control-port` or `ip-range-start`.
* `port_map` (optional) - List of lists of name-value dictionaries defining
  port forwarding from the host network to the container network. Each list of
  name-value dictionaries holds options for one port forwarding.
* `storage_map` (optional) - List of lists of name-value dictionaries mapping
  directories on the host's filesystem into the container. Each list of
  name-value dictionaries holds options for one directory mapping.
* `meta_attrs` (optional) - List of sets of the bundle's meta attributes.
  Currently, only one set is supported.

Note, that the role does not install container launch technology automatically.
However, you can install it by listing appropriate packages in
[`ha_cluster_extra_packages`](#ha_cluster_extra_packages) variable.

Note, that the role does not build and distribute container images. Please, use
other means to supply a fully configured container image to every node allowed
to run a bundle depending on it.

You may take a look at
[an example](#creating-a-cluster-with-fencing-and-several-resources).

#### `ha_cluster_constraints_location`

structure, default: no constraints

This variable defines resource location constraints. They tell the cluster
which nodes a resource can run on. Resources can be specified by their ID or a
pattern matching more resources. Nodes can be specified by their name or a
rule.

Structure for constraints with resource ID and node name:
```yaml
ha_cluster_constraints_location:
  - resource:
      id: resource-id
    node: node-name
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: option-name
        value: option-value
```
* `resource` (mandatory) - Specification of a resource the constraint applies
  to.
* `node` (mandatory) - Name of a node the resource should prefer or avoid.
* `id` (optional) - ID of the constraint. If not specified, it will be
  autogenerated.
* `options` (optional) - List of name-value dictionaries.
  * `score` - Score sets weight of the constraint.
    * Positive value means the resource prefers running on the node.
    * Negative value means the resource should avoid running on the node.
    * `-INFINITY` means the resource must avoid running on the node.
    * If not specified, `score` defaults to `INFINITY`.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

Structure for constraints with resource pattern and node name:
```yaml
ha_cluster_constraints_location:
  - resource:
      pattern: resource-pattern
    node: node-name
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: resource-discovery
        value: resource-discovery-value
```
* This is the same as the previous type, except the resource specification.
* `pattern` (mandatory) - POSIX extended regular expression resource IDs are
  matched against.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

Structure for constraints with resource ID and a rule:
```yaml
ha_cluster_constraints_location:
  - resource:
      id: resource-id
      role: resource-role
    rule: rule-string
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: resource-discovery
        value: resource-discovery-value
```
* `resource` (mandatory) - Specification of a resource the constraint applies
  to.
  * `id` (mandatory) - Resource ID.
  * `role` (optional) - You may limit the constraint to the specified resource
    role: `Started`, `Unpromoted`, `Promoted`.
* `rule` (mandatory) - Constraint rule written using pcs syntax. See `pcs(8)`
  man page, section `constraint location` for details.
* Other items have the same meaning as above.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

Structure for constraints with resource pattern and a rule:
```yaml
ha_cluster_constraints_location:
  - resource:
      pattern: resource-pattern
      role: resource-role
    rule: rule-string
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: resource-discovery
        value: resource-discovery-value
```
* This is the same as the previous type, except the resource specification.
* `pattern` (mandatory) - POSIX extended regular expression resource IDs are
  matched against.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

#### `ha_cluster_constraints_colocation`

structure, default: no constraints

This variable defines resource colocation constraints. They tell the cluster
that the location of one resource depends on the location of another one. There
are two types of colocation constraints: a simple one for two resources, and a
set constraint for multiple resources.

Structure for simple constraints:
```yaml
ha_cluster_constraints_colocation:
  - resource_follower:
      id: resource-id1
      role: resource-role1
    resource_leader:
      id: resource-id2
      role: resource-role2
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: option-name
        value: option-value
```
* `resource_follower` (mandatory) - A resource that should be located relative
  to `resource_leader`.
  * `id` (mandatory) - Resource ID.
  * `role` (optional) - You may limit the constraint to the specified resource
    role: `Started`, `Unpromoted`, `Promoted`.
* `resource_leader` (mandatory) - The cluster will decide where to put this
  resource first and then decide where to put `resource_follower`.
  * `id` (mandatory) - Resource ID.
  * `role` (optional) - You may limit the constraint to the specified resource
    role: `Started`, `Unpromoted`, `Promoted`.
* `id` (optional) - ID of the constraint. If not specified, it will be
  autogenerated.
* `options` (optional) - List of name-value dictionaries.
  * `score` (optional) - Score sets weight of the constraint.
    * Positive values indicate the resources should run on the same node.
    * Negative values indicate the resources should run on different nodes.
    * Values of `+INFINITY` and `-INFINITY` change "should" to "must".
    * If not specified, `score` defaults to `INFINITY`.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

Structure for set constraints:
```yaml
ha_cluster_constraints_colocation:
  - resource_sets:
      - resource_ids:
          - resource-id1
          - resource-id2
        options:
          - name: option-name
            value: option-value
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: option-name
        value: option-value
```
* `resource_sets` (mandatory) - List of resource sets.
  * `resource_ids` (mandatory) - List of resources in a set.
  * `options` (optional) - List of name-value dictionaries fine-tuning how
    resources in the sets are treated by the constraint.
* `id` (optional) - Same as above.
* `options` (optional) - Same as above.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

#### `ha_cluster_constraints_order`

structure, default: no constraints

This variable defines resource order constraints. They tell the cluster the
order in which certain resource actions should occur. There are two types of
order constraints: a simple one for two resources, and a set constraint for
multiple resources.

Structure for simple constraints:
```yaml
ha_cluster_constraints_order:
  - resource_first:
      id: resource-id1
      action: resource-action1
    resource_then:
      id: resource-id2
      action: resource-action2
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: option-name
        value: option-value
```
* `resource_first` (mandatory) - Resource that the `resource_then` depends on.
  * `id` (mandatory) - Resource ID.
  * `action` (optional) - The action that the resource must complete before  an
    action can be initiated for the `resource_then`. Allowed values: `start`,
    `stop`, `promote`, `demote`.
* `resource_then` (mandatory) - The dependent resource.
  * `id` (mandatory) - Resource ID.
  * `action` (optional) - The action that the resource can execute only after
    the action on the `resource_first` has completed. Allowed values: `start`,
    `stop`, `promote`, `demote`.
* `id` (optional) - ID of the constraint. If not specified, it will be
  autogenerated.
* `options` (optional) - List of name-value dictionaries.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

Structure for set constraints:
```yaml
ha_cluster_constraints_order:
  - resource_sets:
      - resource_ids:
          - resource-id1
          - resource-id2
        options:
          - name: option-name
            value: option-value
    id: constraint-id
    options:
      - name: score
        value: score-value
      - name: option-name
        value: option-value
```
* `resource_sets` (mandatory) - List of resource sets.
  * `resource_ids` (mandatory) - List of resources in a set.
  * `options` (optional) - List of name-value dictionaries fine-tuning how
    resources in the sets are treated by the constraint.
* `id` (optional) - Same as above.
* `options` (optional) - Same as above.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

#### `ha_cluster_constraints_ticket`

structure, default: no constraints

This variable defines resource ticket constraints. They let you specify the
resources depending on a certain ticket. There are two types of ticket
constraints: a simple one for two resources, and a set constraint for multiple
resources.

Structure for simple constraints:
```yaml
ha_cluster_constraints_ticket:
  - resource:
      id: resource-id
      role: resource-role
    ticket: ticket-name
    id: constraint-id
    options:
      - name: loss-policy
        value: loss-policy-value
      - name: option-name
        value: option-value
```
* `resource` (mandatory) - Specification of a resource the constraint applies
  to.
  * `id` (mandatory) - Resource ID.
  * `role` (optional) - You may limit the constraint to the specified resource
    role: `Started`, `Unpromoted`, `Promoted`.
* `ticket` (mandatory) - Name of a ticket the resource depends on.
* `id` (optional) - ID of the constraint. If not specified, it will be
  autogenerated.
* `options` (optional) - List of name-value dictionaries.
  * `loss-policy` (optional) - Action that should happen to the resource if the
    ticket is revoked.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

Structure for set constraints:
```yaml
ha_cluster_constraints_ticket:
  - resource_sets:
      - resource_ids:
          - resource-id1
          - resource-id2
        options:
          - name: option-name
            value: option-value
    ticket: ticket-name
    id: constraint-id
    options:
      - name: option-name
        value: option-value
```
* `resource_sets` (mandatory) - List of resource sets.
  * `resource_ids` (mandatory) - List of resources in a set.
  * `options` (optional) - List of name-value dictionaries fine-tuning how
    resources in the sets are treated by the constraint.
* `ticket` (mandatory) - Same as above.
* `id` (optional) - Same as above.
* `options` (optional) - Same as above.

You may take a look at
[an example](#creating-a-cluster-with-resource-constraints).

#### `ha_cluster_qnetd`

structure and default value:
```yaml
ha_cluster_qnetd:
  present: boolean
  start_on_boot: boolean
  regenerate_keys: boolean
```

This configures a qnetd host which can then serve as an external quorum device
for clusters. The items are as follows:

* `present` (optional) - If `true`, configure a qnetd instance on the host. If
  `false`, remove qnetd configuration from the host. Defaults to `false`. If
  you set this to `true`, you must set
  [`ha_cluster_cluster_present`](#ha_cluster_cluster_present) to `false`.
* `start_on_boot` (optional) - Configures whether the qnetd should start
  automatically on boot. Defaults to `true`.
* `regenerate_keys` (optional) - Set this variable to `true` to regenerate
  qnetd TLS certificate. If you regenerate the certificate, you will need to
  re-run the role for each cluster to connect it to the qnetd again or run pcs
  manually to do that.

Note that you cannot run qnetd on a cluster node as fencing would disrupt qnetd
operation.

You may take a look at [an
example](#configuring-a-cluster-using-a-quorum-device).

### Inventory

#### Nodes' names and addresses
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

#### SBD watchdog and devices
When using SBD, you may optionally configure watchdog and SBD devices for each
node in inventory. Even though all SBD devices must be shared to and accessible
from all nodes, each node may use different names for the devices. Watchdog may
be different for each node as well. See also [SBD
variables](#ha_cluster_sbd_enabled).

Example inventory with targets `node1` and `node2`:
```yaml
all:
  hosts:
    node1:
      ha_cluster:
        sbd_watchdog: /dev/watchdog2
        sbd_devices:
          - /dev/vdx
          - /dev/vdy
    node2:
      ha_cluster:
        sbd_watchdog: /dev/watchdog1
        sbd_devices:
          - /dev/vdw
          - /dev/vdz
```

* `sbd_watchdog` (optional) - Watchdog device to be used by SBD. Defaults to
  `/dev/watchdog` if not set.
* `sbd_devices` (optional) - Devices to use for exchanging SBD messages and for
  monitoring. Defaults to empty list if not set.

## Example Playbooks

Following examples show what the structure of the role variables looks like.
They are not guides or best practices for configuring a cluster.

### Configuring firewall and selinux using each role

To run `ha_cluster` properly, the `ha_cluster` ports need to be configured
for `firewalld` and the `SELinux` policy as shown in this example. Although
they are omitted in each example playbook, we highly recommend to set them
to `true` in your playbooks using the `ha_cluster` role.

```yaml
- hosts: node1 node2
  vars:
    ha_cluster_manage_firewall: true
    ha_cluster_manage_selinux: true

  roles:
    - linux-system-roles.ha_cluster
```

### Creating pcsd TLS cert and key files using the `certificate` role

This example creates self-signed pcsd certificate and private key files
in /var/lib/pcsd with the file name FILENAME.crt and FILENAME.key, respectively.

```yaml
- hosts: node1 node2
  vars:
    ha_cluster_pcsd_certificates:
      - name: FILENAME
        common_name: "{{ ansible_hostname }}"
        ca: self-sign
  roles:
    - linux-system-roles.ha_cluster
```

### Creating a cluster running no resources
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password

  roles:
    - linux-system-roles.ha_cluster
```

### Advanced Corosync configuration
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password
    ha_cluster_transport:
      type: knet
      options:
        - name: ip_version
          value: ipv4-6
        - name: link_mode
          value: active
      links:
        -
          - name: linknumber
            value: 1
          - name: link_priority
            value: 5
        -
          - name: linknumber
            value: 0
          - name: link_priority
            value: 10
      compression:
        - name: level
          value: 5
        - name: model
          value: zlib
      crypto:
        - name: cipher
          value: none
        - name: hash
          value: none
    ha_cluster_totem:
      options:
        - name: block_unlisted_ips
          value: 'yes'
        - name: send_join
          value: 0
    ha_cluster_quorum:
      options:
        - name: auto_tie_breaker
          value: 1
        - name: wait_for_all
          value: 1

  roles:
    - linux-system-roles.ha_cluster
```

### Configuring cluster to use SBD
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password
    ha_cluster_sbd_enabled: true
    ha_cluster_sbd_options:
      - name: delay-start
        value: 'no'
      - name: startmode
        value: always
      - name: timeout-action
        value: 'flush,reboot'
      - name: watchdog-timeout
        value: 5
    #  if you need to set stonith-watchdog-timeout property as well:
    ha_cluster_cluster_properties:
      - attrs:
          - name: stonith-watchdog-timeout
            value: 10

  roles:
    - linux-system-roles.ha_cluster
```

### Configuring cluster properties
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password
    ha_cluster_cluster_properties:
      - attrs:
          - name: stonith-enabled
            value: 'true'
          - name: no-quorum-policy
            value: stop

  roles:
    - linux-system-roles.ha_cluster
```

### Creating a cluster with fencing and several resources
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password
    ha_cluster_resource_primitives:
      - id: xvm-fencing
        agent: 'stonith:fence_xvm'
        instance_attrs:
          - attrs:
              - name: pcmk_host_list
                value: node1 node2
      - id: simple-resource
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: resource-with-options
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
        instance_attrs:
          - attrs:
              - name: fake
                value: fake-value
              - name: passwd
                value: passwd-value
        meta_attrs:
          - attrs:
              - name: target-role
                value: Started
              - name: is-managed
                value: 'true'
        operations:
          - action: start
            attrs:
              - name: timeout
                value: '30s'
          - action: monitor
            attrs:
              - name: timeout
                value: '5'
              - name: interval
                value: '1min'
      - id: example-1
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: example-2
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: example-3
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: simple-clone
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: clone-with-options
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: bundled-resource
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
    ha_cluster_resource_groups:
      - id: simple-group
        resource_ids:
          - example-1
          - example-2
        meta_attrs:
          - attrs:
              - name: target-role
                value: Started
              - name: is-managed
                value: 'true'
      - id: cloned-group
        resource_ids:
          - example-3
    ha_cluster_resource_clones:
      - resource_id: simple-clone
      - resource_id: clone-with-options
        promotable: true
        id: custom-clone-id
        meta_attrs:
          - attrs:
              - name: clone-max
                value: '2'
              - name: clone-node-max
                value: '1'
      - resource_id: cloned-group
        promotable: true
    ha_cluster_resource_bundles:
      - id: bundle-with-resource
        resource-id: bundled-resource
        container:
          type: podman
          options:
            - name: image
              value: my:image
        network_options:
          - name: control-port
            value: 3121
        port_map:
          -
            - name: port
              value: 10001
          -
            - name: port
              value: 10002
            - name: internal-port
              value: 10003
        storage_map:
          -
            - name: source-dir
              value: /srv/daemon-data
            - name: target-dir
              value: /var/daemon/data
          -
            - name: source-dir-root
              value: /var/log/pacemaker/bundles
            - name: target-dir
              value: /var/log/daemon
        meta_attrs:
          - attrs:
              - name: target-role
                value: Started
              - name: is-managed
                value: 'true'

  roles:
    - linux-system-roles.ha_cluster
```

### Creating a cluster with resource constraints
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password
    # In order to use constraints, we need resources the constraints will apply
    # to.
    ha_cluster_resource_primitives:
      - id: xvm-fencing
        agent: 'stonith:fence_xvm'
        instance_attrs:
          - attrs:
              - name: pcmk_host_list
                value: node1 node2
      - id: example-1
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: example-2
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: example-3
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: example-4
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: example-5
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
      - id: example-6
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
    # location constraints
    ha_cluster_constraints_location:
      # resource ID and node name
      - resource:
          id: example-1
        node: node1
        options:
          - name: score
            value: 20
      # resource pattern and node name
      - resource:
          pattern: example-\d+
        node: node1
        options:
          - name: score
            value: 10
      # resource ID and rule
      - resource:
          id: example-2
        rule: '#uname eq node2 and date in_range 2022-01-01 to 2022-02-28'
      # resource pattern and rule
      - resource:
          pattern: example-\d+
        rule: node-type eq weekend and date-spec weekdays=6-7
    # colocation constraints
    ha_cluster_constraints_colocation:
      # simple constraint
      - resource_leader:
          id: example-3
        resource_follower:
          id: example-4
        options:
          - name: score
            value: -5
      # set constraint
      - resource_sets:
          - resource_ids:
              - example-1
              - example-2
          - resource_ids:
              - example-5
              - example-6
            options:
              - name: sequential
                value: "false"
        options:
          - name: score
            value: 20
    # order constraints
    ha_cluster_constraints_order:
      # simple constraint
      - resource_first:
          id: example-1
        resource_then:
          id: example-6
        options:
          - name: symmetrical
            value: "false"
      # set constraint
      - resource_sets:
          - resource_ids:
              - example-1
              - example-2
            options:
              - name: require-all
                value: "false"
              - name: sequential
                value: "false"
          - resource_ids:
              - example-3
          - resource_ids:
              - example-4
              - example-5
            options:
              - name: sequential
                value: "false"
    # ticket constraints
    ha_cluster_constraints_ticket:
      # simple constraint
      - resource:
          id: example-1
        ticket: ticket1
        options:
          - name: loss-policy
            value: stop
      # set constraint
      - resource_sets:
          - resource_ids:
              - example-3
              - example-4
              - example-5
        ticket: ticket2
        options:
          - name: loss-policy
            value: fence

  roles:
    - linux-system-roles.ha_cluster
```

### Configuring a cluster using a quorum device

#### Configuring a quorum device
Before you can add a quorum device to a cluster, you need to set the device up.
This is only needed to be done once for each quorum device. Once it has been
set up, you can use a quorom device in any number of clusters.

Note that you cannot run a quorum device on a cluster node.

```yaml
- hosts: nodeQ
  vars:
    ha_cluster_cluster_present: false
    ha_cluster_hacluster_password: password
    ha_cluster_qnetd:
      present: true

  roles:
    - linux-system-roles.ha_cluster
```

#### Configuring a cluster to use a quorum device
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password
    ha_cluster_quorum:
      device:
        model: net
        model_options:
          - name: host
            value: nodeQ
          - name: algorithm
            value: lms

  roles:
    - linux-system-roles.ha_cluster
```

### Purging all cluster configuration
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_present: false

  roles:
    - linux-system-roles.ha_cluster
```

## License

MIT

## Author Information

Tomas Jelinek
