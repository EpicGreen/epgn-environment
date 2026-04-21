%{!?postgresql_default:%global postgresql_default 1}

%global pname vchord
%global sname VectorChord
%global pgversion 16

Name:		postgresql%{pgversion}-%{pname}
Version:	1.1.1
Release:	1%{?dist}
Summary:	Scalable, fast, and disk-friendly vector search in Postgres, the successor of pgvecto.rs.
License:	AGPLv3
URL:		https://github.com/tensorchord/%{sname}/
Source0:	https://github.com/tensorchord/%{sname}/archive/refs/tags/%{version}.tar.gz

%if %?postgresql_default
%global pkgname %{pname}
%package -n %{pkgname}
Summary: VectorChord (vchord) is a PostgreSQL extension engineered for scalable, high-performance, and cost-effective vector search.
%else
%global pkgname %name
%endif

BuildRequires:	make gcc cargo rust
BuildRequires:	postgresql%{pgversion}-server-devel
Requires:	postgresql%{pgversion}-server

%global precise_version %{?epoch:%epoch:}%version-%release

%if %?postgresql_default
Provides: postgresql-%{pname} = %precise_version
Provides: %name = %precise_version
%endif
Provides: %{pkgname}%{?_isa} = %precise_version
Provides: %{pkgname} = %precise_version
Provides: %{pname}-any
Conflicts: %{pname}-any

%description
Open-source vector similarity search for Postgres. Supports L2 distance,
inner product, and cosine distance

%description -n %{pkgname}
Open-source vector similarity search for Postgres. Supports L2 distance,
inner product, and cosine distance

%prep
%setup -q -n %{sname}-%{version}

%build
%make_build %{?_smp_mflags} OPTFLAGS=""

%install
%make_install

#Remove header file, we don't need it right now:
%{__rm} %{buildroot}/%{_includedir}/pgsql/server/extension/%{pname}/%{pname}.h

%files -n %{pkgname}
%doc README.md
%license LICENSE
%{_libdir}/pgsql/%{pname}.so
%{_datadir}/pgsql/extension//%{pname}.control
%{_datadir}/pgsql/extension/%{pname}*sql

%changelog
* Tue Apr 21 2026 <a.debaas@epicgreen.nl> - 1.1.1-1
- Test package for 1.1.1
