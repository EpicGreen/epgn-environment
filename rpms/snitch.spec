Name:           snitch
Version:        0.2.1
Release:        1%{?dist}
Summary:        A friendlier ss/netstat for humans – inspect network connections with a clean TUI or styled tables

License:        MIT
URL:            https://github.com/karol-broda/snitch
Source0:        https://github.com/karol-broda/snitch/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  systemd-rpm-macros

# Only build on supported architectures for Go
ExcludeArch:    s390 %{power64}

# For COPR compatibility
%if 0%{?fedora} >= 36 || 0%{?rhel} >= 9
%bcond_without check
%else
%bcond_with check
%endif

%global debug_package %{nil}

Requires:       glibc

%description
snitch is a friendlier alternative to ss/netstat for humans. It lets you inspect network connections with a clean terminal user interface (TUI) or styled tables. Features include live-updating connection lists, filtering, DNS/service name resolution, and multiple output formats (styled, plain, JSON, CSV). Supports Linux and macOS.

%prep
%autosetup -n %{name}-%{version}

%build
mkdir -p %{buildroot}/go25.5.linux-amd64
curl --proto '=https' --tlsv1.2 -sSf https://dl.google.com/go/go1.25.5.linux-amd64.tar.gz | tar -C %{buildroot}/go25.5.linux-amd64 -xz
export CGO_ENABLED=0
export GOFLAGS="-buildvcs=false"
%{buildroot}/go25.5.linux-amd64/bin/go build -v -o snitch .

%install
install -d %{buildroot}%{_bindir}
install -m 755 snitch %{buildroot}%{_bindir}/snitch

%files
%{_bindir}/snitch

%changelog
* Thu Dec 25 2025 Ante de Baas <5467398+antedebaas@users.noreply.github.com> - 0.2.1-1
- Initial package for COPR
