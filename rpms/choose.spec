Name:           choose
Version:        1.3.7
Release:        1%{?dist}
Summary:        A human-friendly and fast alternative to cut (and sometimes awk)

License:        GPL-3.0
URL:            https://github.com/theryangeary/%{name}
Source0:        https://github.com/theryangeary/%{name}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(openssl)
BuildRequires:  make
BuildRequires:  git

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
A human-friendly and fast alternative to cut (and sometimes awk)

%prep
%autosetup -n %{name}-%{version}

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
%install
install -d %{buildroot}%{_bindir}

# Install binary
install -D -m 755 %{_builddir}/%{name}-%{version}/target/release/%{name} %{buildroot}%{_bindir}/%{name}

%files
%{_bindir}/%{name}

%changelog
* Thu Nov 25 2025 Ante de Baas <antedebaas@users.github.com> - 1.3.7-1
- Initial package
