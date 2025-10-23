Name:           epgn-environment
Version:        1.0.0
Release:        %{commit_date}%{shortcommit}%{?dist}
Summary:        Installs shell scripts in /etc/profile.d/
License:        GPLv3-only
URL:            https://github.com/EpicGreen/epgn-environment
Source0:        https://github.com/EpicGreen/epgn-environment/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildArch:      noarch

%description
Installs shell scripts in /etc/profile.d/

%prep
%autosetup

%build

%install
install -D -m 0755 scripts/epgn-aliases.sh %{buildroot}/etc/profile.d/epgn-aliases.sh
install -D -m 0755 scripts/epgn-default-editor.sh %{buildroot}/etc/profile.d/epgn-default-editor.sh
install -D -m 0755 scripts/epgn-history.sh %{buildroot}/etc/profile.d/epgn-history.sh
install -D -m 0755 scripts/epgn-prompt.sh %{buildroot}/etc/profile.d/epgn-prompt.sh

%files
/etc/profile.d/epgn-aliases.sh
/etc/profile.d/epgn-default-editor.sh
/etc/profile.d/epgn-history.sh
/etc/profile.d/epgn-prompt.sh

%changelog
* Thu Oct 23 2025 Ante <ante@users.github.com> - 1.0.0-1
- Initial package
