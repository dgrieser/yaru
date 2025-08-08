#!/bin/bash

echo "Renaming folders..." 1>&2
find . -type d -iname "*yaru*" | grep -v "^./.git" | while IFS= read -r dir; do
    mv -v "${dir}" "$(echo "${dir}" | sed -E 's/(yaru)/\1dave/ig')"
done

echo "Renaming files..." 1>&2
find . -type f -iname "*yaru*" | grep -v "^./.git" | while IFS= read -r file; do
    mv -v "${file}" "$(echo "${file}" | sed -E 's/(yaru)/\1dave/ig')"
done

echo "Renaming in content..." 1>&2
grep -lIir "yaru" . | grep -v "^./.git" | while IFS= read -r file; do
    echo "Replacing content in ${file}..."
    sed -i -E 's/(yaru)/\1dave/ig' "${file}"
    sed -i -E 's/(yaru)dave\.git/\1\.git/ig' "${file}"
done
