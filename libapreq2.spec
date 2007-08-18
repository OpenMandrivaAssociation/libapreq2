#Module-Specific definitions
%define rversion 2.08
%define revision r376644

%define mod_name mod_apreq
%define mod_conf 76_%{mod_name}2.conf
%define mod_so %{mod_name}2.so

%define apache_version 2.2.0

%define	major 2
%define libname	%mklibname apreq %{major}

Summary:	Apache Request Library
Name:		libapreq2
Version:	%{rversion}
#Release:	%mkrel 0.%{revision}.1
Release:	%mkrel 7
License:	Apache License
Group:          System/Libraries
URL:		http://httpd.apache.org/apreq/
#Source0:	libapreq2-%{rversion}-%{revision}.tar.bz2
Source0:	http://www.apache.org/dist/httpd/libapreq/libapreq2-%{rversion}.tar.gz
Source1:	http://www.apache.org/dist/httpd/libapreq/libapreq2-%{rversion}.tar.gz.asc
Source2:	76_mod_apreq2.conf
Patch0:		libapreq2-2.03-dev-version_check_fix.diff
Patch1:		libapreq2-2.08-autoconf260.diff
Patch2:		libapreq2-2.08-test_fixes.diff
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
BuildRequires:	chrpath
BuildRequires:	perl-devel
BuildRequires:	perl-doc
BuildRequires:	perl-Pod-Tests
BuildRequires:	perl-Apache-Test
BuildRequires:	perl-Template-Toolkit
BuildRequires:	perl-Tie-IxHash
BuildRequires:	perl-ExtUtils-XSBuilder
BuildRequires:	perl-Parse-RecDescent
BuildRequires:	perl-libwww-perl
BuildRequires:	apache-mod_perl-devel
BuildRequires:	apache-devel >= %{apache_version}
BuildRequires:	apache-source >= %{apache_version}
BuildRequires:	apache-mod_ssl >= %{apache_version}
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

This package contains the shared libraries for %{name}

%if "%{_lib}" != "lib"
%package -n	%{libname}
Summary:	Apache Request Library
Version:	%{rversion}
Group: 		System/Libraries

%description -n	%{libname}
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

This package contains the shared libraries for %{name}
%endif

%package -n	%{libname}-devel
Summary:	Development library and header files for the Apache Request Library
Version:	%{rversion}
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	libapreq-devel = %{version}

%description -n	%{libname}-devel
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

This package contains the development library and its header files.

%package -n	perl-libapreq2
Summary:	Apache Request Library Perl Glue
Version:	%{rversion}
Group:		System/Servers
Requires:	apache-mod_perl
Requires:	apache-mod_apreq = %{rversion}

%description -n perl-libapreq2
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

%package -n	apache-%{mod_name}
Summary:	Mod_apreq2 is a DSO module for the apache Web server
Group:		System/Servers
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= %{apache_version}
Requires:	apache-conf >= 2.2.0
Requires:	apache >= %{apache_version}
Requires:	perl-libapreq2 = %{rversion}

%description -n	apache-%{mod_name}
Mod_%{name} is a DSO module for the apache Web server.

%prep

%setup -q -n libapreq2-%{rversion}
%patch0 -p0
%patch1 -p0
%patch2 -p1

# got the idea why this wasn't working from debian, thanks guys!
# P0 combined with this hack fixes it all...
perl -pi -e "s|_APACHE2_REAL_VERSION_|%{apache_version}|g" build/version_check.pl

cp %{SOURCE2} %{mod_conf}

%build
export WANT_AUTOCONF_2_5=1
#libtoolize --copy --force && aclocal-1.7 && autoconf && autoheader && automake-1.7 -a -c

export AUTOMAKE="automake-1.7"
export ACLOCAL="aclocal-1.7"

sh ./buildconf

%configure2_5x \
    --with-perl=%{_bindir}/perl \
    --enable-perl-glue \
    --with-mm-opts=INSTALLDIRS=vendor \
    --with-apache2-apxs=%{_sbindir}/apxs \
    --with-apr-config=%{_bindir}/apr-1-config \
    --with-apu-config=%{_bindir}/apu-1-config

%make

# Build the perl modules
#pushd glue/perl
#    %{__perl} ../../build/xsbuilder.pl run
#    CFLAGS="%{optflags}" %{__perl} Makefile.PL -apxs %{_sbindir}/apxs INSTALLDIRS=vendor
#    %make
#    mv Makefile Makefile.xx
#popd

make test

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

# move the module in place
mv %{buildroot}%{_libdir}/apache %{buildroot}%{_libdir}/apache-extramodules

# install module conf files for the "conf.d" dir loading structure
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/

# install one extra devel file
install -m0755 apreq*-config %{buildroot}%{_bindir}/

# install the perl stuff
#pushd glue/perl
#cp Makefile.xx Makefile
#%makeinstall_std
#popd

# nuke rpath
find %{buildroot}%{perl_vendorlib} -name "*.so" | xargs chrpath -d

# cleanup
rm -f %{buildroot}%{_libdir}/apache-extramodules/*.a
rm -f %{buildroot}%{_libdir}/apache-extramodules/*.la

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post -n apache-%{mod_name}
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun -n apache-%{mod_name}
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc CHANGES INSTALL README
%{_libdir}/libapreq*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%doc CHANGES INSTALL README
%{_bindir}/apreq*-config
%{_libdir}/libapreq*.so
%{_libdir}/libapreq*.la
%{_libdir}/libapreq*.a
%{_includedir}/apreq*
%{_includedir}/apache/apreq*

%files -n apache-%{mod_name}
%defattr(-,root,root)
%doc CHANGES INSTALL README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

%files -n perl-libapreq2
%defattr(-,root,root)
%doc CHANGES INSTALL README
%{perl_vendorlib}/*/auto/APR/Request/*
%{perl_vendorlib}/*/Apache2/*
%{perl_vendorlib}/*/APR/*
%{_mandir}/man3/*


