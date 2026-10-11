#!/usr/bin/env bash
# Script to build Debian / Ubuntu (.deb) package
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="1.0.0"
PKG_NAME="drivemounter"
BUILD_DIR="$PROJECT_DIR/build_deb/${PKG_NAME}_${VERSION}_all"
OUTPUT_DIR="$PROJECT_DIR/dist"

echo "==> Building Debian package for $PKG_NAME v$VERSION..."

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/lib/python3/dist-packages"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/kio/servicemenus"
mkdir -p "$BUILD_DIR/usr/share/doc/$PKG_NAME"
mkdir -p "$OUTPUT_DIR"

# 1. DEBIAN/control file
cat <<EOF > "$BUILD_DIR/DEBIAN/control"
Package: $PKG_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: Krzysztof (Shieldziak) Tarczyński <32707076+Shieldowskyy@users.noreply.github.com>
Depends: python3 (>= 3.9), python3-pyqt6, cifs-utils, smbclient
Recommends: nfs-common, davfs2, libnotify-bin
Homepage: https://github.com/Shieldowskyy/drivemounter
Description: 1:1 Windows Map Network Drive clone for KDE Plasma
 Seamlessly mount remote network storage (SMB, NFS, WebDAV) on KDE Plasma
 with a familiar Windows workflow, drive letters (Z: to D:), auto-reconnect,
 Dolphin Places and service menu integration, and native Breeze styling.
EOF

# 2. Copy Python package
cp -r "$PROJECT_DIR/drivemounter" "$BUILD_DIR/usr/lib/python3/dist-packages/"
find "$BUILD_DIR/usr/lib/python3/dist-packages/drivemounter" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 3. Create launcher in /usr/bin/drivemounter
cat <<'EOF' > "$BUILD_DIR/usr/bin/drivemounter"
#!/usr/bin/env bash
exec python3 -m drivemounter.app "$@"
EOF
chmod 755 "$BUILD_DIR/usr/bin/drivemounter"

# 4. Install Desktop file
cp "$PROJECT_DIR/drivemounter.desktop" "$BUILD_DIR/usr/share/applications/drivemounter.desktop"
chmod 644 "$BUILD_DIR/usr/share/applications/drivemounter.desktop"

# 5. Install Dolphin Service Menu
cp "$PROJECT_DIR/drivemounter-service.desktop" "$BUILD_DIR/usr/share/kio/servicemenus/drivemounter.desktop"
chmod 644 "$BUILD_DIR/usr/share/kio/servicemenus/drivemounter.desktop"

# 6. Install documentation & license
cp "$PROJECT_DIR/LICENSE" "$BUILD_DIR/usr/share/doc/$PKG_NAME/copyright"
cp "$PROJECT_DIR/README.md" "$BUILD_DIR/usr/share/doc/$PKG_NAME/README.md"

# 7. Build package
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$OUTPUT_DIR/${PKG_NAME}_${VERSION}_all.deb"

echo "==> Successfully built Debian package: $OUTPUT_DIR/${PKG_NAME}_${VERSION}_all.deb"
