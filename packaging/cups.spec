#
# RPM "spec" file for CUPS.
#
# Original version by Jason McMullan <jmcc@ontv.com>.
#
# Copyright © 2020-2023 by OpenPrinting
# Copyright © 2007-2019 by Apple Inc.
# Copyright © 1999-2007 by Easy Software Products, all rights reserved.
#
# Licensed under Apache License v2.0.  See the file "LICENSE" for more
# information.
#

# Conditional build options (--with name/--without name):
#
#   dbus     - Enable/disable DBUS support (default = enable)
#   dnssd    - Enable/disable DNS-SD support (default = enable)
#   libusb1  - Enable/disable LIBUSB 1.0 support (default = enable)
#   static   - Enable/disable static libraries (default = enable)
#   systemd  - Enable/disable systemd support (default = enable)

%{!?_with_dbus: %{!?_without_dbus: %define _with_dbus --with-dbus}}
%{?_with_dbus: %define _dbus --enable-dbus}
%{!?_with_dbus: %define _dbus --disable-dbus}

%{!?_with_dnssd: %{!?_without_dnssd: %define _with_dnssd --with-dnssd}}
%{?_with_dnssd: %define _dnssd --enable-avahi}
%{!?_with_dnssd: %define _dnssd --disable-avahi}

%{!?_with_libusb1: %{!?_without_libusb1: %define _with_libusb1 --with-libusb1}}
%{?_with_libusb1: %define _libusb1 --enable-libusb}
%{!?_with_libusb1: %define _libusb1 --disable-libusb}

%{!?_with_static: %{!?_without_static: %define _without_static --without-static}}
%{?_with_static: %define _static --enable-static}
%{!?_with_static: %define _static --disable-static}

%{!?_with_systemd: %{!?_without_systemd: %define _with_systemd --with-systemd}}
%{?_with_systemd: %define _systemd --enable-systemd}
%{!?_with_systemd: %define _systemd --disable-systemd}

Summary: CUPS
Name: cups
Version: 2.4.12
Release: 0
Epoch: 1
License: GPL
Group: System Environment/Daemons
Source: https://github.com/openprinting/cups/releases/download/v2.4.12/cups-2.4.12-source.tar.gz
Url: https://openprinting.github.io/cups
Packager: Anonymous <anonymous@example.com>
Vendor: OpenPrinting

# Package names are as defined for Red Hat (and clone) distributions
BuildRequires: gnutls-devel, pam-devel

%if %{?_with_dbus:1}%{!?_with_dbus:0}
BuildRequires: dbus-devel
%endif

%if %{?_with_dnssd:1}%{!?_with_dnssd:0}
BuildRequires: avahi-devel
%endif

%if %{?_with_libusb1:1}%{!?_with_libusb1:0}
BuildRequires: libusb-devel >= 1.0
%endif

%if %{?_with_systemd:1}%{!?_with_systemd:0}
BuildRequires: systemd-devel
%endif

# Use buildroot so as not to disturb the version already installed
BuildRoot: /tmp/%{name}-root

# Dependencies...
Requires: %{name}-libs = %{epoch}:%{version}
Obsoletes: lpd, lpr, LPRng
Provides: lpd, lpr, LPRng
Obsoletes: cups-da, cups-de, cups-es, cups-et, cups-fi, cups-fr, cups-he
Obsoletes: cups-id, cups-it, cups-ja, cups-ko, cups-nl, cups-no, cups-pl
Obsoletes: cups-pt, cups-ru, cups-sv, cups-zh

%package devel
Summary: CUPS - development environment
Group: Development/Libraries
Requires: %{name}-libs = %{epoch}:%{version}

%package libs
Summary: CUPS - shared libraries
Group: System Environment/Libraries
Provides: libcups1

%package lpd
Summary: CUPS - LPD support
Group: System Environment/Daemons
Requires: %{name} = %{epoch}:%{version} xinetd

%description
CUPS is the standards-based, open source printing system developed by
Apple Inc. and maintained by OpenPrinting for macOS® and other UNIX®-like
operating systems.

