Name:           atuin
Version:        10.18.0
Release:        1%{?dist}
Summary:        Magical shell history

License:        MIT
URL:            https://github.com/atuinsh/%{name}
Source0:        https://github.com/atuinsh/%{name}/archive/refs/tags/v%{version}.tar.gz

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

%description
Atuin replaces your existing shell history with a SQLite database,
and records additional context for your commands.
Additionally, it provides optional and fully encrypted synchronisation
of your history between machines, via an Atuin server.

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

%install
install -d %{buildroot}%{_bindir}

# Install binary
install -D -m 755 %{_builddir}/%{name}-%{version}/target/release/%{name} %{buildroot}%{_bindir}/%{name}

%files
%{_bindir}/%{name}

%changelog
* Thu Nov 13 2025 Ante de Baas <antedebaas@users.github.com> - 18.10.0-1
- initial package
