Name:           egpn-environment
Version:        1.0
Release:        1%{?dist}
Summary:        Installs a shell script in /etc/profile.d/

License:        GPLv3-only
Source0:        epgn-aliases.sh
Source1:        epgn-default-editor.sh
Source2:        epgn-history.sh
Source3:        epgn-prompt.sh

Requires:       bash
Requires:       bat
Requires:       tmux
Requires:       htop

BuildArch:      noarch

%description
Installs a shell script in /etc/profile.d/

%prep

%build

%install
install -D -m 0755 %{SOURCE0} %{buildroot}/etc/profile.d/epgn-aliases.sh
install -D -m 0755 %{SOURCE1} %{buildroot}/etc/profile.d/epgn-default-editor.sh
install -D -m 0755 %{SOURCE2} %{buildroot}/etc/profile.d/epgn-history.sh
install -D -m 0755 %{SOURCE3} %{buildroot}/etc/profile.d/epgn-prompt.sh

%files
/etc/profile.d/epgn-aliases.sh
/etc/profile.d/epgn-default-editor.sh
/etc/profile.d/epgn-history.sh
/etc/profile.d/epgn-prompt.sh

%changelog
* Thu Oct 23 2025 Ante <ante@users.github.com> - 1.0-1
- Initial package
