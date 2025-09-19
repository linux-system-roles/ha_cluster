#!/bin/bash

source "$PYENV_ROOT/bin/activate"

TESTS_CI=$(
  for test in $(tmt tests ls --filter "tag:tier1"); do
    echo tests/tests_${test##*/}.yml;
  done | sort
)
TESTS_DIR=$(
  ls -1 tests/tests_*.yml | sort
)

echo -e "Tests found:\n$TESTS_DIR"
echo -e "\nTests defined:\n$TESTS_CI"
echo -e "\nDiff tests found vs tests defined:"
diff -u <(echo -e "$TESTS_DIR") <(echo -e "$TESTS_CI")
