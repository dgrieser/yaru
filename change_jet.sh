#!/bin/bash

set -euo pipefail

APP="$(basename "${0}")"

jet_old="#181818"
jet_new="${JET_NEW:-#262A2E}"

script_dir="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Limit the search to the theme sources (and any generated build output), but skip
# VCS metadata and this helper script itself.
search_roots=(.)
exclude_dirs=(--exclude-dir=.git --exclude-dir=.sass-cache --exclude-dir=meson-logs --exclude-dir=meson-private)
exclude_files=(--exclude="${APP}")

echo "Using jet_old=${jet_old}, jet_new=${jet_new}"

# Compute the derived colors the theme uses (lighten/darken/transparentize) so we
# can replace literal values in pre-generated CSS as well as the SCSS sources.
mapfile -t replacements < <(JET_OLD="${jet_old}" JET_NEW="${jet_new}" python "${script_dir}/change_jet_colors.py")

replace_literal() {
  local label="$1"
  local old="$2"
  local new="$3"

  # Gather files containing the old literal; ignore binaries.
  mapfile -t files < <(
    grep -lRIF "${exclude_dirs[@]}" "${exclude_files[@]}" -- "${old}" "${search_roots[@]}" || true
  )

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "No matches for ${label} (${old})"
    return
  fi

  echo "Replacing ${label}: ${old} -> ${new}"
  # Use Perl for robust literal replacement (handles #, parentheses, etc.).
  perl -pi -e 's/\Q'"${old}"'\E/'"${new}"'/g' "${files[@]}"
}

echo "Calculated replacements:"
for line in "${replacements[@]}"; do
  IFS=$'\t' read -r label old new <<<"${line}"
  printf "  %-18s %s -> %s\n" "${label}" "${old}" "${new}"
done

echo
for line in "${replacements[@]}"; do
  IFS=$'\t' read -r label old new <<<"${line}"
  replace_literal "${label}" "${old}" "${new}"

  # Also swap uppercase forms of hex colors if present.
  if [[ "${old}" =~ ^#[0-9a-fA-F]{6}$ ]]; then
    replace_literal "${label} (upper)" "${old^^}" "${new^^}"
  fi
done
