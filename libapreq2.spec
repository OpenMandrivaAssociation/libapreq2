#Module-Specific definitions
%define rversion 2.13
%define revision r376644

%define mod_name mod_apreq
%define mod_conf 76_%{mod_name}2.conf
%define mod_so %{mod_name}2.so

%define apache_version 2.2.0

%define major 2
%define libname %mklibname apreq %{major}
%define develname %mklibname apreq -d

Summary:	Apache Request Library
Name:		libapreq2
Version:	%perl_convert_version %{rversion}
Release:	5
License:	Apache License
Group:		System/Libraries
URL:		http://httpd.apache.org/apreq/
#Source0:	libapreq2-%{rversion}-%{revision}.tar.bz2
Source0:	http://people.apache.org/~issac/libapreq2-%{rversion}.tar.gz
Source1:	http://people.apache.org/~issac/libapreq2-%{rversion}.tar.gz.asc
Source2:	76_mod_apreq2.conf
Source3:	libapreq2.pc.in
Patch0:		libapreq2-2.03-dev-version_check_fix.diff
Patch1:		libapreq2-2.08-autoconf260.diff
Patch2:		libapreq2-2.09-pkgconfig.patch
Patch3:		libapreq2-2.13-libtool.patch
BuildRequires:	autoconf2.5
BuildRequires:	automake
BuildRequires:	chrpath
BuildRequires:	perl-devel
BuildRequires:	perl-doc
BuildRequires:	perl(Pod::Tests)
BuildRequires:	perl(Apache::Test)
BuildRequires:	perl(Template)
BuildRequires:	perl(Tie::IxHash)
BuildRequires:	perl(ExtUtils::XSBuilder)
BuildRequires:	perl(Parse::RecDescent)
BuildRequires:	perl-libwww-perl
BuildRequires:	apache-mod_perl-devel
BuildRequires:	apache-devel >= %{apache_version}
BuildRequires:	apache-source >= %{apache_version}
BuildRequires:	apache-mod_ssl >= %{apache_version}

%description
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

This package contains the shared libraries for %{name}

# because it's the same name as srpm one on ia32:
%if "%{_lib}" != "lib"
%package -n	%{libname}
Summary:	Apache Request Library
Group: 		System/Libraries

%description -n	%{libname}
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

This package contains the shared libraries for %{name}
%endif

%package -n	%{develname}
Summary:	Development library and header files for the Apache Request Library
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	libapreq-devel = %{version}
Obsoletes:	%{mklibname apreq 0 -d}

%description -n	%{develname}
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

This package contains the development library and its header files.

%package -n	perl-libapreq2
Summary:	Apache Request Library Perl Glue
Group:		System/Servers
Requires:	apache-mod_perl
Requires:	apache-mod_apreq >= %{version}
Provides:	perl-libapreq

%description -n perl-libapreq2
libapreq is a safe, standards-compliant, high-performance library used for
parsing HTTP cookies, query-strings and POST data. The original version
(libapreq-1.X) was designed by Lincoln Stein and Doug MacEachern. The perl
APIs Apache::Request and Apache::Cookie are the lightweight mod_perl analogs of
the CGI and CGI::Cookie perl modules.

%package -n	apache-%{mod_name}
Summary:	DSO module for the apache Web server
Group:		System/Servers
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= %{apache_version}
Requires:	apache-conf >= 2.2.0
Requires:	apache >= %{apache_version}
Requires:	perl-libapreq2 >= %{version}

%description -n	apache-%{mod_name}
Mod_%{name} is a DSO module for the apache Web server.

%prep
%setup -q -n libapreq2-%{rversion}
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p1

# got the idea why this wasn't working from debian, thanks guys!
# P0 combined with this hack fixes it all...
perl -pi -e "s|_APACHE2_REAL_VERSION_|%{apache_version}|g" build/version_check.pl

cp %{SOURCE2} %{mod_conf}
cp %{SOURCE3} .

%build
export WANT_AUTOCONF_2_5=1
#libtoolize --copy --force && aclocal && autoconf && autoheader && automake -a -c


export AUTOMAKE="automake"
export ACLOCAL="aclocal"