%description devel
This package provides the CUPS headers and development environment.

%description libs
This package provides the CUPS shared libraries.

%description lpd
This package provides LPD client support.

%prep
%setup

%build
CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_OPT_FLAGS" \
    ./configure %{_dbus} %{_dnssd} %{_libusb1} %{_static} %{_systemd}
# If we got this far, all prerequisite libraries must be here.
make

%install
# Make sure the RPM_BUILD_ROOT directory exists.
rm -rf $RPM_BUILD_ROOT

make BUILDROOT=$RPM_BUILD_ROOT install
rm -rf $RPM_BUILD_ROOT/usr/share/cups/banners $RPM_BUILD_ROOT/usr/share/cups/data

%post
%if %{?_with_systemd:1}%{!?_with_systemd:0}
/bin/systemctl enable cups.service

if test $1 -ge 1; then
	/bin/systemctl stop cups.service
	/bin/systemctl start cups.service
fi

%else
/sbin/chkconfig --add cups
/sbin/chkconfig cups on

# Restart cupsd if we are upgrading...
if test $1 -gt 1; then
	/sbin/service cups stop
	/sbin/service cups start
fi
%endif

%post libs
/sbin/ldconfig

%preun
%if %{?_with_systemd:1}%{!?_with_systemd:0}
if test $1 -ge 1; then
	/bin/systemctl stop cups.service
	/bin/systemctl disable cups.service
fi

%else
if test $1 = 0; then
	/sbin/service cups stop
	/sbin/chkconfig --del cups
fi
%endif

%postun
%if %{?_with_systemd:1}%{!?_with_systemd:0}
if test $1 -ge 1; then
	/bin/systemctl stop cups.service
	/bin/systemctl start cups.service
fi

%else
if test $1 -ge 1; then
	/sbin/service cups stop
	/sbin/service cups start
fi
%endif

