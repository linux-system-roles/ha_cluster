

# fedora.linux_system_roles.ha_cluster role – Manage High Availability Clustering

This role is part of the [fedora.linux_system_roles collection](https://galaxy.ansible.com/ui/repo/published/fedora/linux_system_roles/).

It is not included in `ansible-core`. To check whether it is installed, run `ansible-galaxy collection list`.

To install it use: `ansible-galaxy collection install fedora.linux_system_roles`.

To use it in a playbook, specify: `fedora.linux_system_roles.ha_cluster`.

- [Entry point `main` – Manage High Availability Clustering](#entry-point-main--manage-high-availability-clustering)

  - [Synopsis](#synopsis)

  - [Parameters](#parameters)

  - [Attributes](#attributes)

  - [Notes](#notes)

  - [Examples](#examples)

  - [Authors](#authors)

## Entry point `main` – Manage High Availability Clustering

### Synopsis

- This role manages High Availability Clustering. It configures Corosync and Pacemaker based clusters together with related components such as SBD, quorum devices, fencing, cluster resources, and constraints, and it can also export an existing cluster configuration.

- **Limitations**:

- - Compatible operating systems: RHEL 8.3 and later, Fedora 31 and later, SUSE Linux Enterprise Server 15 and 16 with the HA extension, SUSE Linux Enterprise Server for SAP Applications 15 and 16, and Azure Linux 4.

- - Systems running RHEL are expected to be registered and to have High-Availability repositories accessible, and ResilientStorage repositories accessible if using **`ha_cluster_enable_repos_resilient_storage`**.

- - The role replaces the configuration of HA Cluster on specified nodes. Any settings not specified in the role variables are lost.

- - The role is capable of configuring: single-link or multi-link cluster; Corosync transport options including compression and encryption; Corosync totem options; Corosync quorum options; Corosync quorum device (both qnetd and qdevice); SBD; Pacemaker cluster properties; stonith and resources; resource defaults and resource operation defaults; stonith levels, also known as fencing topology; resource constraints; Pacemaker node attributes; Pacemaker Access Control Lists (ACLs); node and resource utilization; and Pacemaker Alerts.

- - The role is capable of exporting existing cluster configuration: single-link or multi-link cluster; Corosync transport options including compression and encryption; Corosync totem options; Corosync quorum options; Pacemaker cluster properties; stonith and resources; resource defaults and resource operation defaults; resource constraints; stonith levels, also known as fencing topology; Pacemaker node attributes; and node and resource utilization.

- - The role can be used to configure a non-running container or VM image. However, in this mode, the role is limited to only installing cluster packages.

- **Requirements and collection requirements**:

- - The role requires the `firewall` role and the `selinux` role from the `fedora.linux_system_roles` collection if **`ha_cluster_manage_firewall`** and **`ha_cluster_manage_selinux`** are set to `true`, respectively.

- - If `ha_cluster` is a role from the `fedora.linux_system_roles` collection or from the Fedora RPM package, this requirement is already satisfied.

- - To manage `rpm-ostree` systems, you must install additional collections by running `ansible-galaxy collection install -r meta/collection-requirements.yml`.

- - For `rpm-ostree` systems, see the `README-ostree.md` file in the role.

### Parameters

| Parameter                                                          | Comments |
| ------------------------------------------------------------------ | --- |
| **ha_cluster_acls** *dictionary*                                   | This variable defines ACLs roles, users and groups. Configure the cluster property `enable-acl` to enable ACLs in the cluster. **Default:** `{}` |
| • **acl_groups** *list / elements=dictionary*                      | List of ACL groups. |
| • • **id** *string / required*                                     | ID of an ACL group. This is mandatory. |
| • • **roles** *list / elements=string*                             | List of ACL role IDs assigned to the group. |
| • **acl_roles** *list / elements=dictionary*                       | List of ACL roles. |
| • • **description** *string*                                       | Description of the ACL role. |
| • • **id** *string / required*                                     | ID of an ACL role. This is mandatory. |
| • • **permissions** *list / elements=dictionary*                   | List of ACL role permissions. |
| • • • **kind** *string / required*                                 | The access being granted. This is mandatory. **Choices:** `"read"`, `"write"`, `"deny"` |
| • • • **reference** *string*                                       | The ID of an XML element in the CIB to which the permission applies. The ID must exist. It is mandatory to specify exactly one of `xpath` or `reference`. |
| • • • **xpath** *string*                                           | An XPath specification selecting an XML element in the CIB to which the permission applies. It is mandatory to specify exactly one of `xpath` or `reference`. |
| • **acl_users** *list / elements=dictionary*                       | List of ACL users. |
| • • **id** *string / required*                                     | ID of an ACL user. This is mandatory. |
| • • **roles** *list / elements=string*                             | List of ACL role IDs assigned to the user. |
| **ha_cluster_admin_user_group** *string*                           | SUSE and SLES only. Group of the operating system user for cluster administration. This allows cluster administration with a non-root user. |
| **ha_cluster_admin_user_name** *string*                            | SUSE and SLES only. Name of the operating system user for cluster administration. This allows cluster administration with a non-root user. |
| **ha_cluster_alerts** *list / elements=dictionary*                 | This variable defines Pacemaker alerts. The role configures the cluster to call external programs to handle alerts. It is your responsibility to provide the programs and distribute them to cluster nodes. **Default:** `[]` |
| • **description** *string*                                         | Description of the alert. |
| • **id** *string / required*                                       | ID of an alert. This is mandatory. |
| • **instance_attrs** *list / elements=dictionary*                  | List of sets of the alert’s instance attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value dictionaries defining the attributes in the set. |
| • • • **name** *string / required*                                 | Name of the attribute. |
| • • • **value** *string / required*                                | Value of the attribute. |
| • **meta_attrs** *list / elements=dictionary*                      | List of sets of the alert’s meta attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value dictionaries defining the attributes in the set. |
| • • • **name** *string / required*                                 | Name of the attribute. |
| • • • **value** *string / required*                                | Value of the attribute. |
| • **path** *string / required*                                     | Path to the alert agent executable. This is mandatory. |
| • **recipients** *list / elements=dictionary*                      | List of the alert’s recipients. |
| • • **description** *string*                                       | Description of the recipient. |
| • • **id** *string*                                                | ID of the recipient. |
| • • **instance_attrs** *list / elements=dictionary*                | List of sets of the recipient’s instance attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • • **attrs** *list / elements=dictionary*                       | List of name-value dictionaries defining the attributes in the set. |
| • • • • **name** *string / required*                               | Name of the attribute. |
| • • • • **value** *string / required*                              | Value of the attribute. |
| • • **meta_attrs** *list / elements=dictionary*                    | List of sets of the recipient’s meta attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • • **attrs** *list / elements=dictionary*                       | List of name-value dictionaries defining the attributes in the set. |
| • • • • **name** *string / required*                               | Name of the attribute. |
| • • • • **value** *string / required*                              | Value of the attribute. |
| • • **value** *string / required*                                  | Value of a recipient. This is mandatory. |
| **ha_cluster_cluster_name** *string*                               | Name of the cluster. **Default:** `"my-cluster"` |
| **ha_cluster_cluster_present** *boolean*                           | If set to `true`, HA cluster is configured on the hosts according to the other variables. If set to `false`, all HA cluster configuration is purged from the target hosts. If set to `null`, HA cluster configuration is not changed. **Choices:** `false`, `true` (default) |
| **ha_cluster_cluster_properties** *list / elements=dictionary*     | List of sets of cluster properties, that is the Pacemaker cluster-wide configuration. Currently, only one set is supported, so the first set is used and the rest are ignored. **Default:** `[]` |
| • **attrs** *list / elements=dictionary*                           | List of name-value pairs defining the cluster properties in this set. |
| • • **name** *string / required*                                   | Name of a cluster property. |
| • • **value** *string*                                             | Value of the cluster property. |
| **ha_cluster_constraints_colocation** *list / elements=dictionary* | This variable defines resource colocation constraints. They tell the cluster that the location of one resource depends on the location of another one. There are two types of colocation constraints, a simple one for two resources, and a set constraint for multiple resources. **Default:** `[]` |
| • **id** *string*                                                  | ID of the constraint. If not specified, it will be autogenerated. |
| • **options** *list / elements=dictionary*                         | List of name-value dictionaries setting constraint options. |
| • • **name** *string / required*                                   | Name of the option. For `score` the option sets the weight of the constraint: positive values indicate the resources should run on the same node, negative values indicate the resources should run on different nodes, and values of `+INFINITY` and `-INFINITY` change “should” to “must”. If not specified, `score` defaults to `INFINITY`. |
| • • **value** *string / required*                                  | Value of the option. |
| • **resource_follower** *dictionary*                               | A resource that should be located relative to `resource_leader`. Mandatory for a simple colocation constraint. |
| • • **id** *string*                                                | Resource ID. This is mandatory. |
| • • **role** *string*                                              | You may limit the constraint to the specified resource role. **Choices:** `"Started"`, `"Unpromoted"`, `"Promoted"` |
| • **resource_leader** *dictionary*                                 | The cluster will decide where to put this resource first and then decide where to put `resource_follower`. Mandatory for a simple colocation constraint. |
| • • **id** *string*                                                | Resource ID. This is mandatory. |
| • • **role** *string*                                              | You may limit the constraint to the specified resource role. **Choices:** `"Started"`, `"Unpromoted"`, `"Promoted"` |
| • **resource_sets** *list / elements=dictionary*                   | List of resource sets. Mandatory for a set colocation constraint, used instead of `resource_follower` and `resource_leader`. |
| • • **options** *list / elements=dictionary*                       | List of name-value dictionaries fine-tuning how resources in the set are treated by the constraint. |
| • • • **name** *string / required*                                 | Name of the option. |
| • • • **value** *string / required*                                | Value of the option. |
| • • **resource_ids** *list / elements=string*                      | List of resources in a set. This is mandatory. |
| **ha_cluster_constraints_location** *list / elements=dictionary*   | This variable defines resource location constraints. They tell the cluster which nodes a resource can run on. Resources can be specified by their ID or by a pattern matching more resources. Nodes can be specified by their name or by a rule. **Default:** `[]` |
| • **id** *string*                                                  | ID of the constraint. If not specified, it will be autogenerated. |
| • **node** *string*                                                | Name of a node the resource should prefer or avoid. Mandatory when specifying the location by node name. Used with constraints based on a node name instead of a `rule`. |
| • **options** *list / elements=dictionary*                         | List of name-value dictionaries setting constraint options. |
| • • **name** *string / required*                                   | Name of the option. For `score` the option sets the weight of the constraint: a positive value means the resource prefers running on the node, a negative value means the resource should avoid running on the node, and `-INFINITY` means the resource must avoid running on the node. If not specified, `score` defaults to `INFINITY`. For `resource-discovery` the option fine-tunes resource discovery behavior. |
| • • **value** *string / required*                                  | Value of the option. |
| • **resource** *dictionary*                                        | Specification of a resource the constraint applies to. This is mandatory. |
| • • **id** *string*                                                | Resource ID. Mandatory when specifying a resource by ID. Mutually exclusive with `pattern`. |
| • • **pattern** *string*                                           | POSIX extended regular expression that resource IDs are matched against. Mandatory when specifying resources by a pattern. Mutually exclusive with `id`. |
| • • **role** *string*                                              | You may limit the constraint to the specified resource role. This is only used together with a `rule`. **Choices:** `"Started"`, `"Unpromoted"`, `"Promoted"` |
| • **rule** *string*                                                | Constraint rule written using pcs syntax. See the `pcs` man page, section `constraint location` for details. Mandatory when specifying the location by a rule instead of a `node`. |
| **ha_cluster_constraints_order** *list / elements=dictionary*      | This variable defines resource order constraints. They tell the cluster the order in which certain resource actions should occur. There are two types of order constraints, a simple one for two resources, and a set constraint for multiple resources. **Default:** `[]` |
| • **id** *string*                                                  | ID of the constraint. If not specified, it will be autogenerated. |
| • **options** *list / elements=dictionary*                         | List of name-value dictionaries setting constraint options, such as `kind` and `symmetrical`. |
| • • **name** *string / required*                                   | Name of the option. |
| • • **value** *string / required*                                  | Value of the option. |
| • **resource_first** *dictionary*                                  | Resource that the `resource_then` depends on. Mandatory for a simple order constraint. |
| • • **action** *string*                                            | The action that the resource must complete before an action can be initiated for the `resource_then`. **Choices:** `"start"`, `"stop"`, `"promote"`, `"demote"` |
| • • **id** *string*                                                | Resource ID. This is mandatory. |
| • **resource_sets** *list / elements=dictionary*                   | List of resource sets. Mandatory for a set order constraint, used instead of `resource_first` and `resource_then`. |
| • • **options** *list / elements=dictionary*                       | List of name-value dictionaries fine-tuning how resources in the set are treated by the constraint. |
| • • • **name** *string / required*                                 | Name of the option. |
| • • • **value** *string / required*                                | Value of the option. |
| • • **resource_ids** *list / elements=string*                      | List of resources in a set. This is mandatory. |
| • **resource_then** *dictionary*                                   | The dependent resource. Mandatory for a simple order constraint. |
| • • **action** *string*                                            | The action that the resource can execute only after the action on the `resource_first` has completed. **Choices:** `"start"`, `"stop"`, `"promote"`, `"demote"` |
| • • **id** *string*                                                | Resource ID. This is mandatory. |
| **ha_cluster_constraints_ticket** *list / elements=dictionary*     | This variable defines resource ticket constraints. They let you specify the resources depending on a certain ticket. There are two types of ticket constraints, a simple one for two resources, and a set constraint for multiple resources. **Default:** `[]` |
| • **id** *string*                                                  | ID of the constraint. If not specified, it will be autogenerated. |
| • **options** *list / elements=dictionary*                         | List of name-value dictionaries setting constraint options. |
| • • **name** *string / required*                                   | Name of the option. For `loss-policy` the option sets the action that should happen to the resource if the ticket is revoked. |
| • • **value** *string / required*                                  | Value of the option. |
| • **resource** *dictionary*                                        | Specification of a resource the constraint applies to. Mandatory for a simple ticket constraint. |
| • • **id** *string*                                                | Resource ID. This is mandatory. |
| • • **role** *string*                                              | You may limit the constraint to the specified resource role. **Choices:** `"Started"`, `"Unpromoted"`, `"Promoted"` |
| • **resource_sets** *list / elements=dictionary*                   | List of resource sets. Mandatory for a set ticket constraint, used instead of `resource`. |
| • • **options** *list / elements=dictionary*                       | List of name-value dictionaries fine-tuning how resources in the set are treated by the constraint. |
| • • • **name** *string / required*                                 | Name of the option. |
| • • • **value** *string / required*                                | Value of the option. |
| • • **resource_ids** *list / elements=string*                      | List of resources in a set. This is mandatory. |
| • **ticket** *string / required*                                   | Name of a ticket the resource depends on. This is mandatory. |
| **ha_cluster_corosync_key_src** *string*                           | Path to a Corosync authkey file, used as the authentication and encryption key for Corosync communication. It is highly recommended to have a unique value for each cluster. The key should be 256 bytes of random data. If a value is provided, it is recommended to vault encrypt it, see [Ansible vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for details. If no key is specified, a key already present on the nodes is used. If nodes do not have the same key, a key from one node is distributed to the other nodes so that all nodes have the same key. If no node has a key, a new key is generated and distributed to the nodes. If this variable is set, **`ha_cluster_regenerate_keys`** is ignored for this key. |
| **ha_cluster_enable_repos** *boolean*                              | RHEL and CentOS only. When set to `true`, enable the repositories containing the packages needed by the role. **Choices:** `false`, `true` (default) |
| **ha_cluster_enable_repos_resilient_storage** *boolean*            | RHEL and CentOS only. When set to `true`, enable the repositories containing resilient storage packages, such as `dlm` or `gfs2`. For this option to take effect, **`ha_cluster_enable_repos`** must be set to `true`. **Choices:** `false` (default), `true` |
| **ha_cluster_export_configuration** *boolean*                      | Export the existing cluster configuration. See the section on variables exported by the role for details. **Choices:** `false` (default), `true` |
| **ha_cluster_extra_packages** *list / elements=string*             | List of additional packages to be installed. By default, no extra packages are installed. Use this variable to install additional packages not installed automatically by the role, for example custom resource agents. You can specify fence agents here as well. However, **`ha_cluster_fence_agent_packages`** is preferred for that, so that its default value is overridden. **Default:** `[]` |
| **ha_cluster_fence_agent_packages** *list / elements=string*       | List of fence agent packages to install. When not set, it defaults to the fence agent packages appropriate for the managed operating system, as defined in the respective operating-system-family variable files. |
| **ha_cluster_fence_virt_key_src** *string*                         | Path to a `fence-virt` or `fence-xvm` pre-shared key file, used as the authentication key for the `fence-virt` or `fence-xvm` fence agent. If a value is provided, it is recommended to vault encrypt it, see [Ansible vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for details. If no key is specified, a key already present on the nodes is used. If nodes do not have the same key, a key from one node is distributed to the other nodes so that all nodes have the same key. If no node has a key, a new key is generated and distributed to the nodes. If this variable is set, **`ha_cluster_regenerate_keys`** is ignored for this key. If you let the role generate a new key, you are supposed to copy the key to the hypervisor of your nodes to ensure that fencing works. |
| **ha_cluster_hacluster_password** *string*                         | Password of the `hacluster` user. This user has full access to a cluster. This value is sensitive and should be treated as a secret. It is recommended to vault encrypt it, see [Ansible vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for details. This variable is optional if the role is used to configure a non-running container or VM image. **Default:** `""` |
| **ha_cluster_hacluster_qdevice_password** *string*                 | Password of the `hacluster` user on a quorum device. This user has full access to a cluster. This value is sensitive and should be treated as a secret. It is recommended to vault encrypt it, see [Ansible vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for details. This is needed only when **`ha_cluster_quorum`** is configured to use a quorum device of type `net` and the password of the `hacluster` user on the quorum device differs from **`ha_cluster_hacluster_password`**. |
| **ha_cluster_install_cloud_agents** *boolean*                      | The role automatically installs the needed HA cluster packages. However, resource and fence agents for cloud environments are not installed by default on RHEL. If you need those installed, set this variable to `true`. Alternatively, you can specify those packages in the **`ha_cluster_fence_agent_packages`** and **`ha_cluster_extra_packages`** variables. **Choices:** `false` (default), `true` |
| **ha_cluster_manage_firewall** *boolean*                           | Manage the firewall high-availability service as well as the fence-virt port. When set to `true`, the firewall high-availability service and the fence-virt port are enabled. When set to `false`, the role does not manage the firewall. **Note**. This option is limited to *adding* ports. It cannot be used to *remove* ports. To remove ports, use the firewall system role directly. **Note**. In version 1.7.5 of the role or older, the firewall was configured by default if `firewalld` was available when the role was executed. In newer versions, this does not happen unless this option is set to `true`. **Choices:** `false` (default), `true` |
| **ha_cluster_manage_selinux** *boolean*                            | Manage the ports belonging to the firewall high-availability service using the selinux role. When set to `true`, the ports belonging to the firewall high-availability service are associated with the SELinux port type `cluster_port_t`. When set to `false`, the role does not manage SELinux. **Note**. Configuring the firewall is a prerequisite for managing SELinux. If the firewall is not installed, managing SELinux policy is skipped. **Note**. This option is limited to *adding* policy. It cannot be used to *remove* policy. To remove policy, use the selinux system role directly. **Choices:** `false` (default), `true` |
| **ha_cluster_node_options** *list / elements=dictionary*           | This variable defines various settings which vary from cluster node to cluster node. Use an inventory or playbook hosts to specify which nodes form the cluster. This variable merely sets options for the specified nodes. Watchdog and SBD devices can be configured on a node to node basis using this variable. **Default:** `[]` |
| • **attributes** *list / elements=dictionary*                      | List of sets of Pacemaker node attributes for the node. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value dictionaries defining the node attributes. |
| • • • **name** *string / required*                                 | Name of the node attribute. |
| • • • **value** *string / required*                                | Value of the node attribute. |
| • **corosync_addresses** *list / elements=string*                  | List of addresses used by Corosync. All nodes must have the same number of addresses and the order of the addresses matters. |
| • **node_name** *string / required*                                | Node name. It must match a name defined for a node. See also `ha_cluster.node_name`. |
| • **pcs_address** *string*                                         | Address used by pcs to communicate with the node, it can be a name, a FQDN or an IP address. A port can be specified as well. |
| • **sbd_devices** *list / elements=string*                         | Devices to use for exchanging SBD messages and for monitoring. Defaults to an empty list if not set. Always refer to the devices using the long, stable device name under `/dev/disk/by-id/`. |
| • **sbd_watchdog** *string*                                        | Watchdog device to be used by SBD. Defaults to `/dev/watchdog` if not set. |
| • **sbd_watchdog_modules** *list / elements=string*                | Watchdog kernel modules to be loaded, which creates `/dev/watchdog*` devices. Defaults to an empty list if not set. |
| • **sbd_watchdog_modules_blocklist** *list / elements=string*      | Watchdog kernel modules to be unloaded and blocked. Defaults to an empty list if not set. |
| • **utilization** *list / elements=dictionary*                     | List of sets of the node’s utilization. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value dictionaries defining the utilization attributes. |
| • • • **name** *string / required*                                 | Name of the utilization attribute. |
| • • • **value** *integer / required*                               | Value of the utilization attribute. It must be an integer. |
| **ha_cluster_pacemaker_key_src** *string*                          | Path to a Pacemaker authkey file, used as the authentication and encryption key for Pacemaker communication. It is highly recommended to have a unique value for each cluster. The key should be 256 bytes of random data. If a value is provided, it is recommended to vault encrypt it, see [Ansible vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for details. If no key is specified, a key already present on the nodes is used. If nodes do not have the same key, a key from one node is distributed to the other nodes so that all nodes have the same key. If no node has a key, a new key is generated and distributed to the nodes. If this variable is set, **`ha_cluster_regenerate_keys`** is ignored for this key. |
| **ha_cluster_pacemaker_shell** *string*                            | The Linux Pacemaker shell to use, either `pcs` or `crmsh`. **Default:** `"pcs"` |
| **ha_cluster_pcs_permission_list** *list / elements=dictionary*    | This configures permissions to manage a cluster using pcsd. **Default:** `[{"allow_list": ["grant", "read", "write"], "name": "haclient", "type": "group"}]` |
| • **allow_list** *list / elements=string / required*               | Allowed actions for the specified user or group. `read` allows to view cluster status and settings. `write` allows to modify cluster settings except permissions and ACLs. `grant` allows to modify cluster permissions and ACLs. `full` allows unrestricted access to a cluster including adding and removing nodes and access to keys and certificates. **Choices:** `"read"`, `"write"`, `"grant"`, `"full"` |
| • **name** *string / required*                                     | User or group name. |
| • **type** *string / required*                                     | Whether `name` refers to a `user` or a `group`. **Choices:** `"user"`, `"group"` |
| **ha_cluster_pcsd_certificates** *list / elements=dictionary*      | One way to create a pcsd private key and certificate when none is present. The other way is by setting neither **`ha_cluster_pcsd_public_key_src`** and **`ha_cluster_pcsd_private_key_src`** nor this variable. If this variable is provided, the `certificate` role is used internally to create the private key and certificate for pcsd as defined. If none of the variables are provided, the `ha_cluster` role creates pcsd certificates via pcsd itself. The value of this variable is set to the `certificate_requests` variable in the `certificate` role. For more information, see the `certificate_requests` section in the `certificate` role documentation. Unless using IPA and joining the systems to an IPA domain, the `certificate` role creates self-signed certificates, so you need to explicitly configure trust, which is not currently supported by the system roles. When you set this variable, you must not set **`ha_cluster_pcsd_public_key_src`** and **`ha_cluster_pcsd_private_key_src`**. When you set this variable, **`ha_cluster_regenerate_keys`** is ignored for this certificate and key pair. **Default:** `[]` |
| **ha_cluster_pcsd_private_key_src** *string*                       | Path to the pcsd TLS private key. Pair this with `ha_cluster_pcsd_public_key_src`. If this is not specified, a certificate and key pair already present on the nodes is used. If a certificate and key pair is not present, a random new one is generated. If the private key value is provided, it is recommended to vault encrypt it, see [Ansible vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for details. If these variables are set, **`ha_cluster_regenerate_keys`** is ignored for this certificate and key pair. |
| **ha_cluster_pcsd_public_key_src** *string*                        | Path to the pcsd TLS certificate. Pair this with `ha_cluster_pcsd_private_key_src`. If this is not specified, a certificate and key pair already present on the nodes is used. If a certificate and key pair is not present, a random new one is generated. If these variables are set, **`ha_cluster_regenerate_keys`** is ignored for this certificate and key pair. |
| **ha_cluster_qnetd** *dictionary*                                  | This configures a qnetd host which can then serve as an external quorum device for clusters. Note that you cannot run qnetd on a cluster node as fencing would disrupt qnetd operation. If you set this variable to `null`, then qnetd host configuration will not be changed. **Default:** `{"present": false, "regenerate_keys": false, "start_on_boot": true}` |
| • **present** *boolean*                                            | If `true`, configure a qnetd instance on the host. If `false`, remove qnetd configuration from the host. If you set this to `true`, you must set **`ha_cluster_cluster_present`** to `false`. **Choices:** `false` (default), `true` |
| • **regenerate_keys** *boolean*                                    | Set this variable to `true` to regenerate the qnetd TLS certificate. If you regenerate the certificate, you will need to re-run the role for each cluster to connect it to the qnetd again, or run pcs manually to do that. **Choices:** `false` (default), `true` |
| • **start_on_boot** *boolean*                                      | Configures whether the qnetd should start automatically on boot. **Choices:** `false`, `true` (default) |
| **ha_cluster_quorum** *dictionary*                                 | Cluster quorum configuration. When no settings are provided, no quorum settings are applied. To regenerate the quorum device TLS certificate, set the **`ha_cluster_regenerate_keys`** variable to `true`. **Default:** `{}` |
| • **device** *dictionary*                                          | Configures the cluster to use a quorum device. By default, no quorum device is used. Quorum device options are documented in the `corosync-qdevice` man page. Generic options are `sync_timeout` and `timeout`. For model net options check the `quorum.device.net` section, and for heuristics options see the `quorum.device.heuristics` section. |
| • • **generic_options** *list / elements=dictionary*               | List of name-value dictionaries setting quorum device options which are not model specific. |
| • • • **name** *string / required*                                 | Name of the generic option. |
| • • • **value** *string / required*                                | Value of the generic option. |
| • • **heuristics_options** *list / elements=dictionary*            | List of name-value dictionaries configuring quorum device heuristics. |
| • • • **name** *string / required*                                 | Name of the heuristics option. |
| • • • **value** *string / required*                                | Value of the heuristics option. |
| • • **model** *string / required*                                  | Specifies the type of the quorum device. Currently, only `net` is supported. |
| • • **model_options** *list / elements=dictionary*                 | List of name-value dictionaries configuring the specified quorum device model. For model `net`, the options `host` and `algorithm` must be specified. You may use the `pcs-address` option to set a custom pcsd address and port to connect to the qnetd host. Otherwise, the role connects to the default pcsd port on the value of `host`. |
| • • • **name** *string / required*                                 | Name of the model option. |
| • • • **value** *string / required*                                | Value of the model option. |
| • **options** *list / elements=dictionary*                         | List of name-value dictionaries configuring quorum. Allowed options are `auto_tie_breaker`, `last_man_standing`, `last_man_standing_window` and `wait_for_all`. They are documented in the `votequorum` man page. |
| • • **name** *string / required*                                   | Name of the quorum option. |
| • • **value** *string / required*                                  | Value of the quorum option. |
| **ha_cluster_regenerate_keys** *boolean*                           | If this is set to `true`, pre-shared keys and TLS certificates are regenerated. See also **`ha_cluster_corosync_key_src`**, **`ha_cluster_pacemaker_key_src`**, **`ha_cluster_fence_virt_key_src`**, **`ha_cluster_pcsd_public_key_src`**, **`ha_cluster_pcsd_private_key_src`** and **`ha_cluster_pcsd_certificates`**. **Choices:** `false` (default), `true` |
| **ha_cluster_resource_bundles** *list / elements=dictionary*       | This variable defines resource bundles. Note that the role does not install container launch technology automatically. However, you can install it by listing appropriate packages in **`ha_cluster_extra_packages`**. Note that the role does not build and distribute container images. Please use other means to supply a fully configured container image to every node allowed to run a bundle depending on it. **Default:** `[]` |
| • **container** *dictionary*                                       | Container settings of the bundle. |
| • • **options** *list / elements=dictionary*                       | List of name-value dictionaries. Depending on the selected `type`, certain options may be required to be specified, such as `image`. |
| • • • **name** *string / required*                                 | Name of a container option. |
| • • • **value** *string*                                           | Value of the container option. |
| • • **type** *string / required*                                   | Container technology, such as `docker`, `podman` or `rkt`. This is mandatory. **Choices:** `"docker"`, `"podman"`, `"rkt"` |
| • **id** *string / required*                                       | ID of a bundle. This is mandatory. |
| • **meta_attrs** *list / elements=dictionary*                      | List of sets of the bundle meta attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value pairs defining the meta attributes in this set. |
| • • • **name** *string / required*                                 | Name of a meta attribute. |
| • • • **value** *string*                                           | Value of the meta attribute. |
| • **network_options** *list / elements=dictionary*                 | List of name-value dictionaries. When a resource is placed into a bundle, some network options may be required to be specified, such as `control-port` or `ip-range-start`. |
| • • **name** *string / required*                                   | Name of a network option. |
| • • **value** *string*                                             | Value of the network option. |
| • **port_map** *list / elements=list*                              | List of lists of name-value dictionaries defining port forwarding from the host network to the container network. Each list of name-value dictionaries holds options for one port forwarding. |
| • • **name** *string / required*                                   | Name of a port forwarding option. |
| • • **value** *string*                                             | Value of the port forwarding option. |
| • **resource_id** *string*                                         | Resource to be placed into the bundle. The resource must be defined in **`ha_cluster_resource_primitives`**. |
| • **storage_map** *list / elements=list*                           | List of lists of name-value dictionaries mapping directories on the host filesystem into the container. Each list of name-value dictionaries holds options for one directory mapping. |
| • • **name** *string / required*                                   | Name of a storage mapping option. |
| • • **value** *string*                                             | Value of the storage mapping option. |
| **ha_cluster_resource_clones** *list / elements=dictionary*        | This variable defines resource clones. **Default:** `[]` |
| • **id** *string*                                                  | Custom ID of the clone. If no ID is specified, it will be generated. A warning will be emitted if this option is not supported by the cluster. |
| • **meta_attrs** *list / elements=dictionary*                      | List of sets of the clone meta attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value pairs defining the meta attributes in this set. |
| • • • **name** *string / required*                                 | Name of a meta attribute. |
| • • • **value** *string*                                           | Value of the meta attribute. |
| • **promotable** *boolean*                                         | Create a promotable clone, `true` or `false`. **Choices:** `false`, `true` |
| • **resource_id** *string / required*                              | Resource to be cloned. This is mandatory. The resource must be defined in **`ha_cluster_resource_primitives`** or **`ha_cluster_resource_groups`**. |
| **ha_cluster_resource_defaults** *dictionary*                      | This variable defines sets of resource defaults. You can define multiple sets of the defaults and apply them to resources of specific agents using rules. Note that defaults do not apply to resources which override them with their own defined values. Only meta attributes can be specified as defaults. **Default:** `{}` |
| • **meta_attrs** *list / elements=dictionary*                      | List of sets of resource meta attribute defaults. |
| • • **attrs** *list / elements=dictionary*                         | Meta attributes applied to resources as defaults. |
| • • • **name** *string / required*                                 | Name of a meta attribute. |
| • • • **value** *string*                                           | Value of the meta attribute. |
| • • **id** *string*                                                | ID of the defaults set. If not specified, it will be autogenerated. |
| • • **rule** *string*                                              | Rule written using pcs syntax specifying when and for which resources the set applies. See the `pcs` man page, section `resource defaults set create` for details. |
| • • **score** *string*                                             | Score sets the weight of the defaults set. |
| **ha_cluster_resource_groups** *list / elements=dictionary*        | This variable defines resource groups. **Default:** `[]` |
| • **id** *string / required*                                       | ID of a group. This is mandatory. |
| • **meta_attrs** *list / elements=dictionary*                      | List of sets of the group meta attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value pairs defining the meta attributes in this set. |
| • • • **name** *string / required*                                 | Name of a meta attribute. |
| • • • **value** *string*                                           | Value of the meta attribute. |
| • **resource_ids** *list / elements=string / required*             | List of the group resources. This is mandatory. Each resource is referenced by its ID and the resources must be defined in **`ha_cluster_resource_primitives`**. At least one resource must be listed. |
| **ha_cluster_resource_operation_defaults** *dictionary*            | This variable defines sets of resource operation defaults. You can define multiple sets of the defaults and apply them to resources of specific agents and / or specific resource operations using rules. Note that defaults do not apply to resource operations which override them with their own defined values. Note that by default, the role configures resources in such a way that they define their own values for resource operations. See `copy_operations_from_agent` in **`ha_cluster_resource_primitives`** for more information. Only meta attributes can be specified as defaults. The structure is the same as for **`ha_cluster_resource_defaults`**, except that rules are described in section `resource op defaults set create` of the `pcs` man page. **Default:** `{}` |
| • **meta_attrs** *list / elements=dictionary*                      | List of sets of resource operation meta attribute defaults. |
| • • **attrs** *list / elements=dictionary*                         | Meta attributes applied to resource operations as defaults. |
| • • • **name** *string / required*                                 | Name of a meta attribute. |
| • • • **value** *string*                                           | Value of the meta attribute. |
| • • **id** *string*                                                | ID of the defaults set. If not specified, it will be autogenerated. |
| • • **rule** *string*                                              | Rule written using pcs syntax specifying when and for which resource operations the set applies. See the `pcs` man page, section `resource op defaults set create` for details. |
| • • **score** *string*                                             | Score sets the weight of the defaults set. |
| **ha_cluster_resource_primitives** *list / elements=dictionary*    | This variable defines Pacemaker resources, including stonith, configured by the role. **Default:** `[]` |
| • **agent** *string / required*                                    | Name of a resource or stonith agent, for example `ocf:pacemaker:Dummy` or `stonith:fence_xvm`. This is mandatory. It is mandatory to use the `stonith:` prefix for stonith agents. For resource agents, it is possible to use a short name, such as `Dummy` instead of `ocf:pacemaker:Dummy`. However, if several agents with the same short name are installed, the role will fail as it will be unable to decide which agent should be used. Therefore, it is recommended to use full names. |
| • **copy_operations_from_agent** *boolean*                         | Resource agents usually define default settings for resource operations, such as interval and timeout, optimized for the specific agent. If this variable is set to `true`, then those settings are copied to the resource configuration. Otherwise, clusterwide defaults will apply to the resource. You may want to set this to `false` if you also define resource operation defaults in **`ha_cluster_resource_operation_defaults`** for the resource. **Choices:** `false`, `true` (default) |
| • **id** *string / required*                                       | ID of a resource. This is mandatory. |
| • **instance_attrs** *list / elements=dictionary*                  | List of sets of the resource instance attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. The exact names and values of attributes, as well as whether they are mandatory or not, depend on the resource or stonith agent. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value pairs defining the instance attributes in this set. |
| • • • **name** *string / required*                                 | Name of an instance attribute. |
| • • • **value** *string*                                           | Value of the instance attribute. |
| • **meta_attrs** *list / elements=dictionary*                      | List of sets of the resource meta attributes. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value pairs defining the meta attributes in this set. |
| • • • **name** *string / required*                                 | Name of a meta attribute. |
| • • • **value** *string*                                           | Value of the meta attribute. |
| • **operations** *list / elements=dictionary*                      | List of the resource operations. |
| • • **action** *string / required*                                 | Operation action as defined by Pacemaker and the resource or stonith agent. This is mandatory. |
| • • **attrs** *list / elements=dictionary / required*              | Operation options. At least one option must be specified. |
| • • • **name** *string / required*                                 | Name of an operation option. |
| • • • **value** *string*                                           | Value of the operation option. |
| • **utilization** *list / elements=dictionary*                     | List of sets of the resource utilization. Currently, only one set is supported, so the first set is used and the rest are ignored. |
| • • **attrs** *list / elements=dictionary*                         | List of name-value pairs defining the utilization attributes in this set. |
| • • • **name** *string / required*                                 | Name of a utilization attribute. |
| • • • **value** *integer*                                          | Value of the utilization attribute. The value must be an integer. |
| **ha_cluster_sbd_enabled** *boolean*                               | Defines whether to use SBD. **Choices:** `false` (default), `true` |
| **ha_cluster_sbd_options** *list / elements=dictionary*            | List of name-value dictionaries specifying SBD options. See the `sbd(8`) man page, section ‘Configuration via environment’, for their description. **Default:** `[]` |
| • **name** *string / required*                                     | Name of the SBD option. Supported options are `delay-start`, which is a `false` or an integer that defaults to `false` and is documented as `SBD_DELAY_START`; `startmode`, which is a string that defaults to `always` and is documented as `SBD_STARTMODE`; `timeout-action`, which is a string that defaults to `flush,reboot` and is documented as `SBD_TIMEOUT_ACTION`; and `watchdog-timeout`, which is an integer that defaults to `5` and is documented as `SBD_WATCHDOG_TIMEOUT`. |
| • **value** *any / required*                                       | Value of the SBD option. |
| **ha_cluster_secure_logging** *boolean*                            | If `true`, suppress potentially sensitive output from tasks that handle credentials, secrets, and other sensitive data by setting `no_log` to `true` on those tasks. This prevents passwords, API tokens, preshared keys, and similar sensitive information from appearing in Ansible logs and console output. If you need to debug issues with credential handling or secret management, you can temporarily set this to `false` to see the full output from these tasks. However, be aware that this may expose sensitive information in logs, so it should only be used in development or troubleshooting scenarios. **Choices:** `false`, `true` (default) |
| **ha_cluster_start_on_boot** *boolean*                             | If set to `true`, cluster services are configured to start on boot. If set to `false`, cluster services are configured not to start on boot. **Choices:** `false`, `true` (default) |
| **ha_cluster_stonith_levels** *list / elements=dictionary*         | This variable defines stonith levels, also known as fencing topology. They configure the cluster to use multiple devices to fence nodes. You may define alternative devices in case one fails, or require multiple devices to all be executed successfully in order to consider a node successfully fenced, or even a combination of the two. Exactly one of `target`, `target_pattern`, `target_attribute` must be specified. **Default:** `[]` |
| • **level** *integer / required*                                   | Order in which to attempt the levels, from `1` to `9`. This is mandatory. Levels are attempted in ascending order until one succeeds. |
| • **resource_ids** *list / elements=string / required*             | List of stonith resources that must all be tried for this level. This is mandatory. |
| • **target** *string*                                              | Name of a node this level applies to. |
| • **target_attribute** *string*                                    | Name of a node attribute that is set for nodes this level applies to. Used together with `target_value`. |
| • **target_pattern** *string*                                      | Regular expression, as defined in POSIX, matching names of nodes this level applies to. |
| • **target_value** *string*                                        | Value of a node attribute that is set for nodes this level applies to. Used together with `target_attribute`. |
| **ha_cluster_totem** *dictionary*                                  | Corosync totem configuration. When no settings are provided, no totem settings are applied. For a list of allowed options, see `pcs -h cluster setup` or the `pcs` man page, section cluster, command setup. For a detailed description, see the `corosync.conf` man page. **Default:** `{}` |
| • **options** *list / elements=dictionary*                         | List of name-value dictionaries with totem options. |
| • • **name** *string / required*                                   | Name of the totem option. |
| • • **value** *string / required*                                  | Value of the totem option. |
| **ha_cluster_transport** *dictionary*                              | Corosync transport configuration. When no settings are provided, the defaults are used. For a list of allowed options, see `pcs -h cluster setup` or the `pcs` man page, section cluster, command setup. For a detailed description, see the `corosync.conf` man page. **Default:** `{}` |
| • **compression** *list / elements=dictionary*                     | List of name-value dictionaries configuring transport compression. Only available for the `knet` transport. |
| • • **name** *string / required*                                   | Name of the compression option. |
| • • **value** *string / required*                                  | Value of the compression option. |
| • **crypto** *list / elements=dictionary*                          | List of name-value dictionaries configuring transport encryption. Only available for the `knet` transport, where encryption is enabled by default. Encryption is always disabled with the `udp` and `udpu` transports. |
| • • **name** *string / required*                                   | Name of the crypto option. |
| • • **value** *string / required*                                  | Value of the crypto option. |
| • **links** *list / elements=list*                                 | List of lists of name-value dictionaries. Each inner list of name-value dictionaries holds options for one Corosync link. It is recommended to set the `linknumber` value for each link. Otherwise, the first list of dictionaries is assigned to the first link, the second one to the second link and so on. Only one link is supported with the `udp` and `udpu` transports. |
| • **options** *list / elements=dictionary*                         | List of name-value dictionaries with transport options. |
| • • **name** *string / required*                                   | Name of the transport option. |
| • • **value** *string / required*                                  | Value of the transport option. |
| • **type** *string*                                                | Transport type. If not specified, it defaults to `knet`. **Choices:** `"knet"`, `"udp"`, `"udpu"` |
| **ha_cluster_use_latest_packages** *boolean*                       | If set to `true`, all packages are installed with their latest version. If set to `false`, existing packages are not updated. **Choices:** `false` (default), `true` |
| **ha_cluster_zypper_patterns** *list / elements=string*            | SUSE specific. List of additional zypper patterns to be installed. By default, no patterns are installed. **Default:** `[]` |

### Attributes

| Attribute    | Support                                                                                              | Description |
| ------------ | ---------------------------------------------------------------------------------------------------- | --- |
| **platform** | **Platforms:** **Fedora**, **RHEL**, **CentOS**, **AlmaLinux**, **Rocky**, **SLES**, **Azure Linux** | Target operating systems. |

### Notes

- Nodes’ names and addresses can optionally be configured in the `ha_cluster` inventory variable. Addresses configured in **`ha_cluster_node_options`** override those configured in `ha_cluster`. If no names or addresses are configured, the play’s targets are used.

- Per-node `ha_cluster` inventory entries may set `node_name` (the name of a node in a cluster), `pcs_address` (an address used by pcs to communicate with the node, which can be a name, FQDN, or IP address and may contain a port), and `corosync_addresses` (a list of addresses used by Corosync, where all nodes must have the same number of addresses and the order of the addresses matters).

- When using SBD, watchdog and SBD devices may optionally be configured per node in the `ha_cluster` inventory variable; SBD settings defined in **`ha_cluster_node_options`** override those defined in `ha_cluster`.

- The role contains the `ha_cluster_info` module, which exports the current cluster configuration as a dictionary matching the structure of this role’s variables. Running the role with these variables recreates the same cluster.

- The exported dictionary may not be complete and manual modification is expected; most notably you must set **`ha_cluster_hacluster_password`**. Depending on the pcs version installed on managed nodes, certain variables may not be present in the export.

- Primitive resource operations are exported explicitly and `ha_cluster_resource_primitives.copy_operations_from_agent` is always set to `false`. Only the first rule is exported in **`ha_cluster_constraints_location`**, and the attribute `lifetime` is not exported at all because the role does not support it.

- To export the current cluster configuration into the `ha_cluster_facts` variable, run the role with **`ha_cluster_export_configuration`** set to `true`; this triggers the export once the role finishes configuring a cluster or a qnetd host. To trigger the export without modifying existing configuration, set **`ha_cluster_cluster_present`** and **`ha_cluster_qnetd`** to `null`, otherwise the role reconfigures the cluster and removes qnetd configuration on the specified hosts before exporting.

- **Values returned by the role**:

- - `ha_cluster_facts` — the exported current cluster configuration, populated when **`ha_cluster_export_configuration`** is `true`.

- - The following variables are present in the export:

- - **`ha_cluster_enable_repos`** — RHEL and CentOS only.

- - **`ha_cluster_enable_repos_resilient_storage`** — RHEL and CentOS only.

- - **`ha_cluster_manage_firewall`** — requires `python3-firewall` to be installed on managed nodes.

- - **`ha_cluster_manage_selinux`** — requires `python3-policycoreutils` to be installed on managed nodes.

- - **`ha_cluster_cluster_present`** — whether a cluster is configured.

- - **`ha_cluster_start_on_boot`** — whether cluster services start on boot.

- - **`ha_cluster_install_cloud_agents`** — RHEL and CentOS only.

- - **`ha_cluster_pcs_permission_list`** — pcs permissions.

- - **`ha_cluster_cluster_name`** — the cluster name.

- - **`ha_cluster_transport`** — Corosync transport configuration.

- - **`ha_cluster_totem`** — Corosync totem configuration.

- - **`ha_cluster_quorum`** — Corosync quorum configuration.

- - **`ha_cluster_node_options`** — per-node options, specifically `node_name`, `corosync_addresses`, `pcs_address`, `attributes`, and `utilization`.

- - **`ha_cluster_resource_primitives`** — primitive resource definitions.

- - **`ha_cluster_resource_groups`** — resource group definitions.

- - **`ha_cluster_resource_clones`** — resource clone definitions.

- - **`ha_cluster_resource_bundles`** — resource bundle definitions.

- - **`ha_cluster_cluster_properties`** — Pacemaker cluster properties.

- - **`ha_cluster_resource_defaults`** — resource defaults.

- - **`ha_cluster_resource_operation_defaults`** — resource operation defaults.

- - **`ha_cluster_constraints_location`** — location constraints.

- - **`ha_cluster_constraints_colocation`** — colocation constraints.

- - **`ha_cluster_constraints_order`** — order constraints.

- - **`ha_cluster_constraints_ticket`** — ticket constraints.

- - **`ha_cluster_stonith_levels`** — stonith levels, also known as fencing topology.

- - The following variables are never present in the export (consult the role documentation for the impact of these variables missing when running the role):

- - **`ha_cluster_hacluster_password`** — a mandatory variable for the role that cannot be extracted from existing clusters.

- - **`ha_cluster_hacluster_qdevice_password`** — cannot be extracted from existing clusters.

- - **`ha_cluster_fence_agent_packages`** — not exported.

- - **`ha_cluster_extra_packages`** — cannot be extracted from existing clusters.

- - **`ha_cluster_use_latest_packages`** — it is your responsibility to decide whether to upgrade cluster packages to their latest version.

- - **`ha_cluster_corosync_key_src`**, **`ha_cluster_pacemaker_key_src`**, and **`ha_cluster_fence_virt_key_src`** — these are supposed to contain paths to files with the keys; since the keys themselves are not exported, these variables are not present in the export either, and Corosync and Pacemaker keys are supposed to be unique for each cluster.

- - **`ha_cluster_pcsd_public_key_src`** and **`ha_cluster_pcsd_private_key_src`** — these are supposed to contain paths to files with the TLS certificate and private key for pcsd; since the certificate and key themselves are not exported, these variables are not present in the export either.

- - **`ha_cluster_pcsd_certificates`** — the value of this variable is set to the variable `certificate_requests` in the `certificate` role; see the `certificate` role documentation to check whether it provides any means for exporting configuration.

- - **`ha_cluster_regenerate_keys`** — it is your responsibility to decide whether to use existing keys or generate new ones.

### Examples

```yaml
# Manage an HA cluster while also configuring firewall and SELinux
- name: Manage HA cluster and firewall and selinux
  hosts: node1 node2
  vars:
    ha_cluster_manage_firewall: true
    ha_cluster_manage_selinux: true

  roles:
    - linux-system-roles.ha_cluster

# Create a minimal cluster running no resources
- name: Manage HA cluster with no resources
  hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
  roles:
    - linux-system-roles.ha_cluster

# Advanced Corosync configuration (transport, totem and quorum options)
- name: Manage HA cluster with Corosync options
  hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
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

# Configure a cluster to use SBD fencing with per-node watchdog and devices
- hosts: node1 node2
  vars:
    my_sbd_devices:
      # This variable is not used by the role directly.
      # Its purpose is to define SBD devices once so they don't need
      # to be repeated several times in the role variables.
      # Instead, variables directly used by the role refer to this variable.
      - /dev/disk/by-id/000001
      - /dev/disk/by-id/000002
      - /dev/disk/by-id/000003
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
    ha_cluster_sbd_enabled: true
    ha_cluster_sbd_options:
      - name: delay-start
        value: 'no'
      - name: startmode
        value: always
      - name: timeout-action
        value: 'flush,reboot'
      - name: watchdog-timeout
        value: 30
    ha_cluster_node_options:
      - node_name: node1
        sbd_watchdog_modules:
          - iTCO_wdt
        sbd_watchdog_modules_blocklist:
          - ipmi_watchdog
        sbd_watchdog: /dev/watchdog1
        sbd_devices: "{{ my_sbd_devices }}"
      - node_name: node2
        sbd_watchdog_modules:
          - iTCO_wdt
        sbd_watchdog_modules_blocklist:
          - ipmi_watchdog
        sbd_watchdog: /dev/watchdog1
        sbd_devices: "{{ my_sbd_devices }}"
    # Best practice for setting SBD timeouts:
    # watchdog-timeout * 2 = msgwait-timeout (set automatically)
    # msgwait-timeout * 1.2 = stonith-timeout
    ha_cluster_cluster_properties:
      - attrs:
          - name: stonith-timeout
            value: 72
    ha_cluster_resource_primitives:
      - id: fence_sbd
        agent: 'stonith:fence_sbd'
        instance_attrs:
          - attrs:
              - name: devices
                value: "{{ my_sbd_devices | join(',') }}"
              - name: pcmk_delay_base
                value: 30

  roles:
    - linux-system-roles.ha_cluster

# Create a cluster with stonith fencing and several resources
# (primitives, groups, clones and bundles)
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
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

# Create a cluster with location, colocation, order and ticket constraints
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
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

# Set up a quorum device (qnetd) host (must not be a cluster node)
- hosts: nodeQ
  vars:
    ha_cluster_cluster_present: false
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
    ha_cluster_qnetd:
      present: true

  roles:
    - linux-system-roles.ha_cluster

# Configure a cluster to use a quorum device
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
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

# Configure ACL roles, users and groups
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
    # To use an ACL role permission reference, the reference must exist in CIB.
    ha_cluster_resource_primitives:
      - id: not-for-operator
        # wokeignore:rule=dummy
        agent: 'ocf:pacemaker:Dummy'
    # ACLs must be enabled (using the enable-acl cluster property) in order to
    # be effective.
    ha_cluster_cluster_properties:
      - attrs:
          - name: enable-acl
            value: 'true'
    ha_cluster_acls:
      acl_roles:
        - id: operator
          description: HA cluster operator
          permissions:
            - kind: write
              xpath: //crm_config//nvpair[@name='maintenance-mode']
            - kind: deny
              reference: not-for-operator
        - id: administrator
          permissions:
            - kind: write
              xpath: /cib
      acl_users:
        - id: alice
          roles:
            - operator
            - administrator
        - id: bob
          roles:
            - administrator
      acl_groups:
        - id: admins
          roles:
            - administrator

  roles:
    - linux-system-roles.ha_cluster

# Configure cluster alerts and recipients
- hosts: node1 node2
  vars:
    ha_cluster_cluster_name: my-new-cluster
    ha_cluster_hacluster_password: "{{ cluster_password }}"  # vault-encrypted
    ha_cluster_alerts:
      - id: alert1
        path: /alert1/path
        description: Alert1 description
        instance_attrs:
          - attrs:
              - name: alert_attr1_name
                value: alert_attr1_value
        meta_attrs:
          - attrs:
              - name: alert_meta_attr1_name
                value: alert_meta_attr1_value
        recipients:
          - value: recipient_value
            id: recipient1
            description: Recipient1 description
            instance_attrs:
              - attrs:
                  - name: recipient_attr1_name
                    value: recipient_attr1_value
            meta_attrs:
              - attrs:
                  - name: recipient_meta_attr1_name
                    value: recipient_meta_attr1_value

  roles:
    - linux-system-roles.ha_cluster

# Purge all cluster configuration from the nodes
- hosts: node1 node2
  vars:
    ha_cluster_cluster_present: false

  roles:
    - linux-system-roles.ha_cluster
```

### Authors

- Tomas Jelinek (@tomjelinek)
