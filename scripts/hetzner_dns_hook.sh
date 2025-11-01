#!/usr/bin/env bash

if [[ ! $1 ]]; then
    echo "Usage: $0 {create|cleanup|setup}"
    echo "certbot certonly --manual --preferred-challenges=dns --manual-auth-hook \"$0 create\" --manual-cleanup-hook \"$0 cleanup\" -d yourdomain.com -d *.yourdomain.com"
    exit 1
fi

USE=CLI
if [[ ! $(command -v hcloud) || $(printf '%s\n' "1.54.0" "$(hcloud version | awk '{print $2}')" | sort -V | head -n1) < "1.54.0" ]]; then
    USE=API
    if [[ ! -f /etc/hetzner/auth ]]; then
        if [ "$1" = "setup" ]; then
            mkdir -p /etc/hetzner
            echo "Using Hetzner API for DNS management."
            read -p "Please enter your Hetzner API token:" API_TOKEN
            if [ -z "$API_TOKEN" ]; then
                echo "API token cannot be empty."
                exit 1
            fi
            echo "cloud_token=$API_TOKEN" | sudo tee /etc/hetzner/auth > /dev/null
            sudo chmod 600 /etc/hetzner/auth
            echo "API token saved to /etc/hetzner/auth."
            exit 0
        fi
        echo "Hetzner Cloud API token file not found at /etc/hetzner/auth."
        echo "Please run '$0 setup'."
        exit 1
    fi
    API_TOKEN=$(grep 'cloud_token=' /etc/hetzner/auth | cut -d '=' -f 2)
else
    if [[ $(hcloud context list | wc -l) = 1 ]]; then
        if [ "$1" = "setup" ]; then
            echo "Using Hetzner hcloud cli for DNS management."
            echo "Please enter your Hetzner API token:"
            hcloud context create default
            if [ $? -ne 0 ]; then
                echo "Failed to create hcloud context."
                exit 1
            fi
            exit 0
        fi
        echo "No hcloud context found."
        echo "Please run '$0 setup'."
        exit 1
    fi
    USE=CLI
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
    RECORD="_acme-challenge.${SUBDOMAIN}"
fi

if [[ "$1" = "create" ]]; then
    if [ "$USE" = "API" ]; then
        RESPONSE=$(curl -s -X POST \
       	-H "Authorization: Bearer $API_TOKEN" \
       	-H "Content-Type: application/json" \
       	-d '{"name":"'${RECORD}'","type":"txt","ttl":60,"records":[{"value":"\"'${CERTBOT_VALIDATION}'\""}]}' \
       	"https://api.hetzner.cloud/v1/zones/${ZONE}/rrsets")
        if [[ $(echo $RESPONSE | jq -r '.error') != "null" ]]; then
            echo "Failed to create DNS record with messsage: $(echo $RESPONSE | jq -r '.error.message')"
            exit 1
        fi
    else
        $(hcloud zone rrset create ${ZONE} --name ${RECORD} --type TXT --ttl 60 --record "\"${CERTBOT_VALIDATION}\"")
        if [ $? -ne 0 ]; then
            echo "Failed to create DNS record."
            exit 1
        fi
    fi
    exit 0
elif [[ "$1" = "cleanup" ]]; then
    if [ "$USE" = "API" ]; then
        RESPONSE=$(curl -s -X DELETE \
       	-H "Authorization: Bearer $API_TOKEN" \
       		"https://api.hetzner.cloud/v1/zones/${ZONE}/rrsets/${RECORD}/TXT")
        if [[ $(echo $RESPONSE | jq -r '.error') != "null" ]]; then
            echo "Failed to cleanup DNS record with messsage: $(echo $RESPONSE | jq -r '.error.message')"
            exit 1
        fi
    else
        hcloud zone rrset delete ${ZONE} ${RECORD} TXT
        if [ $? -ne 0 ]; then
            echo "Failed to delete DNS record."
            exit 1
        fi
    fi
    exit 0
fi
