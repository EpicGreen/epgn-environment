Name:           atuin
Version:        18.13.6
Release:        2%{?dist}
Summary:        Magical shell history

%global epgn_version 1.3.3

License:        MIT
URL:            https://github.com/atuinsh/%{name}
Source0:        https://github.com/atuinsh/%{name}/archive/refs/tags/v%{version}.tar.gz
Source1:        https://github.com/EpicGreen/epgn-environment/archive/refs/tags/v%{epgn_version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(openssl)
BuildRequires:  make
BuildRequires:  git
BuildRequires:  curl
BuildRequires:  cargo

# Only build on supported architectures for Rust
ExcludeArch:    i686 s390 %{power64}

# For COPR compatibility
%if 0%{?fedora} >= 36 || 0%{?rhel} >= 9
%bcond_without check
%else
%bcond_with check
%endif

%global debug_package %{nil}

Requires:       glibc

%description
Atuin replaces your existing shell history with a SQLite database,
and records additional context for your commands.
Additionally, it provides optional and fully encrypted synchronisation
of your history between machines, via an Atuin server.

%prep
%autosetup -n %{name}-%{version}
# Extract epgn-environment source
tar -xzf %{SOURCE1} -C %{_builddir}

%build
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Set build environment for optimal compilation
export CARGO_TARGET_DIR=%{_builddir}/%{name}-%{version}/target
export RUSTFLAGS="-Ccodegen-units=1 -Clink-dead-code=off"

# Ensure we have a proper Cargo.lock
[ -f Cargo.lock ] || cargo generate-lockfile

# Build with release optimizations
cargo build --release --verbose --locked

git clone --recursive --depth 1 --shallow-submodules https://github.com/akinomyoga/ble.sh.git %{_builddir}/ble.sh
make -C %{_builddir}/ble.sh install PREFIX=%{_builddir}/usr

%install
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/blesh

# Install binairy
install -D -m 755 %{_builddir}/%{name}-%{version}/target/release/%{name} %{buildroot}%{_bindir}/%{name}

#copy profile.d scripts from epgn-environment
install -D -m 644 %{_builddir}/epgn-environment-%{epgn_version}/profile.d/atuin.sh %{buildroot}/etc/profile.d/atuin.sh

# Install ble.sh directory and its contents
cp -a %{_builddir}/usr/share/blesh %{buildroot}%{_datadir}/

%files
%{_bindir}/%{name}
%{_datadir}/blesh
/etc/profile.d/atuin.sh

%changelog
* Sat Apr 4 2026 Ante de Baas <antedebaas@users.github.com> - 18.13.6
- update version

* Thu Nov 13 2025 Ante de Baas <antedebaas@users.github.com> - 18.10.0-2
- initial package
