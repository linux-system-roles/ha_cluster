Changelog
=========

[1.7.5] - 2022-09-19
--------------------

### New Features

- none

### Bug Fixes

- only install and setup fence-virt on x86_64 hosts (#64)

fence-virt is not available for any architecture other than x86_64

### Other Changes

- replace yes, no, default with true, false, d

Use `true`, `false`, and `d` instead of `yes`, `no`, and `default`

- readme: update SBD example (#61)

[1.7.4] - 2022-07-19
--------------------

### New Features

- none

### Bug Fixes

- readme: describe limitations of udp transports (#56)

### Other Changes

- make all tests work with gather_facts: false (#52)

Ensure tests work when using ANSIBLE_GATHERING=explicit

- make min_ansible_version a string in meta/main.yml (#53)

The Ansible developers say that `min_ansible_version` in meta/main.yml
must be a `string` value like `"2.9"`, not a `float` value like `2.9`.

- Add CHANGELOG.md (#54)

[1.7.3] - 2022-06-10
--------------------

### New Features

- none

### Bug fixes

- s/ansible\_play\_hosts\_all/ansible\_play\_hosts/ where applicable

### Other Changes

- none

[1.7.2] - 2022-05-27
--------------------

### New Features

- none

### Bug fixes

- If ansible\_hostname includes '\_' the role fails with `invalid characters in salt`

### Other Changes

- Setup test vars

[1.7.1] - 2022-05-06
--------------------

### New Features

- none

### Bug Fixes

- additional fix for password\_hash salt length

### Other Changes

- bump tox-lsr version to 2.11.0; remove py37; add py310

[1.7.0] - 2022-04-13
--------------------

### New features

- Add support for SBD devices
- support gather\_facts: false; support setup-snapshot.yml
- add support for configuring bundle resources

### Bug fixes

- Pcs fixes

### Other Changes

- none

[1.6.0] - 2022-03-15
--------------------

### New features

- add support for advanced corosync configuration

### Bug Fixes

- none

### Other Changes

- bump tox-lsr version to 2.10.1

[1.5.0] - 2022-02-17
--------------------

### New features

- add SBD support

### Bug Fixes

- none

### Other Changes

- bump tox-lsr version to 2.9.1

[1.4.1] - 2022-02-01
--------------------

### New Features

- none

### Bug fixes

- fix default pcsd permissions

### Other Changes

- none

[1.4.0] - 2022-01-10
--------------------

### New features

- add support for configuring resource constraints

### Bug Fixes

- none

### Other Changes

- bump tox-lsr version to 2.8.3
- change recursive role symlink to individual role dir symlinks

[1.3.2] - 2021-11-08
--------------------

### New Features

- none

### Bug Fixes

- fix ansible-lint issues

### Other Changes

- update tox-lsr version to 2.7.1
- support python 39, ansible-core 2.12, ansible-plugin-scan

[1.3.1] - 2021-09-22
--------------------

### New features

- use firewall-cmd instead of firewalld module
- replace rhsm\_repository with subscription-manager cli
- Use the openssl command-line interface instead of the openssl module

### Bug fixes

- fix password\_hash salt length

### Other Changes

- use apt-get install -y
- use tox-lsr version 2.5.1

[1.3.0] - 2021-08-10
--------------------

### New features

- Drop support for Ansible 2.8 by bumping the Ansible version to 2.9

### Bug Fixes

- none

### Other Changes

- none

[1.2.0] - 2021-07-13
--------------------

### New features

- add pacemaker cluster properties configuration

### Bug fixes

- do not fail if openssl is not installed

### Other Changes

- none

[1.1.1] - 2021-05-27
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- Code cleanup

[1.1.0] - 2021-05-20
--------------------

### New features

- add pacemaker resources configuration

### Bug Fixes

- fix reading preshared keys
- Fix issues related to enabling repositories
- Ha\_cluster - fixing ansible-test errors

### Other Changes

- Remove python-26 environment from tox testing
- update to tox-lsr 2.4.0 - add support for ansible-test sanity with docker
- CI: Add support for RHEL-9

[1.0.0] - 2021-02-17
--------------------

### Initial Release