%postun libs
/sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%files
%docdir /usr/share/doc/cups
%defattr(-,root,root)
%dir /etc/cups
%config(noreplace) /etc/cups/*.conf
/etc/cups/cups-files.conf.default
/etc/cups/cupsd.conf.default
/etc/cups/snmp.conf.default
%dir /etc/cups/ppd
%attr(0700,root,root) %dir /etc/cups/ssl

%if %{?_with_dbus:1}%{!?_with_dbus:0}
# DBUS
/etc/dbus-1/system.d/*
%endif

# PAM
%dir /etc/pam.d
/etc/pam.d/*

%if %{?_with_systemd:1}%{!?_with_systemd:0}
# SystemD
/usr/lib/systemd/system/cups.*

%else
# Legacy init support on Linux
/etc/init.d/*
/etc/rc0.d/*
/etc/rc2.d/*
/etc/rc3.d/*
/etc/rc5.d/*
%endif

/usr/bin/cancel
/usr/bin/cupstestppd
/usr/bin/ippeveprinter
/usr/bin/ipptool
/usr/bin/lp*
%dir /usr/lib/cups
%dir /usr/lib/cups/backend
%if %{?_with_dnssd:1}%{!?_with_dnssd:0}
# DNS-SD
/usr/bin/ippfind
/usr/lib/cups/backend/dnssd
%endif
/usr/lib/cups/backend/http
/usr/lib/cups/backend/https
%attr(0700,root,root) /usr/lib/cups/backend/ipp
/usr/lib/cups/backend/ipps
%attr(0700,root,root) /usr/lib/cups/backend/lpd
/usr/lib/cups/backend/snmp
/usr/lib/cups/backend/socket
/usr/lib/cups/backend/usb
%dir /usr/lib/cups/cgi-bin
/usr/lib/cups/cgi-bin/*
%dir /usr/lib/cups/command
/usr/lib/cups/command/*
%dir /usr/lib/cups/daemon
/usr/lib/cups/daemon/cups-deviced
/usr/lib/cups/daemon/cups-driverd
/usr/lib/cups/daemon/cups-exec
%dir /usr/lib/cups/driver
%dir /usr/lib/cups/filter
/usr/lib/cups/filter/*
%dir /usr/lib/cups/monitor
/usr/lib/cups/monitor/*
%dir /usr/lib/cups/notifier
/usr/lib/cups/notifier/*

/usr/sbin/*
%dir /usr/share/cups
%dir /usr/share/cups/drv
/usr/share/cups/drv/*
%dir /usr/share/cups/ipptool
/usr/share/cups/ipptool/*
%dir /usr/share/cups/mime
/usr/share/cups/mime/*
%dir /usr/share/cups/model
%dir /usr/share/cups/ppdc
/usr/share/cups/ppdc/*
%dir /usr/share/cups/templates
/usr/share/cups/templates/*
%if %{?_with_libusb1:1}%{!?_with_libusb1:0}
# LIBUSB quirks files
%dir /usr/share/cups/usb
/usr/share/cups/usb/*
%endif

%dir /usr/share/doc/cups
/usr/share/doc/cups/*.*
%dir /usr/share/doc/cups/help
/usr/share/doc/cups/help/accounting.html
/usr/share/doc/cups/help/admin.html
/usr/share/doc/cups/help/cgi.html
/usr/share/doc/cups/help/encryption.html
/usr/share/doc/cups/help/firewalls.html
/usr/share/doc/cups/help/glossary.html
/usr/share/doc/cups/help/kerberos.html
/usr/share/doc/cups/help/license.html
/usr/share/doc/cups/help/man-*.html
/usr/share/doc/cups/help/network.html
/usr/share/doc/cups/help/options.html
/usr/share/doc/cups/help/overview.html
/usr/share/doc/cups/help/policies.html
/usr/share/doc/cups/help/ref-*.html
/usr/share/doc/cups/help/security.html
/usr/share/doc/cups/help/sharing.html
/usr/share/doc/cups/help/translation.html
%dir /usr/share/doc/cups/images
/usr/share/doc/cups/images/*

#%dir /usr/share/doc/cups/ca
#/usr/share/doc/cups/ca/*
#%dir /usr/share/doc/cups/cs
#/usr/share/doc/cups/cs/*
%dir /usr/share/doc/cups/de
/usr/share/doc/cups/de/*
%dir /usr/share/doc/cups/es
/usr/share/doc/cups/es/*
#%dir /usr/share/doc/cups/fr
#/usr/share/doc/cups/fr/*
%dir /usr/share/doc/cups/ja
/usr/share/doc/cups/ja/*
%dir /usr/share/doc/cups/pt_BR
/usr/share/doc/cups/pt_BR/*
%dir /usr/share/doc/cups/ru
/usr/share/doc/cups/ru/*

%dir /usr/share/locale/ca
/usr/share/locale/ca/cups_ca.po
%dir /usr/share/locale/cs
/usr/share/locale/cs/cups_cs.po
%dir /usr/share/locale/de
/usr/share/locale/de/cups_de.po
%dir /usr/share/locale/en
/usr/share/locale/en/cups_en.po
%dir /usr/share/locale/es
/usr/share/locale/es/cups_es.po
%dir /usr/share/locale/fr
/usr/share/locale/fr/cups_fr.po
%dir /usr/share/locale/it
/usr/share/locale/it/cups_it.po
%dir /usr/share/locale/ja
/usr/share/locale/ja/cups_ja.po
%dir /usr/share/locale/pt_BR
/usr/share/locale/pt_BR/cups_pt_BR.po
%dir /usr/share/locale/ru
/usr/share/locale/ru/cups_ru.po
%dir /usr/share/locale/zh_CN
/usr/share/locale/zh_CN/cups_zh_CN.po

%dir /usr/share/man/man1
/usr/share/man/man1/cancel.1.gz
/usr/share/man/man1/cups.1.gz
/usr/share/man/man1/cupstestppd.1.gz
/usr/share/man/man1/ippeveprinter.1.gz
%if %{?_with_dnssd:1}%{!?_with_dnssd:0}
# DNS-SD
/usr/share/man/man1/ippfind.1.gz
%endif
/usr/share/man/man1/ipptool.1.gz
/usr/share/man/man1/lp.1.gz
/usr/share/man/man1/lpoptions.1.gz
/usr/share/man/man1/lpq.1.gz
/usr/share/man/man1/lpr.1.gz
/usr/share/man/man1/lprm.1.gz
/usr/share/man/man1/lpstat.1.gz
%dir /usr/share/man/man5
/usr/share/man/man5/*.conf.5.gz
/usr/share/man/man5/cupsd-logs.5.gz
/usr/share/man/man5/ipptoolfile.5.gz
/usr/share/man/man5/mime.*.5.gz
%dir /usr/share/man/man7
/usr/share/man/man7/ippevepcl.7.gz
/usr/share/man/man7/ippeveps.7.gz
%dir /usr/share/man/man8
/usr/share/man/man8/cups-deviced.8.gz
/usr/share/man/man8/cups-driverd.8.gz
/usr/share/man/man8/cups-exec.8.gz
/usr/share/man/man8/cups-snmp.8.gz
/usr/share/man/man8/cupsaccept.8.gz
/usr/share/man/man8/cupsctl.8.gz
/usr/share/man/man8/cupsfilter.8.gz
/usr/share/man/man8/cupsd.8.gz
/usr/share/man/man8/cupsd-helper.8.gz
/usr/share/man/man8/cupsdisable.8.gz
/usr/share/man/man8/cupsenable.8.gz
/usr/share/man/man8/cupsreject.8.gz
/usr/share/man/man8/lpadmin.8.gz
/usr/share/man/man8/lpc.8.gz
/usr/share/man/man8/lpinfo.8.gz
/usr/share/man/man8/lpmove.8.gz

%dir /var/cache/cups
%attr(0775,root,sys) %dir /var/cache/cups/rss
%dir /var/log/cups
%dir /var/run/cups
%attr(0711,lp,sys) %dir /var/run/cups/certs
%attr(0710,lp,sys) %dir /var/spool/cups
%attr(1770,lp,sys) %dir /var/spool/cups/tmp

# Desktop files
/usr/share/applications/*
/usr/share/icons/*

%files devel
%defattr(-,root,root)
%dir /usr/share/cups/examples
/usr/share/cups/examples/*
%dir /usr/share/man/man1
/usr/share/man/man1/cups-config.1.gz
/usr/share/man/man1/ppd*.1.gz
%dir /usr/share/man/man5
/usr/share/man/man5/ppdcfile.5.gz
/usr/share/man/man7/backend.7.gz
/usr/share/man/man7/filter.7.gz
/usr/share/man/man7/notifier.7.gz

/usr/bin/cups-config
/usr/bin/ppd*
%dir /usr/include/cups
/usr/include/cups/*
/usr/lib*/*.so

%if %{?_with_static:1}%{!?_with_static:0}
/usr/lib*/*.a
%endif

%dir /usr/share/doc/cups/help
/usr/share/doc/cups/help/api*.html
/usr/share/doc/cups/help/cupspm.*
/usr/share/doc/cups/help/postscript-driver.html
/usr/share/doc/cups/help/ppd-compiler.html
/usr/share/doc/cups/help/raster-driver.html
/usr/share/doc/cups/help/spec*.html

%files libs
%defattr(-,root,root)
/usr/lib*/*.so.*

%files lpd
%defattr(-,root,root)
%if %{?_with_systemd:1}%{!?_with_systemd:0}
# SystemD
/usr/lib/systemd/system/cups-lpd*
%else
# Legacy xinetd
/etc/xinetd.d/cups-lpd
%endif

%dir /usr/lib/cups
%dir /usr/lib/cups/daemon
/usr/lib/cups/daemon/cups-lpd
%dir /usr/share/man/man8
/usr/share/man/man8/cups-lpd.8.gz
