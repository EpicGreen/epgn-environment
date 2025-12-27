#!/bin/env bash

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 {provides}"
  exit 1
fi

if [[ "$1" == "provides" ]]; then
    SPEC_FILES=(
        "atuin"
        "bandwhich"
        "choose"
        "dua-cli"
        "procs"
        "rainfrog"
        "snitch"
        "witr"
    )
    echo "EpicGreen Enviroment provides the following packages:"
    for spec in "${SPEC_FILES[@]}"; do
        echo "    $spec"
    done
else
  echo "Usage: $0 provides"
  exit 1
fi
