#!/bin/bash -eu
# SPDX-License-Identifier: MIT

set -eu

usage() {
  echo "Usage: $0 check|check-and-setup <clustername> <qnetd host>"
}



check_certs() {
  CLUSTER_NAME=$1
  QNETD_HOST=$2
  result=$(pcs -- quorum device check_local_qnetd_certs "$QNETD_HOST" "$CLUSTER_NAME")
  if [ "${result}x" == "certificate presentx" ]; then
    return 0
  fi
  return 1
}



if [ $# -ne 3 ]; then
  usage
  exit 1
fi

ACTION=$1
CLUSTER_NAME=$2
QNETD_HOST=$3

case "$ACTION" in
  "check")
    if check_certs "$CLUSTER_NAME" "$QNETD_HOST"; then
      echo "** certificate already present **"
    else
      echo "** certificate missing **"
    fi
  ;;
  "check-and-setup")
    if check_certs "$CLUSTER_NAME" "$QNETD_HOST"; then
      echo "** certificate already present **"
    else
      pcs -- quorum device setup_local_qnetd_certs "$QNETD_HOST" "$CLUSTER_NAME"
      echo "** certificate set up **"
    fi
  ;;
  *)
    usage
    exit 1
  ;;
esac
