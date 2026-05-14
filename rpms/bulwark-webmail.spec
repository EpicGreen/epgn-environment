Name:           bulwark-webmail
Version:        1.6.5
Release:        1%{?dist}
Summary:        Modern webmail client built with Next.js and the JMAP protocol

License:        AGPL-3.0-only
URL:            https://github.com/bulwarkmail/webmail
Source0:        https://github.com/bulwarkmail/webmail/archive/refs/tags/%{version}.tar.gz

BuildRequires:  nodejs >= 20.0.0
BuildRequires:  npm
BuildRequires:  systemd-rpm-macros
BuildRequires:  git

# Only build on supported architectures for Node.js
ExcludeArch:    i686 s390

# For COPR compatibility
%if 0%{?fedora} >= 36 || 0%{?rhel} >= 9
%bcond_without check
%else
%bcond_with check
%endif

%global debug_package %{nil}

Requires:       nodejs >= 20.0.0
Requires(pre):  shadow-utils

%description
Bulwark is a modern, self-hosted webmail client for Stalwart Mail Server,
built with Next.js and the JMAP protocol. It provides a full webmail suite
including Mail, Calendar, Contacts, and Files management with OAuth2/OIDC
support, multi-language interface, and a plugin system.

%prep
%autosetup -n webmail-%{version}

%build
# Set build environment
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1
export GIT_COMMIT=%{version}
export HUSKY=0

# Remove husky prepare script from package.json (not needed for building)
node -e "const fs=require('fs'); const pkg=JSON.parse(fs.readFileSync('package.json')); delete pkg.scripts.prepare; fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));"

# Install dependencies
npm install --legacy-peer-deps

# Explicitly install Tailwind CSS PostCSS (might not be in package-lock)
npm install @tailwindcss/postcss --save-dev --legacy-peer-deps

# Build the Next.js application (without Turbopack for stability)
./node_modules/.bin/next build

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{name} \
    -s /sbin/nologin -c "Bulwark Webmail" %{name}

%install
# Create application directory
install -d -m 755 %{buildroot}%{_datadir}/%{name}

# Install the Next.js standalone build
cp -a .next/standalone/* %{buildroot}%{_datadir}/%{name}/
install -d -m 755 %{buildroot}%{_datadir}/%{name}/.next
cp -a .next/static %{buildroot}%{_datadir}/%{name}/.next/
cp -a public %{buildroot}%{_datadir}/%{name}/

# Create data directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/settings
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/admin
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/admin-state
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/telemetry
install -d -m 755 %{buildroot}%{_var}/log/%{name}

# Install systemd service
install -d -m 755 %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/%{name}.service << 'EOF'
[Unit]
Description=Bulwark Webmail
After=network.target

[Service]
Type=simple
User=bulwark-webmail
Group=bulwark-webmail
WorkingDirectory=%{_datadir}/%{name}
EnvironmentFile=%{_sysconfdir}/%{name}/.env.local
ExecStart=/usr/bin/node server.js
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bulwark-webmail

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=%{_sharedstatedir}/%{name}
ReadWritePaths=%{_var}/log/%{name}

[Install]
WantedBy=multi-user.target
EOF

# Create environment file template
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}
cat > %{buildroot}%{_sysconfdir}/%{name}/.env.local << 'EOF'
# Bulwark Webmail Configuration
# See https://github.com/bulwarkmail/webmail for full documentation

# Server listen address
HOSTNAME=0.0.0.0
PORT=3000

# JMAP Server (comment out to use the web setup wizard)
#JMAP_SERVER_URL=https://mail.example.com

# Session secret (required for production)
# Generate with: openssl rand -base64 32
#SESSION_SECRET=

# OAuth2/OIDC (optional)
#OAUTH_ENABLED=true
#OAUTH_CLIENT_ID=webmail
#OAUTH_CLIENT_SECRET=
#OAUTH_ISSUER_URL=

# Branding (optional)
#APP_NAME=Bulwark Webmail
#APP_SHORT_NAME=Webmail

# Logging
LOG_FORMAT=text
LOG_LEVEL=info

# Stalwart integration
STALWART_FEATURES=true

# Settings sync
SETTINGS_SYNC_ENABLED=true
SETTINGS_DATA_DIR=%{_sharedstatedir}/%{name}/settings

# Admin data directories
ADMIN_CONFIG_DIR=%{_sharedstatedir}/%{name}/admin
ADMIN_STATE_DIR=%{_sharedstatedir}/%{name}/admin-state

# Disable update check & telemetry by default
BULWARK_UPDATE_CHECK=off

# Production environment
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
EOF

%post
# Set ownership of data directories
chown -R %{name}:%{name} %{_sharedstatedir}/%{name}
chown -R %{name}:%{name} %{_var}/log/%{name}
chmod 750 %{_sharedstatedir}/%{name}
chmod 750 %{_var}/log/%{name}

%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md CHANGELOG.md FEATURES.md CONTRIBUTING.md
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%dir %attr(0750,%{name},%{name}) %{_var}/log/%{name}
%dir %attr(0750,%{name},%{name}) %{_sharedstatedir}/%{name}
%dir %attr(0750,%{name},%{name}) %{_sharedstatedir}/%{name}/settings
%dir %attr(0750,%{name},%{name}) %{_sharedstatedir}/%{name}/admin
%dir %attr(0750,%{name},%{name}) %{_sharedstatedir}/%{name}/admin-state
%dir %attr(0750,%{name},%{name}) %{_sharedstatedir}/%{name}/telemetry
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/.env.local
%{_unitdir}/%{name}.service

%changelog
* Thu May 14 2026 Ante de Baas <antedebaas@users.github.com> - 1.6.5-1
- Initial RPM package for bulwark-webmail
- Modern webmail client with JMAP protocol support
- Includes Mail, Calendar, Contacts, and Files features
- OAuth2/OIDC authentication support
- Multi-language interface with 15 languages
- Plugin system and theme support
- Web-based setup wizard
