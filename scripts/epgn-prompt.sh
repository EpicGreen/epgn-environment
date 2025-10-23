if [ "$USER" = "root" ]; then
    export PS1='[\[\e[1;31m\]\u\[\e[m\]@\[\e[0;35m\]\h\[\e[m\] \W]\$\[\e[0m\] '
else
    export PS1='[\[\e[1;32m\]\u\[\e[m\]@\[\e[0;35m\]\h\[\e[m\] \W]\$\[\e[0m\] '
fi
