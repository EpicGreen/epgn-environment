Name:           stallwart
Version:        0.16.4
Release:        1%{?dist}
Summary:        All-in-one Mail & Collaboration server. Secure, scalable and fluent in every protocol (IMAP, JMAP, SMTP, CalDAV, CardDAV, WebDAV).

%global epgn_version 1.3.4

License:        MIT
URL:            https://github.com/stalwartlabs/%{name}
Source0:        https://github.com/stalwartlabs/%{name}/archive/refs/tags/v%{version}.tar.gz
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
All-in-one Mail & Collaboration server. Secure, scalable and fluent in every protocol (IMAP, JMAP, SMTP, CalDAV, CardDAV, WebDAV).

%prep
%autosetup -n %{name}-%{version}
### Extract epgn-environment source
###tar -xzf %{SOURCE1} -C %{_builddir}

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

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{name} \
    -s /sbin/nologin -c "%{name}" %{name}

%install
install -D -m 755 %{_builddir}/%{name}-%{version}/target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -D -m 644 %{_builddir}/epgn-environment-%{epgn_version}/configs/%{name}.json %{buildroot}%{_sysconfdir}/%{name}.json
install -D -m 644 %{_builddir}/epgn-environment-%{epgn_version}/configs/%{name}.service %{buildroot}%{_unitdir}/%{name}.service

%post
chown -R %{name}:%{name} /var/lib/%{name}

if grep -q "# master_key = \"YOUR_MASTER_KEY_VALUE\"" %{_sysconfdir}/%{name}.toml; then
    RANDOM_KEY=$(uuidgen)
    sed -i "s/# master_key = \"YOUR_MASTER_KEY_VALUE\"/master_key = \"$RANDOM_KEY\"/" %{_sysconfdir}/%{name}.toml
fi
chown %{name}:%{name} %{_sharedstatedir}/%{name}
%systemd_post %{name}.service

%files
%{_bindir}/%{name}
%{_sharedstatedir}/%{name}
%{_sharedstatedir}/%{name}/data
%{_sharedstatedir}/%{name}/dumps
%{_sharedstatedir}/%{name}/snapshots
%config(noreplace) %{_sysconfdir}/%{name}.toml
%{_unitdir}/%{name}.service

%changelog
* Fri May 4 2026 Ante de Baas <antedebaas@users.github.com> - 1.43.0
- inital
