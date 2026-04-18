LANG=en_US.utf8
if [ -f /usr/share/blesh/ble.sh ]; then
    source -- /usr/share/blesh/ble.sh
fi
eval "$(atuin init bash)" >> /dev/null
