#!/usr/bin/env bash

set -euo pipefail

if [[ ! -f .gitignore ]]; then
    echo "ERROR: .gitignore is required before creating a release."
    exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: run this script from the Mapier Git repository."
    exit 1
fi

current_version="$(dpkg-parsechangelog -SVersion)"
maintainer="$(dpkg-parsechangelog -SMaintainer)"

echo "Current package version: $current_version"
read -r -p "New release version (for example, 0.1.1): " version
version="${version#v}"

if [[ ! "$version" =~ ^[0-9][0-9A-Za-z.+:~_-]*$ ]]; then
    echo "ERROR: invalid version: $version"
    exit 1
fi

debian_version="${version}-1"
tag="v${version}"

if git show-ref --tags --verify --quiet "refs/tags/$tag"; then
    echo "ERROR: tag $tag already exists."
    exit 1
fi

echo "New package version:     $debian_version"

tmp_changelog="$(mktemp)"
{
    printf 'mapier (%s) unstable; urgency=medium\n\n' "$debian_version"
    printf '  * Release %s.\n\n' "$version"
    printf ' -- %s  %s\n\n' "$maintainer" "$(LC_ALL=C date -R)"
    cat debian/changelog
} > "$tmp_changelog"
mv "$tmp_changelog" debian/changelog

git add -A
git commit -m "Release $tag"

./build.sh

artifacts=(
    "debs/mapier_${debian_version}_all.deb"
    "debs/mapier_latest_all.deb"
    "debs/mapier_${debian_version}_amd64.changes"
    "debs/mapier_${debian_version}_amd64.buildinfo"
)

for artifact in "${artifacts[@]}"; do
    if [[ ! -f "$artifact" ]]; then
        echo "ERROR: expected build artifact not found: $artifact"
        exit 1
    fi
done

git tag -a "$tag" -m "Mapier $tag"
git push origin main
git push origin "$tag"

gh release create "$tag" "${artifacts[@]}" \
    --title "Mapier $tag" \
    --generate-notes
