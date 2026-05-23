# Ladybird Web Browser RPM SPEC file
#
# SPDX-License-Identifier: BSD-3-Clause
# Maintainer: Dejan Lekic <dejan.lekic@gmail.com>

#############################################################################
# Global settings
#############################################################################

# Disable automatic debug package generation (we handle this ourselves)
%global debug_package %{nil}

# Disable Fedora's LTO flags as they interfere with the build
%global _lto_cflags %{nil}

# Ladybird uses its own RPATH handling
%undefine _cmake_skip_rpath

# Prevent stripping of binaries (preserves debug info for crash reports)
# We remove entire lines containing brp-strip to avoid leaving /usr/bin/strip orphaned
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!.*brp-strip.*!!g')

# Filter out auto-detected dependencies on bundled vcpkg libraries
# These are installed to a private directory and should not be system requirements
# This regex matches all the vcpkg-built libraries that we bundle
%global __requires_exclude ^lib(cpptrace|skia|simdjson|simdutf|sqlite3|libEGL_angle|libGLESv2_angle|icudata|icui18n|icuuc|tommath|avcodec|avformat|avutil|swresample|avif|brotlicommon|brotlidec|brotlienc|curl|crypto|ssl|dav1d|expat|fontconfig|freetype|harfbuzz|jpeg|jxl|jxl_cms|jxl_threads|png16|webp|webpdecoder|webpdemux|webpmux|woff2common|woff2dec|xml2|z|zstd|SDL3|openh264|opus|ogg|vorbis|vpx|tiff|lcms2|highway|nghttp2|nghttp3|ngtcp2)\\.so

# Filter out auto-generated provides for bundled vcpkg libraries
# We don't want to advertise these as system libraries that other packages can use
%global __provides_exclude ^lib(cpptrace|skia|simdjson|simdutf|sqlite3|libEGL_angle|libGLESv2_angle|icudata|icui18n|icuuc|tommath|avcodec|avformat|avutil|swresample|avif|brotlicommon|brotlidec|brotlienc|curl|crypto|ssl|dav1d|expat|fontconfig|freetype|harfbuzz|jpeg|jxl|jxl_cms|jxl_threads|png16|webp|webpdecoder|webpdemux|webpmux|woff2common|woff2dec|xml2|z|zstd|SDL3|openh264|opus|ogg|vorbis|vpx|tiff|lcms2|highway|nghttp2|nghttp3|ngtcp2)\\.so

# Private library directory (absolute path for %files section)
%global ladybird_libdir %{_libdir}/%{name}

# Private libexec directory for helper processes (absolute path for %files section)
%global ladybird_libexecdir %{_libexecdir}/%{name}

# Relative paths for CMake (these get combined with CMAKE_INSTALL_PREFIX)
# Using relative paths avoids double-prefix issues like /usr/usr/libexec
%global ladybird_libdir_rel lib64/%{name}
%global ladybird_libexecdir_rel libexec/%{name}

#############################################################################
# Version information
#############################################################################

# For release builds, set to a tag; for snapshots, use commit hash
# Update these for each new snapshot/release
#
# IMPORTANT: Set git_commit to the FULL 40-character commit hash.
# GitHub archives always extract to a directory named ladybird-<full_commit_hash>
# regardless of how you name the downloaded file.
%global git_commit      1c20baf3f3e84c98a242d77bd4f119cf5c1ee6ab
%global git_date        20260523

# Upstream version from CMakeLists.txt
%global upstream_version 0.1.0

#############################################################################
# Build conditionals
#############################################################################

# Enable Qt UI (default and recommended for Linux)
%bcond qt               1

# Enable running tests during build
%bcond tests            0

# Debug build
%bcond debug            0

#############################################################################
# Package metadata
#############################################################################

Name:           ladybird
Version:        %{upstream_version}
Release:        0.%{git_date}git%(c=%{git_commit}; echo ${c:0:10})%{?dist}
Summary:        A truly independent web browser using a novel engine based on web standards
License:        BSD-2-Clause
URL:            https://ladybird.org

