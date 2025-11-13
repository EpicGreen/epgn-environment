Name:           atuin
Version:        18.10.0
Release:        1%{?dist}
Summary:        Magical shell history

License:        MIT
URL:            https://github.com/atuinsh/%{name}
Source0:        https://github.com/atuinsh/%{name}/archive/refs/tags/v%{version}.tar.gz

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
Atuin replaces your existing shell history with a SQLite database,
and records additional context for your commands.
Additionally, it provides optional and fully encrypted synchronisation
of your history between machines, via an Atuin server.

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

git clone --recursive --depth 1 --shallow-submodules https://github.com/akinomyoga/ble.sh.git %{_builddir}/ble.sh
make -C %{_builddir}/ble.sh install PREFIX=%{_builddir}/usr

%install
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}blesh

# Install binary
install -D -m 755 %{_builddir}/%{name}-%{version}/target/release/%{name} %{buildroot}%{_bindir}/%{name}

#install ble.sh
install -D -m 755 %{_builddir}%{_datadir}/blesh/ble.sh %{buildroot}%{_datadir}/blesh/ble.sh

%files
%{_bindir}/%{name}
%{_datadir}/blesh/ble.sh

%post
echo 'eval "$(atuin init bash)" >> /dev/null' >> /etc/bashrc
echo 'source -- /usr/share/blesh/ble.sh' >> /etc/bashrc

%postun
sed -i '/atuin init bash/d' /etc/bashrc
sed -i '/source -- \/usr\/share\/blesh\/ble.sh/d' /etc/bashrc

%changelog
* Thu Nov 13 2025 Ante de Baas <antedebaas@users.github.com> - 18.10.0-1
- initial package