sh ./buildconf

%configure2_5x \
    --with-perl=%{_bindir}/perl \
    --enable-perl-glue \
    --with-mm-opts=INSTALLDIRS=vendor \
    --with-apache2-apxs=%{_bindir}/apxs \
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

#make test

%install
%makeinstall_std

mkdir -p %{buildroot}%{_libdir}/pkgconfig
install -m 644 %{name}.pc %{buildroot}%{_libdir}/pkgconfig/%{name}.pc

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

%files -n %{libname}
%doc CHANGES INSTALL README
%{_libdir}/libapreq*.so.*

%files -n %{develname}
%doc CHANGES INSTALL README
%{_bindir}/apreq*-config
%{_libdir}/libapreq*.so
%{_libdir}/libapreq*.a
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/apreq*
%{_includedir}/apache/apreq*

%files -n apache-%{mod_name}
%doc CHANGES INSTALL README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

%files -n perl-libapreq2
%doc CHANGES INSTALL README
%{perl_vendorlib}/*/auto/APR/Request/*
%{perl_vendorlib}/*/Apache2/*
%{perl_vendorlib}/*/APR/*
%{_mandir}/man3/*


%changelog
* Wed Jan 25 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 2.130.0-3
+ Revision: 768358
- mass rebuild of perl extensions against perl 5.14.2

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 2.130.0-2mdv2011.0
+ Revision: 627783
- don't force the usage of automake1.7

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 2.130.0-1mdv2011.0
+ Revision: 607387
- fix deps

* Thu Dec 02 2010 Paulo Andrade <pcpa@mandriva.com.br> 2.130.0-0.0.3mdv2011.0
+ Revision: 605291
- Rebuild with apr with workaround to issue with gcc type based

* Thu Dec 02 2010 Paulo Andrade <pcpa@mandriva.com.br> 2.130.0-0.0.2mdv2011.0
+ Revision: 605060
- Rebuild with apr with workaround to issue with gcc type based alias analysis

* Sun Nov 28 2010 Oden Eriksson <oeriksson@mandriva.com> 2.130.0-0.0.1mdv2011.0
+ Revision: 602334
- 2.13 (pre-release)

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 2.12-5mdv2011.0
+ Revision: 588133
- rebuild

* Thu Jul 22 2010 Jérôme Quelin <jquelin@mandriva.org> 2.12-4mdv2011.0
+ Revision: 556774
- rebuild for perl 5.12

* Wed Jan 06 2010 Oden Eriksson <oeriksson@mandriva.com> 2.12-3mdv2010.1
+ Revision: 486818
- rebuilt against bdb 4.8

* Sun Aug 02 2009 Oden Eriksson <oeriksson@mandriva.com> 2.12-2mdv2010.0
+ Revision: 407519
- rebuild

* Sat Mar 14 2009 Oden Eriksson <oeriksson@mandriva.com> 2.12-1mdv2009.1
+ Revision: 354928
- 2.12

* Tue Jan 20 2009 Oden Eriksson <oeriksson@mandriva.com> 2.11-0.1mdv2009.1
+ Revision: 331679
- 2.11 (rc)
- rediffed P1
- 2.10-RC1

* Tue Jan 06 2009 Oden Eriksson <oeriksson@mandriva.com> 2.08-16mdv2009.1
+ Revision: 325871
- rebuild

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 2.08-15mdv2009.0
+ Revision: 235144
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Sun Jun 08 2008 Oden Eriksson <oeriksson@mandriva.com> 2.08-14mdv2009.0
+ Revision: 216852
- added P3 from HEAD to fix more autoconf260 borkiness
- disable the test suite for now. it works with openssl-0.9.8g but not with openssl-0.9.8h
- rebuild

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 2.08-13mdv2008.1
+ Revision: 170942
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake

* Thu Jan 17 2008 Oden Eriksson <oeriksson@mandriva.com> 2.08-12mdv2008.1
+ Revision: 154213
- bump release
- rebuild

* Mon Dec 24 2007 Oden Eriksson <oeriksson@mandriva.com> 2.08-11mdv2008.1
+ Revision: 137509
- rebuilt against openldap-2.4.7 libs

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Dec 14 2007 Thierry Vignaud <tv@mandriva.org> 2.08-10mdv2008.1
+ Revision: 119839
- fix upgrade

* Fri Dec 14 2007 Thierry Vignaud <tv@mandriva.org> 2.08-9mdv2008.1
+ Revision: 119837
- rebuild b/c of missing subpackage on ia32
- explain hackery

* Sun Sep 09 2007 Oden Eriksson <oeriksson@mandriva.com> 2.08-8mdv2008.0
+ Revision: 83438
- new devel naming

* Sat Aug 18 2007 Oden Eriksson <oeriksson@mandriva.com> 2.08-7mdv2008.0
+ Revision: 65824
- rebuild

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - rebuild for expat


* Sun Mar 11 2007 Oden Eriksson <oeriksson@mandriva.com> 2.08-5mdv2007.1
+ Revision: 141330
- rebuild

* Mon Nov 20 2006 Oden Eriksson <oeriksson@mandriva.com> 2.08-4mdv2007.1
+ Revision: 85563
- fixed deps and added a patch (P2) to make the tests pass under iurt
- added a autoconf-2.60 bug workaround (P1)
- rebuild
- Import libapreq2

* Sun Aug 13 2006 Oden Eriksson <oeriksson@mandriva.com> 2.08-1mdk
- 2.08

* Mon May 08 2006 Scott Karns <scottk@mandriva.org> 2.07-3mdk
- Added Requires: apache-mod_apreq to perl-libapreq2

* Mon Mar 20 2006 Oden Eriksson <oeriksson@mandriva.com> 2.07-2mdk
- fix deps

* Sun Feb 12 2006 Oden Eriksson <oeriksson@mandriva.com> 2.07-1mdk
- 2.07 (addresses CVE-2006-0042)

* Fri Feb 10 2006 Oden Eriksson <oeriksson@mandriva.com> 2.07-0.r376644.1mdk
- use a recent snap (r376644)

* Mon Jan 30 2006 Oden Eriksson <oeriksson@mandriva.com> 2.06-4.dev.4mdk
- actually _load_ the frigging apache module, DUH!

* Tue Dec 13 2005 Oden Eriksson <oeriksson@mandriva.com> 2.06-4.dev.3mdk
- rebuilt against apache-2.2.0

* Fri Sep 09 2005 Oden Eriksson <oeriksson@mandriva.com> 2.06-4.dev.1mdk
- rebuild

* Wed Aug 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.06-2.dev.2mdk
- rebuilt against new openldap-2.3.6 libs

* Sun Jul 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.06-1.dev.2mdk
- fix deps

* Fri Jul 22 2005 Oden Eriksson <oeriksson@mandriva.com> 2.06-1.dev.1mdk
- 2.06-dev

* Fri Jun 03 2005 Oden Eriksson <oeriksson@mandriva.com> 2.06-0.r179569.1mdk
- new SVN snap (r179569)
- rename the apache sub package (apache2/apache)
- the conf.d directory is renamed to modules.d
- use new rpm-4.4.x pre,post magic
- use better %%post and %%postun magic
- fix naming

* Sun Mar 20 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.05-0.r161185.1mdk
- use a recent cvs snap (r161185)
- run the tests

* Sun Mar 20 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.04_03-6mdk
- use the %%mkrel macro

* Fri Feb 18 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.04_03-5mdk
- spec file cleanups, remove the ADVX-build stuff

* Wed Feb 09 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.04_03-4mdk
- rebuilt for apache 2.0.53

* Fri Feb 04 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.04_03-3mdk
- rebuilt against new openldap libs

* Tue Dec 07 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 2.04_03-2mdk
- Rebuild for new perl
- Remove MANIFEST files

* Sat Sep 04 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.04_03-1mdk
- 2.04_03

* Wed Aug 11 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.03_04-3mdk
- rebuilt

* Mon Aug 02 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.03_04-2mdk
- rebuilt for apache 2.0.50

* Tue Jun 22 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.03_04-1mdk
- initial mandrake package based on the spec file by Bojan Smojver