# Source tarball from GitHub
# Download with: spectool -g -R ladybird.spec
# Or: curl -L -o ladybird-<commit>.tar.gz https://github.com/LadybirdBrowser/ladybird/archive/<commit>.tar.gz
#
# Note: GitHub archives ALWAYS extract to ladybird-<full_commit_hash>/ regardless
# of the download URL or local filename.
Source0:        https://github.com/LadybirdBrowser/ladybird/archive/%{git_commit}.tar.gz#/%{name}-%{git_commit}.tar.gz

# Ladybird requires 64-bit architectures with modern SIMD support
ExclusiveArch:  x86_64 aarch64

#############################################################################
# Build requirements
#############################################################################

# Core build tools
BuildRequires:  cmake >= 3.30
BuildRequires:  ninja-build
BuildRequires:  gcc-c++ >= 14
BuildRequires:  git-core
BuildRequires:  ccache
BuildRequires:  pkgconfig
BuildRequires:  make

# Rust toolchain (required for LibRegex)
BuildRequires:  rust >= 1.75
BuildRequires:  cargo >= 1.75

# Python (for build scripts and code generation)
BuildRequires:  python3 >= 3.9
BuildRequires:  python3-devel

# Autotools (required for some vcpkg dependencies)
BuildRequires:  autoconf >= 2.71
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  libtool

# Additional build tools
BuildRequires:  nasm
BuildRequires:  patchelf
BuildRequires:  curl
BuildRequires:  tar
BuildRequires:  unzip
BuildRequires:  zip
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  gperf

# Perl modules (required by some dependency builds)
BuildRequires:  perl-interpreter
BuildRequires:  perl-generators
BuildRequires:  perl(FindBin)
BuildRequires:  perl(IPC::Cmd)
BuildRequires:  perl(lib)
BuildRequires:  perl(Time::Piece)
BuildRequires:  perl(File::Copy)

# Graphics and display libraries
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  libglvnd-devel
BuildRequires:  vulkan-headers
BuildRequires:  vulkan-loader-devel

# Audio support
BuildRequires:  pkgconfig(libpulse)

# Wayland support
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(xkbcommon)

# X11 support (fallback)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(xi)
BuildRequires:  pkgconfig(xext)

%if %{with qt}
# Qt6 UI dependencies
BuildRequires:  qt6-qtbase-devel >= 6.4
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtwayland-devel
%endif

# Static library required by build
BuildRequires:  zlib-ng-compat-static
BuildRequires:  openssl-devel

# Desktop integration validation tools
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# Fonts used during build for tests/rendering
BuildRequires:  liberation-sans-fonts

#############################################################################
# Runtime requirements
#############################################################################

# Required fonts
Requires:       liberation-sans-fonts
Requires:       google-noto-emoji-fonts

# Desktop integration
Requires:       hicolor-icon-theme

# Audio (weak dependency - browser works without it)
Recommends:     pulseaudio-libs
Recommends:     pipewire-pulseaudio

# Hardware acceleration
Recommends:     mesa-dri-drivers
Recommends:     mesa-vulkan-drivers

# D-Bus for desktop integration
Recommends:     dbus

#############################################################################
# Bundled dependencies documentation
#
# Ladybird uses vcpkg to manage its dependencies with specific versions
# and build configurations. This is intentional and required for:
# - Consistent behavior across platforms
# - Specific feature flags and patches
# - Version compatibility guarantees
#
# These libraries are statically linked or installed to a private directory
# to avoid conflicts with system libraries.
#############################################################################

# Rendering and graphics
Provides:       bundled(skia) = 144
Provides:       bundled(angle) = chromium_7258

# Media codecs
Provides:       bundled(ffmpeg) = 7.1.1
Provides:       bundled(dav1d) = 1.5.1
Provides:       bundled(libavif) = 1.3.0
Provides:       bundled(libjxl) = 0.11.1

