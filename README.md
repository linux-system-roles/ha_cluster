# ha_cluster
![CI Testing](https://github.com/linux-system-roles/ha_cluster/workflows/tox/badge.svg)

An Ansible role for managing High Availability Clustering.

## Limitations

* Supported OS: RHEL 8.3+, Fedora 31+
* Systems running RHEL are expected to be registered and have High-Availability
  repositories accessible.
* The role replaces the configuration of HA Cluster on specified nodes. Any
  settings not specified in the role variables will be lost.
* For now, the role is capable of configuring:
  * a basic corosync cluster
  * pacemaker cluster properties
  * stonith and resources
  * resource constraints

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

structure and default value:
```yaml
ha_cluster_pcs_permission_list:
  - type: group
    name: hacluster
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

List of sets of cluster properties - pacemaker cluster-wide configuration.
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

This variable defines pacemaker resources (including stonith) configured by the
role. The items are as follows:

* `id` (mandatory) - ID of a resource.
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
    promotable: yes
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
* `promotable` (optional) - Create a promotable clone, yes or no.
* `id` (optional) - Custom ID of the clone. If no ID is specified, it will be
  generated. Warning will be emitted if this option is not supported by the
  cluster.
* `meta_attrs` (optional) - List of sets of the clone's meta attributes.
  Currently, only one set is supported.

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


## Example Playbooks

### Creating a cluster running no resources
```yaml
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: password

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
        agent: 'ocf:pacemaker:Dummy'
      - id: resource-with-options
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
      - id: dummy-1
        agent: 'ocf:pacemaker:Dummy'
      - id: dummy-2
        agent: 'ocf:pacemaker:Dummy'
      - id: dummy-3
        agent: 'ocf:pacemaker:Dummy'
      - id: simple-clone
        agent: 'ocf:pacemaker:Dummy'
      - id: clone-with-options
        agent: 'ocf:pacemaker:Dummy'
    ha_cluster_resource_groups:
      - id: simple-group
        resource_ids:
          - dummy-1
          - dummy-2
        meta_attrs:
          - attrs:
              - name: target-role
                value: Started
              - name: is-managed
                value: 'true'
      - id: cloned-group
        resource_ids:
          - dummy-3
    ha_cluster_resource_clones:
      - resource_id: simple-clone
      - resource_id: clone-with-options
        promotable: yes
        id: custom-clone-id
        meta_attrs:
          - attrs:
              - name: clone-max
                value: '2'
              - name: clone-node-max
                value: '1'
      - resource_id: cloned-group
        promotable: yes

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
      - id: dummy-1
        agent: 'ocf:pacemaker:Dummy'
      - id: dummy-2
        agent: 'ocf:pacemaker:Dummy'
      - id: dummy-3
        agent: 'ocf:pacemaker:Dummy'
      - id: dummy-4
        agent: 'ocf:pacemaker:Dummy'
      - id: dummy-5
        agent: 'ocf:pacemaker:Dummy'
      - id: dummy-6
        agent: 'ocf:pacemaker:Dummy'
    # location constraints
    ha_cluster_constraints_location:
      # resource ID and node name
      - resource:
          id: dummy-1
        node: node1
        options:
          - name: score
            value: 20
      # resource pattern and node name
      - resource:
          pattern: dummy-\d+
        node: node1
        options:
          - name: score
            value: 10
      # resource ID and rule
      - resource:
          id: dummy-2
        rule: '#uname eq node2 and date in_range 2022-01-01 to 2022-02-28'
      # resource pattern and rule
      - resource:
          pattern: dummy-\d+
        rule: node-type eq weekend and date-spec weekdays=6-7
    # colocation constraints
    ha_cluster_constraints_colocation:
      # simple constraint
      - resource_leader:
          id: dummy-3
        resource_follower:
          id: dummy-4
        options:
          - name: score
            value: -5
      # set constraint
      - resource_sets:
          - resource_ids:
              - dummy-1
              - dummy-2
          - resource_ids:
              - dummy-5
              - dummy-6
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
          id: dummy-1
        resource_then:
          id: dummy-6
        options:
          - name: symmetrical
            value: "false"
      # set constraint
      - resource_sets:
          - resource_ids:
              - dummy-1
              - dummy-2
            options:
              - name: require-all
                value: "false"
              - name: sequential
                value: "false"
          - resource_ids:
              - dummy-3
          - resource_ids:
              - dummy-4
              - dummy-5
            options:
              - name: sequential
                value: "false"
    # ticket constraints
    ha_cluster_constraints_ticket:
      # simple constraint
      - resource:
          id: dummy-1
        ticket: ticket1
        options:
          - name: loss-policy
            value: stop
      # set constraint
      - resource_sets:
          - resource_ids:
              - dummy-3
              - dummy-4
              - dummy-5
        ticket: ticket2
        options:
          - name: loss-policy
            value: fence

  roles:
    - linux-system-roles.ha_cluster
```

### Purging all cluster configuration
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
