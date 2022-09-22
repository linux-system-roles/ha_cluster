#!/bin/bash -eu
# SPDX-License-Identifier: MIT

set -eu

usage() {
  echo "Usage: $0 check|check-and-setup <clustername> <qnetd host>"
}



token() {
  HOST=$1
  # The node runs pcs which depends on python3, so we can safely use it.
  TOKEN=$(python3 -c "import json; print(json.load(open('/var/lib/pcsd/known-hosts'))['known_hosts']['${HOST}']['token'])")
  echo "$TOKEN"
}



pcs_addr() {
  HOST=$1
  # The node runs pcs which depends on python3, so we can safely use it.
  ADDR=$(python3 -c "import json; dest = json.load(open('/var/lib/pcsd/known-hosts'))['known_hosts']['${HOST}']['dest_list'][0]; da = dest['addr']; a = '[' + da + ']' if ':' in da else da; print(a + ':' + str(dest['port']));")
  echo "$ADDR"
}



check_certs() {
  CLUSTER_NAME=$1
  QNETD_HOST=$2
  CERT_DB=/etc/corosync/qdevice/net/nssdb/

  echo "Checking if qdevice certs are present"
  if [ 1 -ne "$(certutil -d "$CERT_DB" -L | grep -c 'QNet CA')" ]; then
    return 1
  fi
  if [ 1 -ne "$(certutil -d "$CERT_DB" -L | grep -c 'Cluster Cert')" ]; then
    return 1
  fi

  echo "Checking cluster name '${CLUSTER_NAME}' in existing certificates"
  EXISTING_NAME=$(certutil -d "$CERT_DB" -L -n 'Cluster Cert' | sed -e 's/\s*Subject: "CN=\(.*\)"/\1/ p ; d')
  echo "Found name: '$EXISTING_NAME'"
  if [ "${CLUSTER_NAME}x" != "${EXISTING_NAME}x" ]; then
    return 1
  fi

  echo "Getting pcs token and address for '${QNETD_HOST}'"
  TOKEN=$(token "$QNETD_HOST")
  PCS_ADDR=$(pcs_addr "$QNETD_HOST")
  # use --insecure to support pcsd self-signed certificates
  CURL="curl --insecure --cookie token=${TOKEN}"

  echo "Downloading qnetd CA certificate from '${PCS_ADDR}'"
  QNETD_CA=$($CURL "https://${PCS_ADDR}/remote/qdevice_net_get_ca_certificate" | base64 -d | sed -e '/^-----BEGIN CERTIFICATE-----$/,/^-----END CERTIFICATE-----$/ { p } ; d' | tr -d '\n\r')

  echo "Exporting qdevice CA certificate"
  TEMP=$(mktemp --suffix=_ha_cluster_qdevice)
  pk12util -o "$TEMP" -d "$CERT_DB" -n 'Cluster Cert' -W ''

  echo "Extracting qdevice CA certificate"
  QDEVICE_CA=$(openssl pkcs12 -in "$TEMP" -cacerts -nokeys -passin pass: | sed -e '/^-----BEGIN CERTIFICATE-----$/,/^-----END CERTIFICATE-----$/ { p } ; d' | tr -d '\n\r')
  rm "$TEMP"

  echo "Comparing CA certificate"
  if [ "${QDEVICE_CA}x" != "${QNETD_CA}x" ]; then
    return 1
  fi

  return 0
}



setup_certs() {
  CLUSTER_NAME=$1
  QNETD_HOST=$2

  echo "Getting pcs token and address for '${QNETD_HOST}'"
  TOKEN=$(token "$QNETD_HOST")
  PCS_ADDR=$(pcs_addr "$QNETD_HOST")
  # use --insecure to support pcsd self-signed certificates
  CURL="curl --insecure --cookie token=${TOKEN}"

  echo "Downloading qnetd CA certificate from '${PCS_ADDR}' and initializing qdevice certificate storage"
  $CURL "https://${PCS_ADDR}/remote/qdevice_net_get_ca_certificate" | pcs -- qdevice net-client setup

  echo "Creating a certificate request for cluster '${CLUSTER_NAME}'"
  corosync-qdevice-net-certutil -r -n "$CLUSTER_NAME"
  DATA="$(base64 --wrap 0 /etc/corosync/qdevice/net/nssdb/qdevice-net-node.crq)"

  echo "Asking qnetd to sign the certificate request"
  TEMP=$(mktemp --suffix=_ha_cluster_qdevice)
  $CURL -X POST --data-urlencode "cluster_name=${CLUSTER_NAME}" --data-urlencode "certificate_request=${DATA}" "https://${PCS_ADDR}/remote/qdevice_net_sign_node_certificate" | base64 -d > "$TEMP"

  echo "Converting the signed certificate"
  corosync-qdevice-net-certutil -M -c "$TEMP"
  rm "$TEMP"

  echo "Importing the certificate to qdevice certificate storage"
  base64 --wrap 0 /etc/corosync/qdevice/net/nssdb/qdevice-net-node.p12 | pcs -- qdevice net-client import-certificate
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
      setup_certs "$CLUSTER_NAME" "$QNETD_HOST"
      echo "** certificate set up **"
    fi
  ;;
  *)
    usage
    exit 1
  ;;
esac
