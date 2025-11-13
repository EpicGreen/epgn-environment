Name:           procs
Version:        0.14.10
Release:        1%{?dist}
Summary:        A modern replacement for ps

License:        MIT
URL:            https://github.com/dalance/%{name}
Source0:        https://github.com/dalance/%{name}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  rust >= 1.70
BuildRequires:  cargo
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(openssl)
BuildRequires:  make

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
BuildRequires:  cargo
BuildRequires:  cpp
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make

%description
procs is a replacement for ps written in Rust.

%prep
%autosetup -n %{name}-%{version}

%build
# Set build environment for optimal compilation
export CARGO_TARGET_DIR=%{_builddir}/%{name}-%{version}/target
export RUSTFLAGS="-Ccodegen-units=1 -Clink-dead-code=off"

# Ensure we have a proper Cargo.lock
[ -f Cargo.lock ] || cargo generate-lockfile

# Build with release optimizations
cargo build --release --verbose --locked
%{_builddir}/%{name}-%{version}/target/release/%{name} --gen-completion-out bash >> %{_builddir}/bash-completion

%install
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/bash-completion/completions/
install -d %{buildroot}%{_sysconfdir}/%{name}

install -D -m 755 %{_builddir}/%{name}-%{version}/target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -D -m 644 %{_builddir}/bash-completion %{buildroot}%{_datadir}/bash-completion/completions/%{name}
install -D -m 644 %{_builddir}/%{name}-%{version}/config/large.toml %{buildroot}%{_sysconfdir}/%{name}/config.toml

%files
%{_bindir}/%{name}
%{_datadir}/bash-completion/completions/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.toml

%changelog
* Thu Nov 13 2025 Ante de Baas <antedebaas@users.github.com> - 18.10.0-1
- initial package
