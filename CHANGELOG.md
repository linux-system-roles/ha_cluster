Changelog
=========

[1.19.2] - 2024-08-21
--------------------

### Bug Fixes

- fix: openssl is now required for password (#227)

[1.19.1] - 2024-08-20
--------------------

### Bug Fixes

- fix: Fixes for new pcs and ansible (#223)

### Other Changes

- ci: Add workflow for ci_test bad, use remote fmf plan (#221)
- ci: Fix missing slash in ARTIFACTS_URL (#222)
- docs: fix sbd_devices documentation and examples (#224)
- test: add gather_facts true for tests that need facts (#225)

[1.19.0] - 2024-08-01
--------------------

### New Features

- feat: crmsh watchdog correction, remove obsolete assert for softdog (#217)
- feat: Add alerts support (#218)

### Other Changes

- ci: Add tft plan and workflow (#214)
- ci: Update fmf plan to add a separate job to prepare managed nodes (#216)
- ci: bump sclorg/testing-farm-as-github-action from 2 to 3 (#219)

[1.18.0] - 2024-07-02
--------------------

### New Features

- feat: crmsh corosync jinja2 template rework (#212)

### Other Changes

- ci: ansible-lint action now requires absolute directory (#211)

[1.17.1] - 2024-06-11
--------------------

### Other Changes

- ci: use tox-lsr 3.3.0 which uses ansible-test 2.17 (#205)
- ci: tox-lsr 3.4.0 - fix py27 tests; move other checks to py310 (#207)
- ci: fix Python discovery with Ansible 2.17+ (#208)
- ci: Add supported_ansible_also to .ansible-lint (#209)

[1.17.0] - 2024-04-22
--------------------

### New Features

- feat: crmsh enhancements, master slave, validations (#197)
- feat: Add support for utilization (#202)

### Bug Fixes

- fix: make consistent approach for multiple node attributes sets (#201)

### Other Changes

- ci: fix internal gitlab CI (#200)

[1.16.0] - 2024-04-04
--------------------

### New Features

- feat: SLES15 enablement, HAE detection (#192)
- feat: Add support for ACL (#193)
- feat: easily install cloud agents (#194)
- feat: ha_cluster_node_options allows per-node addresses and SBD options to be set (#196)

### Other Changes

- ci: bump ansible/ansible-lint from 6 to 24 (#195)
- ci: bump mathieudutour/github-tag-action from 6.1 to 6.2 (#198)

[1.15.0] - 2024-02-13
--------------------

### New Features

- feat: crmsh workflow and SUSE support (#186)

### Other Changes

- docs: change Supported to Compatible (#188)

[1.14.0] - 2024-02-07
--------------------

### New Features

- feat: add support for configuring node attributes (#184)

### Other Changes

- ci: bump codecov/codecov-action from 3 to 4 (#182)
- ci: fix python unit test - copy pytest config to tests/unit (#183)

[1.13.5] - 2024-01-16
--------------------

### Other Changes

- ci: bump github/codeql-action from 2 to 3 (#176)
- ci: Use supported ansible-lint action; run ansible-lint against the collection (#177)
- ci: Use supported ansible-lint action; run ansible-lint against the collection (#178)
- style: followup for recent ansible-lint related changes (#179)

[1.13.4] - 2023-12-12
--------------------

### Other Changes

- test: fix jinja templates in conditionals (#173)

[1.13.3] - 2023-12-08
--------------------

### Other Changes

- refactor: get_ostree_data.sh use env shebang - remove from .sanity* (#171)

[1.13.2] - 2023-12-05
--------------------

### Bug Fixes

- fix: set sbd.service timeout based on SBD_START_DELAY (#169)

### Other Changes

- ci: bump actions/github-script from 6 to 7 (#168)

[1.13.1] - 2023-12-01
--------------------

### Bug Fixes

- fix: manage firewall on qnetd hosts (#166)

[1.13.0] - 2023-11-29
--------------------

### New Features

- feat: support for ostree systems (#159)

### Other Changes

- test: update for ansible-test-2.16 (#162)
- test: do not use true test with select (#163)

[1.12.0] - 2023-11-06
--------------------

### New Features

- feat: add an option to enable Resilient Storage rpm repository (#158)

### Bug Fixes

- fix: cast sbd option value to string (#160)

[1.11.0] - 2023-10-23
--------------------

### New Features

- feat: Add support for configuring stonith levels (#147)

### Other Changes

- build(deps): bump actions/checkout from 3 to 4 (#146)
- ci: dependabot git commit msg lint; badge ordering (#150)
- ci: use dump_packages.py callback to get packages used by role (#152)
- test: support for qdevice tls and kaptb options (#153)
- ci: tox-lsr version 3.1.1 (#156)

[1.10.1] - 2023-09-08
--------------------

### Other Changes

- docs: fix missing pronoun in readme (#141)

- ci: Add markdownlint, test_html_build, and build_docs workflows (#142)

  - markdownlint runs against README.md to avoid any issues with
    converting it to HTML
  - test_converting_readme converts README.md > HTML and uploads this test
    artifact to ensure that conversion works fine
  - build_docs converts README.md > HTML and pushes the result to the
    docs branch to publish dosc to GitHub pages site.
  - Fix markdown issues in README.md
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- docs: Make badges consistent, run markdownlint on all .md files (#143)

  - Consistently generate badges for GH workflows in README RHELPLAN-146921
  - Run markdownlint on all .md files
  - Add custom-woke-action if not used already
  - Rename woke action to Woke for a pretty badge
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- ci: Remove badges from README.md prior to converting to HTML (#144)

  - Remove thematic break after badges
  - Remove badges from README.md prior to converting to HTML
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

[1.10.0] - 2023-07-19
--------------------

### New Features

- feat: cluster and quorum can have distinct passwords (#134)

### Bug Fixes

- fix: various minor fixes (#137)
- fix: facts being gathered unnecessarily (#139)

### Other Changes

- ci: Add pull request template and run commitlint on PR title only (#133)
- ci: Rename commitlint to PR title Lint, echo PR titles from env var (#135)
- ci: test with pcs v0.11.6 (#136)
- ci: ansible-lint - ignore var-naming[no-role-prefix] (#138)

[1.9.3] - 2023-05-26
--------------------

### Other Changes

- style: address ansible-lint issues
- docs: Consistent contributing.md for all roles - allow role specific contributing.md section
- docs: fix collection requirements section
- style: fix linter issues in SBD task files
- test: update for upcoming pcs release
- refactor: update qdevice for upcoming pcs release

[1.9.2] - 2023-04-27
--------------------

### Other Changes

- test: check generated files for ansible_managed, fingerprint
- ci: Add commitlint GitHub action to ensure conventional commits with feedback

[1.9.1] - 2023-04-13
--------------------

### Other Changes

- fix ansible-lint issues with changed_when, others (#118)

[1.9.0] - 2023-04-06
--------------------

### New Features

- add support for resource and operation defaults
- Add possibility to load SBD watchdog kernel modules (#82)

### Bug Fixes

- use pcs to setup qdevice certificates if available

### Other Changes

- Add README-ansible.md to refer Ansible intro page on linux-system-roles.github.io (#115)
- Fingerprint RHEL System Role managed config files (#116)

[1.8.7] - 2023-02-08
--------------------

### New Features

- none

### Bug Fixes

- Fix stonith watchdog timeout; fix purging nodes from pacemaker (#105)

### Other Changes

- none

[1.8.6] - 2023-02-02
--------------------

### New Features

- none

### Bug Fixes

- Fence agent firewall port is restricted to x86_64 architecture. (#106)

### Other Changes

- none

[1.8.5] - 2023-01-13
--------------------

### New Features

- none

### Bug Fixes

- Not request password to be specified when purging cluster (#92)

When running the role with ha_cluster_cluster_present: false to purge
cluster passwords are not required
Add a missing bool mapping
do not set hacluster password when it is empty

### Other Changes

- ansible-lint 6.x fixes (#94)
- Add check for non-inclusive language (#97)

[1.8.4] - 2022-12-13
--------------------

### New Features

- none

### Bug Fixes

- Allow enabled SBD on disabled cluster (#81)

Currently the sbd.service will not be enabled if the cluster autostart
is disabled. This is not intended behavior as is will effectively break
the feature. We can simply remove the condition to depend on
ha_cluster_start_on_boot as on a RHEL8 system the sbd.service has a
dependencies (Before/After/PartOf/RequiredBy) to cluster related
services which make sure it is only ever started by the cluster (a
manual start is not possible).

### Other Changes

- none

[1.8.3] - 2022-12-12
--------------------

### New Features

- none

### Bug Fixes

- command warn is not supported in ansible-core 2.14

If users want to suppress the warning, users will need to configure
ansible.cfg.

- fix ownership of cib.xml

- update for upcoming pcs release

The upcoming pcs brings stricter validation for resource
configuration to prevent certain types of misconfiguration.

- tests: add qnetd cleanup

### Other Changes

- none

[1.8.2] - 2022-11-30
--------------------

### New Features

- none

### Bug Fixes

- fix qnetd check mode

### Other Changes

- none

[1.8.1] - 2022-11-14
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- long heading causes problems with md to adoc conversion

The long heading causes problems with md to adoc conversion.  Shorten
the length by using abbreviations.

[1.8.0] - 2022-11-01
--------------------

### New Features

- Use the firewall role and the selinux role from the ha_cluster role

- Introduce ha_cluster_manage_firewall to use the firewall role to
  manage the high-availability service and the fence-virt port.
  Default to false - means the firewall role is not used.

- Introduce ha_cluster_manage_selinux to use the selinux role to
  manage the ports in the high-availability service.
  Assign cluster_port_t to the high-availability service ports.
  Default to false - means the selinux role is not used.

- Add the test check task tasks/check_firewall_selinux.yml for
  verify the ports status.

Note: This pr changes the ha_cluster role's behavior slightly.
It used to configure firewall without any settings if the firewall
service is enabled. With this change made by this pr, unless
ha_cluster_manage_firewall is set to true, the firewall is not
configured.

- Use the certificate role to create the cert and the key

- Introduce a variable ha_cluster_pcsd_certificates to set the certificate_requests.

Note: Get mode of /var/lib/pcsd using the stat module and reset it
in the following file for fixing the issue "risky-file-permissions
File permissions unset or incorrect".

- add support for configuring qnetd

- add support for configuring qdevice

- qdevice and qnetd documentation

### Bug Fixes

- fix decoding variables from an Ansible vault

Workaround Ansible issue https://github.com/ansible/ansible/issues/24425
Before fix, the role was failing with the following message:
object of type 'AnsibleVaultEncryptedUnicode' has no len()

- add a test for vault-encrypted variables

- adapt tests with vault-encrypted variables for CI

- use a real temporary directory for test secrets

The tests were writing generated secrets to the directory tests/tmp
which is shared by all tests when running tests in parallel.
Instead, create a real temporary directory for these secrets for the
tests that use generated secrets.

- fix checking hacluster password

- update sbd config file template

- fix installing qnetd and pcs packages

- fix auth for qnetd host

### Other Changes

- fix linter issues

- fix qnetd setup in tests

- fix typos

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
- update to tox-lsr 2.4.0 - add support for ansible-test with docker
- CI: Add support for RHEL-9

[1.0.0] - 2021-02-17
--------------------

### Initial Release
