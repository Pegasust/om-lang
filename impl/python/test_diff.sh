#!/usr/bin/env sh

OUT_DIR=${1:-"test_output"}


ls test_output | grep -o ".*\." | sort | uniq | while read inp; do
    echo "========= INPUT ========="
    echo "${inp}"
    wdiff -n "${OUT_DIR}/${inp}expect" "${OUT_DIR}/${inp}actual" | colordiff 
done
