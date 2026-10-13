#!/bin/bash

set -e

echo "== Preparing package =="

mkdir -p bin bin-launcher

cp main.py bin/mapier.py
cp configs.py bin/configs.py
cp renderer.py bin/renderer.py
cp requester.py bin/requester.py
cp saver.py bin/saver.py
cp sources.py bin/sources.py

cat > bin-launcher/mapier <<'EOF'
#!/bin/sh
exec python3 /usr/lib/mapier/mapier.py "$@"
EOF

chmod +x bin-launcher/mapier

echo "OK: package files prepared"

echo
echo "== Checking project files =="

files=(
    "main.py"
    "configs.py"
    "renderer.py"
    "requester.py"
    "saver.py"
    "sources.py"
    "bin/mapier.py"
    "bin/configs.py"
    "bin/renderer.py"
    "bin/requester.py"
    "bin/saver.py"
    "bin/sources.py"
    "bin-launcher/mapier"
    "debian/control"
    "debian/rules"
    "debian/mapier.install"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "OK: $file"
    else
        echo "ERROR: missing $file"
        exit 1
    fi
done

echo
echo "== Checking launcher =="

if grep -q 'exec python3 /usr/lib/mapier/mapier.py "\$@"' bin-launcher/mapier; then
    echo "OK: launcher"
else
    echo "ERROR: launcher content is wrong"
    exit 1
fi

if [ -x bin-launcher/mapier ]; then
    echo "OK: launcher is executable"
else
    echo "ERROR: launcher is not executable"
    exit 1
fi

echo
echo "== Checking Debian install file =="

expected=(
    "bin/mapier.py usr/lib/mapier"
    "bin/configs.py usr/lib/mapier"
    "bin/renderer.py usr/lib/mapier"
    "bin/requester.py usr/lib/mapier"
    "bin/saver.py usr/lib/mapier"
    "bin/sources.py usr/lib/mapier"
    "bin-launcher/mapier usr/bin"
)

for line in "${expected[@]}"; do
    if grep -Fxq "$line" debian/mapier.install; then
        echo "OK: $line"
    else
        echo "ERROR: missing '$line'"
        exit 1
    fi
done

echo
echo "== Checking Python entry point =="

if grep -q 'from sources import expand_source_lists, load_layers' bin/mapier.py; then
    echo "OK: source loading import"
else
    echo "ERROR: source loading import missing"
    exit 1
fi

if grep -q 'sources = expand_source_lists' bin/mapier.py; then
    echo "OK: source-list expansion"
else
    echo "ERROR: source-list expansion not found"
    exit 1
fi

echo
echo "== Checking build tools =="

commands=(
    dpkg-buildpackage
    dh
)

for command in "${commands[@]}"; do
    if command -v "$command" >/dev/null 2>&1; then
        echo "OK: $command"
    else
        echo "ERROR: $command not found"
        exit 1
    fi
done

echo
echo "================================"
echo "All checks passed."
echo "================================"

read -r -p "Build package with dpkg-buildpackage? [y/N] " answer

if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo
    echo "== Building package =="
    dpkg-buildpackage -us -uc -b

    mkdir -p debs
    shopt -s nullglob
    artifacts=(../mapier_*.deb ../mapier_*.buildinfo ../mapier_*.changes)
    mv "${artifacts[@]}" debs/
    shopt -u nullglob
else
    echo "Build cancelled."
fi
