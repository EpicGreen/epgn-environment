#!/usr/bin/env bash

if [[ ! -f /etc/hetzner/auth && $1 = "" ]]; then
    read -sp "Enter your Hetzner Cloud API token: " api_token
    echo
    if [ -z "$api_token" ]; then
        echo "No token provided, exiting."
        exit 1
    fi
    sudo mkdir -p /etc/hetzner
    echo api_token=$api_token | sudo tee -a /etc/hetzner/auth > /dev/null
    chmod 0600 /etc/hetzner/auth
    echo "Hetzner Cloud API token saved to /etc/hetzner/auth"
    exit 0
elif [[ ! -f /etc/hetzner/auth  && $1 != "" ]]; then
    echo "No token file found, please run the script without arguments to set up the token."
    exit 1
fi
source /etc/hetzner/auth

if [[ "$1" = "create" ]]; then
    $(hcloud zone rrset create ${CERTBOT_DOMAIN} --name _acme-challenge --type TXT --ttl 60 --record "\"${CERTBOT_VALIDATION}\"")
    if [ $? -ne 0 ]; then
        echo "Failed to create DNS record."
        exit 1
    fi
    exit 0
elif [[ "$1" = "cleanup" ]]; then
    hcloud zone rrset delete ${CERTBOT_DOMAIN} _acme-challenge TXT
    if [ $? -ne 0 ]; then
        echo "Failed to delete DNS record."
        exit 1
    fi
    exit 0
else
    echo "Usage: $0 {create|cleanup}"
    echo "certbot certonly --manual --preferred-challenges=dns --manual-auth-hook \"$0 create\" --manual-cleanup-hook \"$0 cleanup\" -d yourdomain.com -d *.yourdomain.com"
    exit 1
fi
