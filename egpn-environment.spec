Name:           epgn-environment
Version:        1.2.3
Release:        1%{?dist}
Summary:        Installs shell scripts in /etc/profile.d/
License:        GPLv3-only
Source0:        https://github.com/EpicGreen/epgn-environment/archive/refs/tags/v%{version}.tar.gz

BuildArch:      noarch

%description
Installs scripts used by the EpicGreen project to set up user environments.

%prep
%autosetup

%build

%install
install -D -m 0755 configs/helix_config.toml %{buildroot}/etc/skel/.config/helix/config.toml
install -D -m 0755 configs/helix_config.toml %{buildroot}/root/.config/helix/config.toml

install -D -m 0755 yum.repos.d/1password.repo %{buildroot}/etc/yum.repos.d/1password.repo

install -D -m 0644 profile.d/epgn-aliases.sh %{buildroot}/etc/profile.d/epgn-aliases.sh
install -D -m 0644 profile.d/epgn-default-editor.sh %{buildroot}/etc/profile.d/epgn-default-editor.sh
install -D -m 0644 profile.d/epgn-history.sh %{buildroot}/etc/profile.d/epgn-history.sh
install -D -m 0644 profile.d/epgn-prompt.sh %{buildroot}/etc/profile.d/epgn-prompt.sh

install -D -m 0755 scripts/hetzner_dns_hook.sh %{buildroot}/usr/bin/hetzner_dns_hook

%files
/etc/skel/.config/helix/config.toml
/etc/yum.repos.d/1password.repo
/root/.config/helix/config.toml
/etc/profile.d/epgn-aliases.sh
/etc/profile.d/epgn-default-editor.sh
/etc/profile.d/epgn-history.sh
/etc/profile.d/epgn-prompt.sh
/usr/bin/hetzner_dns_hook

%changelog
* Fri Oct 31 2025 Ante <antedebaas@users.github.com> - 1.2.1-1
- Add 1password repo file installation

* Fri Oct 31 2025 Ante <antedebaas@users.github.com> - 1.2.0-1
- Updates to hetzner_dns_hook script for Hetzner Cloud API

* Sun Oct 26 2025 Ante <antedebaas@users.github.com> - 1.1.0-1
- Added hetzner_dns_hook script installation
- Updated helix config installation paths
- Improved file permissions for installed scripts

* Thu Oct 23 2025 Ante <antedebaas@users.github.com> - 1.0.0-1
- Initial package
