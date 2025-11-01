#!/usr/bin/env bash

if [[ ! $1 ]]; then
    echo "Usage: $0 {create|cleanup|setup}"
    echo "certbot certonly --manual --preferred-challenges=dns --manual-auth-hook \"$0 create\" --manual-cleanup-hook \"$0 cleanup\" -d yourdomain.com -d *.yourdomain.com"
    exit 1
fi

if [[ ! $(command -v hcloud) || $(printf '%s\n' "1.54.0" "$(hcloud version | awk '{print $2}')" | sort -V | head -n1) < "1.54.0" ]]; then
    if [[ ! -f /etc/transip/auth ]]; then
        if [ "$1" = "setup" ]; then
            mkdir -p /etc/transip
            echo "Using TransIP API for DNS management."
            read -p "Please enter your TransIP API token:" API_TOKEN
            if [ -z "$API_TOKEN" ]; then
                echo "API token cannot be empty."
                exit 1
            fi
            echo "cloud_token=$API_TOKEN" | sudo tee /etc/transip/auth > /dev/null
            sudo chmod 600 /etc/transip/auth
            echo "API token saved to /etc/transip/auth."
            exit 0
        fi
        echo "TransIP API token file not found at /etc/transip/auth."
        echo "Please run '$0 setup'."
        exit 1
    fi
    API_TOKEN=$(grep 'api_token=' /etc/transip/auth | cut -d '=' -f 2)
fi

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

curl -X POST \
-H "Content-Type: application/json" \
-H "Authorization: Bearer [your JSON web token]" \
-d '{ "dnsEntry": { "name": "www","expire": 86400,"type": "A","content": "127.0.0.1" } }' \
"https://api.transip.nl/v6/domains/example.com/dns"

if [[ "$1" = "create" ]]; then
    RESPONSE=$(curl -s -X POST \
   	-H "Authorization: Bearer $API_TOKEN" \
   	-H "Content-Type: application/json" \
    -d '{ "dnsEntry": { "name": "'${RECORD}'","expire": 60,"type": "TXT","content": "\"'${CERTBOT_VALIDATION}'\"" } }' \
   	"https://api.transip.nl/v6/domains/${ZONE}/dns")
    if [[ $(echo $RESPONSE | jq -r '.error') != "null" ]]; then
        echo "Failed to create DNS record with messsage: $(echo $RESPONSE | jq -r '.error.message')"
        exit 1
    fi
exit 0
elif [[ "$1" = "cleanup" ]]; then
    RESPONSE=$(curl -s -X DELETE \
   	-H "Authorization: Bearer $API_TOKEN" \
   	-H "Content-Type: application/json" \
    -d '{ "dnsEntry": { "name": "'${RECORD}'","expire": 60,"type": "TXT","content": "\"'${CERTBOT_VALIDATION}'\"" } }' \
   	"https://api.transip.nl/v6/domains/${ZONE}/dns")
    if [[ $(echo $RESPONSE | jq -r '.error') != "null" ]]; then
        echo "Failed to cleanup DNS record with messsage: $(echo $RESPONSE | jq -r '.error.message')"
        exit 1
    fi
    exit 0
fi
