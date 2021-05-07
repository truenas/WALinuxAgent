#!/usr/bin/env bash


RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

script_fullpath=$1
script_name=$(basename $script_fullpath)

script_output=$(sudo env PYTHONPATH=$PYTHONPATH python "$script_fullpath" 2>&1)
script_exitcode=$?

set -e

if [[ $script_exitcode -eq 0 ]]; then
    echo -e "${GREEN}Script $script_name Succeeded${NC}"

    exit 0
fi

echo -e "${RED}Script $script_name Failed:${NC}"
echo "======================================"
echo "$script_output"
echo "======================================"

exit $script_exitcode