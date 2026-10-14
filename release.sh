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
repository_url="$(gh repo view --json url --jq .url)"

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

python3 - "$version" "$repository_url" <<'PY'
from pathlib import Path
import sys

version, repository_url = sys.argv[1:]
path = Path("README.md")
content = path.read_text()
start = "<!-- latest-release:start -->"
end = "<!-- latest-release:end -->"
replacement = f"""{start}
The latest release is [v{version}]({repository_url}/releases/tag/v{version}).

Download and install the latest package:

```bash
wget {repository_url}/releases/latest/download/mapier_latest_all.deb
sudo apt install ./mapier_latest_all.deb
```
{end}"""

if start not in content or end not in content:
    raise SystemExit("ERROR: README latest-release block is missing.")

before, remainder = content.split(start, 1)
_, after = remainder.split(end, 1)
path.write_text(before + replacement + after)
PY

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
