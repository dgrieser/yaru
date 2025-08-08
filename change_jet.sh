#!/bin/bash

APP="$(basename "${0}")"

jet_new="#2C3540"

grep -lr '$jet: #181818;' . | grep -v '^\./\.git'

grep -lIr '$jet: #181818;' . | grep -v "^\./\.git" | grep -v "^./${APP}$" | while IFS= read -r file; do
    echo "Replacing content in ${file}..."
    sed -i -E 's/#181818/'"${jet_new}"'/g' "${file}"
done
