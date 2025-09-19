#!/bin/bash

TEST_NAME="${TMT_TEST_NAME##*/}"
TEST_FILE_NAME="tests_$TEST_NAME.yml"
grep "$TEST_FILE_NAME" tests/no-vault-variables.txt \
  || PLAYBOOK_EXTRA_ARGS+=" -e @tests/vars/vault-variables.yml"

echo "Test file name: $TEST_FILE_NAME"
echo "Extra playbook args: '$PLAYBOOK_EXTRA_ARGS'"

source "$PYENV_ROOT/bin/activate"
python --version
ansible --version

EXIT_CODE=0
ansible-playbook -v -i localhost, -c local \
  --vault-password-file tests/vault_pwd $PLAYBOOK_EXTRA_ARGS \
  "tests/$TEST_FILE_NAME" || EXIT_CODE=$?

# Create a directory with test artifacts
LOG_DIR="$TMT_TEST_DATA/var_log_$TEST_NAME"
mkdir "$LOG_DIR"
journalctl -x > "$LOG_DIR/journal"
cp -r /var/log/pcsd/ "$LOG_DIR" || true
cp -r /var/log/pacemaker/ "$LOG_DIR" || true
cp -r /var/log/cluster/ "$LOG_DIR" || true

exit $EXIT_CODE
