Name:           stalwart
Version:        0.16.4
Release:        1%{?dist}
Summary:        All-in-one Mail & Collaboration server. Secure, scalable and fluent in every protocol (IMAP, JMAP, SMTP, CalDAV, CardDAV, WebDAV).

%global epgn_version 1.3.6

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
BuildRequires:  clang19-devel clang19-libs

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

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{name} \
    -s /sbin/nologin -c "%{name}" %{name}

%install
# Install binary
install -D -m 755 %{_builddir}/%{name}-%{version}/target/release/%{name} %{buildroot}%{_bindir}/%{name}

# Install config file
install -D -m 644 %{_builddir}/epgn-environment-%{epgn_version}/configs/%{name}.json %{buildroot}%{_sysconfdir}/%{name}.json

# Install systemd service
install -D -m 644 %{_builddir}/epgn-environment-%{epgn_version}/configs/%{name}.service %{buildroot}%{_unitdir}/%{name}.service

# Create data directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/data
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/dumps
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/snapshots

%post
# Set ownership of data directory
chown -R %{name}:%{name} %{_sharedstatedir}/%{name}
chown %{name}:%{name} %{_sysconfdir}/%{name}.json

%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%{_bindir}/%{name}
%dir %attr(0755,%{name},%{name}) %{_sharedstatedir}/%{name}
%dir %attr(0755,%{name},%{name}) %{_sharedstatedir}/%{name}/data
%dir %attr(0755,%{name},%{name}) %{_sharedstatedir}/%{name}/dumps
%dir %attr(0755,%{name},%{name}) %{_sharedstatedir}/%{name}/snapshots
%config(noreplace) %attr(0644,%{name},%{name}) %{_sysconfdir}/%{name}.json
%{_unitdir}/%{name}.service

%changelog
* Fri May 8 2026 Ante de Baas <antedebaas@users.github.com> - 1.43.0
- inital
