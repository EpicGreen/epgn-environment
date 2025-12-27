Name:           witr
Version:        0.1.0
Release:        1%{?dist}
Summary:        Explain why a process, port, or service is running

License:        Apache-2.0
URL:            https://github.com/pranshuparmar/witr
Source0:        https://github.com/pranshuparmar/witr/archive/refs/tags/v%{version}.tar.gz

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
witr answers "why is this running?" for processes, ports, and services.
It traces causality for running things on Linux, showing how and why a process exists, its ancestry, and its context.
Useful for debugging, incident response, and understanding system state.

%prep
%autosetup -n %{name}-%{version}

%build
mkdir -p %{buildroot}/go25.5.linux-amd64
curl --proto '=https' --tlsv1.2 -sSf https://dl.google.com/go/go1.25.5.linux-amd64.tar.gz | tar -C %{buildroot}/go25.5.linux-amd64 -xz
export CGO_ENABLED=0
export GOFLAGS="-buildvcs=false"
%{buildroot}/go25.5.linux-amd64/bin/go build -v -o witr ./cmd/witr

%install
install -d %{buildroot}%{_bindir}
install -m 755 witr %{buildroot}%{_bindir}/witr

%files
%{_bindir}/witr

%changelog
* Sat Dec 27 2025 Ante de Baas <5467398+antedebaas@users.noreply.github.com> - 0.1.0-1
- Initial package for COPR
