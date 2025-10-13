#!/bin/bash -eu

IGNORE_TESTS_FILE="${1:-""}"
echo "Ignore tests file: '$IGNORE_TESTS_FILE'"
ALL_TESTS=$(find tests/unit/ -name 'test*.py' | sort)
if [[ -n $IGNORE_TESTS_FILE ]]; then
  TEST_LIST=$(grep -v -f "$IGNORE_TESTS_FILE" <(echo -e "$ALL_TESTS"))
else
  TEST_LIST="$ALL_TESTS"
fi

echo -e "Test files:\n$TEST_LIST"

source "$PYENV_ROOT/bin/activate"
pcs --version
export PYTHONPATH="./library:./module_utils:${PYTHONPATH:-""}"
# shellcheck disable=SC2086
python -m unittest --verbose $TEST_LIST