# Text and internationalization
Provides:       bundled(icu) = 78.1
Provides:       bundled(harfbuzz) = 10.2.0
Provides:       bundled(woff2) = 1.0.2

# Networking
Provides:       bundled(curl) = 8.16.0
Provides:       bundled(openssl) = 3.5.3
Provides:       bundled(nghttp2) = 1.68.0

# Image formats
Provides:       bundled(libpng) = 1.6.50
Provides:       bundled(libjpeg-turbo) = 3.1.1
Provides:       bundled(libwebp) = 1.6.0
Provides:       bundled(libtiff)

# Data processing
Provides:       bundled(simdjson) = 4.2.4
Provides:       bundled(simdutf) = 7.4.0
Provides:       bundled(sqlite) = 3.50.4
Provides:       bundled(libxml2) = 2.13.8
Provides:       bundled(fast-float) = 8.1.0

# Misc libraries
Provides:       bundled(fontconfig) = 2.15.0
Provides:       bundled(libtommath) = 1.3.0
Provides:       bundled(cpptrace) = 1.0.2
Provides:       bundled(dbus) = 1.16.2
Provides:       bundled(libproxy) = 0.4.18
Provides:       bundled(sdl3) = 3.2.28
Provides:       bundled(zlib) = 1.3.1

#############################################################################
# Package description
#############################################################################

%description
Ladybird is a truly independent web browser using a novel engine based on
web standards. It is not a fork of or based on Blink, Gecko, or WebKit.

Key features:
- Multi-process architecture for security and stability
- Independent LibWeb rendering engine
- Independent LibJS JavaScript engine
- Independent LibWasm WebAssembly implementation
- Sandboxed renderer and network processes

The browser consists of:
- Main UI process (Qt-based on Linux)
- WebContent renderer processes (one per tab)
- ImageDecoder process (for secure image handling)
- RequestServer process (for network requests)
- WebWorker process (for background JavaScript)

Note: Ladybird is currently in a pre-alpha state and is primarily suitable
for developers, testers, and early adopters. Many websites may not work
correctly yet.

#############################################################################
# Devel subpackage (optional - for embedding Ladybird components)
#############################################################################

%package        devel
Summary:        Development files for Ladybird browser components
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package contains CMake configuration files, library symlinks, and headers
for developing applications that embed or extend Ladybird components.

Note: The Ladybird API is unstable and subject to change without notice.
This package is primarily intended for advanced users and contributors.

#############################################################################
# Prep
#############################################################################

%prep
# GitHub archives extract to ladybird-<full_commit_hash>
%setup -q -n %{name}-%{git_commit}

# Remove any pre-existing build artifacts
rm -rf Build/

#############################################################################
# Build
#############################################################################

%build
# Set up build environment
export VCPKG_ROOT="${PWD}/Build/vcpkg"
export VCPKG_FORCE_SYSTEM_BINARIES=1
export LADYBIRD_SOURCE_DIR="${PWD}"

# Unset Fedora RPM build flags that interfere with vcpkg/meson builds
# These flags cause issues like linking C++ code with gcc instead of g++
# and other incompatibilities with vcpkg's build system
unset CFLAGS
unset CXXFLAGS
unset LDFLAGS
unset FFLAGS
unset FCFLAGS

# Clone vcpkg if not present (for local builds)
# IMPORTANT: vcpkg needs FULL git history (not shallow) for version resolution
if [ ! -d "${VCPKG_ROOT}" ]; then
    mkdir -p Build
    git clone https://github.com/microsoft/vcpkg.git "${VCPKG_ROOT}"
fi

# If vcpkg exists but is shallow, unshallow it
if [ -f "${VCPKG_ROOT}/.git/shallow" ]; then
    echo "Unshallowing vcpkg repository..."
    git -C "${VCPKG_ROOT}" fetch --unshallow
fi

