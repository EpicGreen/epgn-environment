#!/usr/bin/env bash

if [[ ! $1 ]]; then
    echo "Usage: $0 {create|cleanup|setup}"
    echo "certbot certonly --manual --preferred-challenges=dns --manual-auth-hook \"$0 create\" --manual-cleanup-hook \"$0 cleanup\" -d yourdomain.com -d *.yourdomain.com"
    exit 1
fi
if [[ ! -f /etc/transip/auth ]]; then
    if [ "$1" = "setup" ]; then
        sudo mkdir -p /etc/transip
        echo "Using TransIP API for DNS management."
        read -p "Please enter your TransIP API key:" API_KEY
        if [ -z "$API_KEY" ]; then
            echo "API key cannot be empty."
            exit 1
        fi
        echo "api_key=$API_KEY" | sudo tee /etc/transip/auth > /dev/null
        sudo chmod 660 /etc/transip/auth
        echo "API key saved to /etc/transip/auth."
        exit 0
    fi
    echo "TransIP API key file not found at /etc/transip/auth."
    echo "Please run '$0 setup'."
    exit 1
fi
API_KEY=$(grep 'api_key=' /etc/transip/auth | cut -d '=' -f 2)

if [ -z "$CERTBOT_DOMAIN" ] || [ -z "$CERTBOT_VALIDATION" ]; then
    echo "This script is intended to be used as a Certbot DNS hook."
    echo "Please set the CERTBOT_DOMAIN and CERTBOT_VALIDATION environment variables."
    exit 1
fi

DOUBLEDOTTED=("uk" "au" "nz" "za" "in" "br" "ar" "jp" "kr" "pk" "lk" "tr" "il" "ka" "tz" "ug" "zw" "mx" "cn" "sg" "my" "hk" "tw" "th" "id" "ph" "bd")
EXTENTION=$(echo ${CERTBOT_DOMAIN} | rev | cut -d '.' -f 1,1 | rev)
if [[ " ${DOUBLEDOTTED[@]} " =~ " ${EXTENTION} " ]]; then
    ZONE=$(echo "${CERTBOT_DOMAIN}" | rev | cut -d '.' -f 1-3 | rev)
    SUBDOMAIN=$(echo "${CERTBOT_DOMAIN}" | sed "s/\.${ZONE}$//")
else
    ZONE=$(echo "${CERTBOT_DOMAIN}" | rev | cut -d '.' -f 1-2 | rev)
    SUBDOMAIN=$(echo "${CERTBOT_DOMAIN}" | sed "s/\.${ZONE}$//")
fi

RECORD="_acme-challenge"
if [ -z $SUBDOMAIN ]; then
    RECORD="_acme-challenge"
else
    WILDCARD=$(echo "${SUBDOMAIN}" | cut -d '.' -f 1)
    if [ "$WILDCARD" = "*" ]; then
        SUBDOMAIN=$(echo "${SUBDOMAIN}" | sed 's/^\*\.//')
    fi
    RECORD="_acme-challenge.${SUBDOMAIN}"
fi

if [[ "$1" = "create" ]]; then
    RESPONSE=$(curl -s --write-out '%{http_code}' --output /dev/null -X POST \
   	-H "Authorization: Bearer $API_KEY" \
   	-H "Content-Type: application/json" \
    -d '{ "dnsEntry": { "name": "'${RECORD}'","expire": 60,"type": "TXT","content": "\"'${CERTBOT_VALIDATION}'\"" } }' \
   	"https://api.transip.nl/v6/domains/${ZONE}/dns")
    if [[ "$RESPONSE" != 201 ]]; then
        echo "Failed to create DNS record. HTTP status code: $RESPONSE"
        exit 1
    fi
    sleep 10
    exit 0
elif [[ "$1" = "cleanup" ]]; then
    RESPONSE=$(curl -s --write-out '%{http_code}' --output /dev/null -X DELETE \
   	-H "Authorization: Bearer $API_KEY" \
   	-H "Content-Type: application/json" \
    -d '{ "dnsEntry": { "name": "'${RECORD}'","expire": 60,"type": "TXT","content": "\"'${CERTBOT_VALIDATION}'\"" } }' \
   	"https://api.transip.nl/v6/domains/${ZONE}/dns")
    if [[ "$RESPONSE" != 204 ]]; then
        echo "Failed to cleanup DNS record. HTTP status code: $RESPONSE"
        exit 1
    fi
    exit 0
fi
