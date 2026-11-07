#!/usr/bin/env bash
# Build a .deb with plain dpkg-deb (no debhelper toolchain needed).
# Run from the repo root on a Debian/Ubuntu machine:
#   bash packaging/deb/build-deb.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
VER="${VER:-1.0}"
OUT_DIR="${OUT_DIR:-$REPO}"
WORK="$(mktemp -d)"
PKG="$WORK/amdpp_${VER}_all"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$PKG/DEBIAN" \
  "$PKG/usr/bin" \
  "$PKG/usr/share/amdpp" \
  "$PKG/usr/lib/amdpp" \
  "$PKG/etc/sudoers.d" \
  "$PKG/etc/xdg/autostart"

cat > "$PKG/DEBIAN/control" <<EOF
Package: amdpp
Version: $VER
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-pyside6.qtcore, python3-pyside6.qtgui, python3-pyside6.qtwidgets, sudo, power-profiles-daemon | tuned-ppd
Maintainer: Wookiee- <Wookiee-@users.noreply.github.com>
Homepage: https://github.com/Wookiee-/AMDPP
Description: AMD power profile and energy preference tray control
 System tray app to switch the power profile and AMD EPP on Ryzen CPUs.
EOF

install -Dm0755 "$REPO/packaging/amdpp" "$PKG/usr/bin/amdpp"
install -Dm0644 "$REPO/power-tray/power_tray.py" "$PKG/usr/share/amdpp/power_tray.py"
install -Dm0644 "$REPO/power-tray/amd.png" "$PKG/usr/share/amdpp/amd.png"
install -Dm0755 "$REPO/packaging/set-epp" "$PKG/usr/lib/amdpp/set-epp"
install -Dm0440 "$REPO/packaging/amdpp.sudoers" "$PKG/etc/sudoers.d/amdpp"
install -Dm0644 "$REPO/packaging/amdpp.desktop" "$PKG/etc/xdg/autostart/amdpp.desktop"

mkdir -p "$OUT_DIR"
dpkg-deb --root-owner-group -b "$PKG" "$OUT_DIR/amdpp_${VER}_all.deb"
echo "Built: $OUT_DIR/amdpp_${VER}_all.deb"