# Bootstrap vcpkg
if [ ! -x "${VCPKG_ROOT}/vcpkg" ]; then
    "${VCPKG_ROOT}/bootstrap-vcpkg.sh" -disableMetrics
fi

# Create cache directory
mkdir -p Build/caches

# Determine build type
%if %{with debug}
BUILD_TYPE="Debug"
VCPKG_TRIPLETS="${PWD}/Meta/CMake/vcpkg/debug-triplets"
%else
BUILD_TYPE="Release"
VCPKG_TRIPLETS="${PWD}/Meta/CMake/vcpkg/release-triplets"
%endif

# Configure with CMake
# Note: We use custom lib/libexec directories to isolate Ladybird's bundled libraries
# Note: LTO is disabled because liblagom-main.a contains main() and LTO with
#       -Wl,--no-undefined causes "undefined symbol: main" linker errors
cmake -B Build/release -S . \
    -G Ninja \
    -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_BINDIR=bin \
    -DCMAKE_INSTALL_LIBDIR=%{ladybird_libdir_rel} \
    -DCMAKE_INSTALL_LIBEXECDIR=%{ladybird_libexecdir_rel} \
    -DCMAKE_INSTALL_DATADIR=share \
    -DCMAKE_INSTALL_INCLUDEDIR=include \
    -DCMAKE_TOOLCHAIN_FILE="${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" \
    -DVCPKG_INSTALL_OPTIONS="--no-print-usage" \
    -DVCPKG_OVERLAY_TRIPLETS="${VCPKG_TRIPLETS}" \
    -DBUILD_SHARED_LIBS=ON \
    -DENABLE_QT=%{?with_qt:ON}%{!?with_qt:OFF} \
    -DENABLE_INSTALL_FREEDESKTOP_FILES=ON \
    -DENABLE_INSTALL_HEADERS=ON \
    -DENABLE_GUI_TARGETS=ON \
    -DENABLE_LTO_FOR_RELEASE=OFF \
    -DLADYBIRD_CACHE_DIR="${PWD}/Build/caches" \
    %{nil}

# Build with parallel jobs
cmake --build Build/release --parallel %{?_smp_mflags}

#############################################################################
# Install
#############################################################################

%install
DESTDIR=%{buildroot} cmake --install Build/release

# Copy vcpkg-built shared libraries to private lib directory
# These are bundled dependencies that aren't installed by CMake
VCPKG_LIB_DIR="${PWD}/Build/release/vcpkg_installed/x64-linux-dynamic/lib"
if [ -d "${VCPKG_LIB_DIR}" ]; then
    # Copy all shared libraries from vcpkg
    find "${VCPKG_LIB_DIR}" -maxdepth 1 -name "*.so*" -exec cp -a {} %{buildroot}%{ladybird_libdir}/ \;
fi

# Fix RUNPATH on all binaries to correctly find the private library directory
# The CMake install sets incorrect paths like $ORIGIN/..//usr/lib64/ladybird
# We need $ORIGIN/../lib64/ladybird for binaries in /usr/bin
for binary in %{buildroot}%{_bindir}/*; do
    if [ -f "$binary" ] && file "$binary" | grep -q "ELF.*executable"; then
        patchelf --set-rpath '%{ladybird_libdir}' "$binary" || :
    fi
done

# Fix RUNPATH on libexec helper binaries
for binary in %{buildroot}%{ladybird_libexecdir}/*; do
    if [ -f "$binary" ] && file "$binary" | grep -q "ELF"; then
        patchelf --set-rpath '%{ladybird_libdir}' "$binary" || :
    fi
done

# Fix RUNPATH on shared libraries in the private lib directory
for lib in %{buildroot}%{ladybird_libdir}/*.so*; do
    if [ -f "$lib" ] && ! [ -L "$lib" ] && file "$lib" | grep -q "ELF.*shared"; then
        patchelf --set-rpath '%{ladybird_libdir}' "$lib" || :
    fi
done

# NOTE: We do NOT add the private lib directory to ld.so.conf.d
# The bundled libraries (libcrypto, libssl, libcurl, etc.) would override
# system libraries and break other applications.
# Instead, we rely on RPATH/RUNPATH in the binaries to find the bundled libs.

# Validate desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/org.ladybird.Ladybird.desktop

# Validate AppStream metadata (non-fatal as pre-alpha may have warnings)
appstream-util validate-relax --nonet \
    %{buildroot}%{_datadir}/metainfo/org.ladybird.Ladybird.metainfo.xml || :

#############################################################################
# Check (tests)
#############################################################################

%check
%if %{with tests}
pushd Build/release
ctest --output-on-failure --parallel %{?_smp_mflags} || :
popd
%endif

#############################################################################
# Post-installation scriptlets
#############################################################################

# NOTE: We don't use ldconfig_scriptlets because our libraries are in a
# private directory that is intentionally NOT in ld.so.conf.d to avoid
# overriding system libraries. Binaries use RPATH to find bundled libs.

%post
# Update icon cache
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ]; then
    # Package removal
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
# Update icon cache and desktop database after transaction completes
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
update-desktop-database &>/dev/null || :

#############################################################################
# Files - main package
#############################################################################

%files
# License and documentation
%license LICENSE
%doc README.md
%doc CONTRIBUTING.md
%doc CODE_OF_CONDUCT.md
%doc SECURITY.md
%doc ISSUES.md
%doc Documentation/

# Main browser binary
%{_bindir}/Ladybird

# JavaScript and WebAssembly utilities
%{_bindir}/js
%{_bindir}/wasm

# Commit file (version tracking)
%{_prefix}/COMMIT

# Helper processes (in private libexec directory)
# These are internal processes spawned by the main browser
%dir %{ladybird_libexecdir}
%{ladybird_libexecdir}/ImageDecoder
%{ladybird_libexecdir}/RequestServer
%{ladybird_libexecdir}/WebContent
%{ladybird_libexecdir}/WebWorker

# Shared libraries (in private lib directory)
# These include both Ladybird's own libs and bundled vcpkg dependencies
%dir %{ladybird_libdir}
%{ladybird_libdir}/*.so.*

# Resource files (fonts, icons, themes, templates)
%{_datadir}/Lagom/

# Desktop integration
%{_datadir}/applications/org.ladybird.Ladybird.desktop
%{_datadir}/icons/hicolor/scalable/apps/org.ladybird.Ladybird.svg
%{_datadir}/metainfo/org.ladybird.Ladybird.metainfo.xml
%{_datadir}/dbus-1/services/org.ladybird.Ladybird.service

#############################################################################
# Files - devel subpackage
#############################################################################

%files devel
# Library symlinks for development (unversioned .so files)
%{ladybird_libdir}/*.so

# Static libraries needed for linking tools
%{ladybird_libdir}/*.a

# CMake package configuration files
%{_datadir}/Ladybird/

# Headers for Ladybird libraries and components
# Using wildcard patterns for maintainability since the exact
# set of installed headers may change between versions
%{_includedir}/AK/
%{_includedir}/Lib*/
%{_includedir}/Services/

# Generated IPC endpoint headers
%{_includedir}/Meta/
%{_includedir}/*Endpoint.h

#############################################################################
# Changelog
#############################################################################

%changelog
* Wed Feb 18 2026 Dejan Lekic <fname.sname@gmail.com> - 0.1.0-0.20260218git2e3c59f791
- Update to latest snapshot (commit 2e3c59f791908f955b79937fb1ba0242fada1ac5)

* Fri Jan 30 2026 Dejan Lekic <fname.sname@gmail.com> - 0.1.0-0.20260130gita5cabf341b
- Initial RPM package for Fedora 43+
- Pre-alpha development snapshot
- Using vcpkg for hermetic dependency management
- Qt6 UI enabled by default
- Multi-process architecture with sandboxed renderers
- Added devel subpackage with CMake configs and headers
