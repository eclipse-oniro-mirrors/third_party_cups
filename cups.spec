Name:    cups
Epoch:   1
Version: 2.2.8
Release: 9
Summary: CUPS is the standards-based, open source printing system for linux operating systems.
License: GPLv2+ and LGPLv2+ with exceptions and AML
Url:     http://www.cups.org/
Source0: https://github.com/apple/cups/releases/download/v%{VERSION}/cups-%{VERSION}-source.tar.gz

Source2: cupsprinter.png
Source3: cups.logrotate
Source4: ncp.backend
Source5: macros.cups

Patch1: cups-no-gzip-man.patch
Patch2: cups-system-auth.patch
Patch3: cups-multilib.patch
Patch5: cups-banners.patch
Patch7: cups-no-export-ssllibs.patch
Patch8: cups-direct-usb.patch
Patch12: cups-eggcups.patch
Patch16: cups-usb-paperout.patch
Patch19: cups-uri-compat.patch
Patch22: cups-hp-deviceid-oid.patch
Patch24: cups-ricoh-deviceid-oid.patch
Patch25: cups-systemd-socket.patch
Patch30: cups-freebind.patch
Patch35: cups-ipp-multifile.patch
Patch37: cups-synconclose.patch
Patch38: cups-ypbind.patch
Patch100: cups-lspp.patch
Patch9: cups-lpr-help.patch
Patch18: cups-filter-debug.patch
Patch29: cups-dymo-deviceid.patch
Patch41: cups-accesslog-null.patch
Patch42: cups-epson-A6-crash.patch
Patch43: cups-ippvalidateattr-regression.patch
Patch44: cups-ippeve-webui.patch
Patch45: 0001-Fix-memory-leaks-found-by-Coverity-Issue-5375.patch
Patch6000: CVE-2018-4300.patch
Patch6001: CVE-2019-8675-CVE-2019-8696.patch 
Patch6002: CVE-2019-2228.patch 

Provides: cupsddk cupsddk-drivers cups-filesystem cups-client cups-ipptool cups-lpd
Provides: lpd lpr /usr/bin/lpq /usr/bin/lpr /usr/bin/lp /usr/bin/cancel /usr/bin/lprm /usr/bin/lpstat
Obsoletes: cups-client cups-filesystem cups-lpd cups-ipptool

BuildRequires: pam-devel pkgconf-pkg-config pkgconfig(gnutls) libacl-devel openldap-devel pkgconfig(libusb-1.0)
BuildRequires: krb5-devel pkgconfig(avahi-client) systemd pkgconfig(libsystemd) pkgconfig(dbus-1) python3-cups
BuildRequires: automake zlib-devel gcc gcc-c++ libselinux-devel audit-libs-devel
Requires: dbus systemd acl cups-filters /usr/sbin/alternatives %{name}-libs = %{epoch}:%{version}-%{release}

%description
CUPS is the standards-based, open source printing system developed by Apple Inc.
for UNIX®-like operating systems. CUPS uses the Internet Printing
Protocol (IPP) to support printing to local and network printers..

%package devel
Summary: CUPS printing system - development environment
License: LGPLv2
Requires: %{name}%-libs = %{epoch}:%{version}-%{release}
Requires: gnutls-devel krb5-devel zlib-devel
Provides: cupsddk-devel

%description devel
CUPS is the standards-based, open source printing system developed by Apple Inc.
for macOS® and other UNIX®-like operating systems. Developers can use this development
package to develop other printer drivers.

%package libs
Summary: CUPS libs
License: LGPLv2 and zlib

%description  libs
The package provides cups libraries

%package    help
Summary:    Documents for cups
Buildarch:  noarch

%description    help
Man pages and other related documents.

%prep
%autosetup -n %{name}-%{version} -p1

sed -i -e '1iMaxLogSize 0' conf/cupsd.conf.in
sed -i -e 's,^ErrorLog .*$,ErrorLog syslog,' -i -e 's,^AccessLog .*$,AccessLog syslog,' -i -e 's,^PageLog .*,PageLog syslog,' conf/cups-files.conf.in

aclocal -I config-scripts
autoconf -I config-scripts

%build
export DSOFLAGS="$DSOFLAGS -L../cgi-bin -L../filter -L../ppdc -L../scheduler -Wl,-z,relro -Wl,-z,now -specs=/usr/lib/rpm/%{?_vendor}/%{?_vendor}-hardened-ld -Wl,-z,relro,-z,now -fPIE -pie" 
export CFLAGS="$RPM_OPT_FLAGS -fstack-protector-all -DLDAP_DEPRECATED=1"
# --enable-debug to avoid stripping binaries
%configure --with-docdir=%{_datadir}/%{name}/www --enable-debug \
    --enable-lspp \
    --with-exe-file-perm=0755 \
    --with-cupsd-file-perm=0755 \
    --with-log-file-perm=0600 \
    --enable-relro \
    --with-dbusdir=%{_sysconfdir}/dbus-1 \
    --with-php=/usr/bin/php-cgi \
    --enable-avahi \
    --enable-threads \
    --enable-gnutls \
    --enable-webif \
    --with-xinetd=no \
    --with-access-log-level=actions \
    --enable-page-logging \
    localedir=%{_datadir}/locale

%make_build

%install
make BUILDROOT=${RPM_BUILD_ROOT} install

rm -rf  ${RPM_BUILD_ROOT}%{_initddir} ${RPM_BUILD_ROOT}%{_sysconfdir}/{init.d,rc?.d}
install -d ${RPM_BUILD_ROOT}%{_unitdir}

find ${RPM_BUILD_ROOT}%{_datadir}/cups/model -name "*.ppd" |xargs gzip -n9f

pushd ${RPM_BUILD_ROOT}%{_bindir}
for file in cancel lp lpq lpr lprm lpstat; do
    mv $file $file.cups
done

mv ${RPM_BUILD_ROOT}%{_sbindir}/lpc ${RPM_BUILD_ROOT}%{_sbindir}/lpc.cups
cd ${RPM_BUILD_ROOT}%{_mandir}/man1
for file in cancel lp lpq lpr lprm lpstat; do
    mv $file.1 $file-cups.1
done

mv ${RPM_BUILD_ROOT}%{_mandir}/man8/lpc.8 ${RPM_BUILD_ROOT}%{_mandir}/man8/lpc-cups.8
popd

mv ${RPM_BUILD_ROOT}%{_unitdir}/org.cups.cupsd.path ${RPM_BUILD_ROOT}%{_unitdir}/cups.path
mv ${RPM_BUILD_ROOT}%{_unitdir}/org.cups.cupsd.service ${RPM_BUILD_ROOT}%{_unitdir}/cups.service
mv ${RPM_BUILD_ROOT}%{_unitdir}/org.cups.cupsd.socket ${RPM_BUILD_ROOT}%{_unitdir}/cups.socket
mv ${RPM_BUILD_ROOT}%{_unitdir}/org.cups.cups-lpd.socket ${RPM_BUILD_ROOT}%{_unitdir}/cups-lpd.socket
mv ${RPM_BUILD_ROOT}%{_unitdir}/org.cups.cups-lpd@.service ${RPM_BUILD_ROOT}%{_unitdir}/cups-lpd@.service

/bin/sed -i -e "s,org.cups.cupsd,cups,g" ${RPM_BUILD_ROOT}%{_unitdir}/cups.service

install -d ${RPM_BUILD_ROOT}%{_datadir}/pixmaps ${RPM_BUILD_ROOT}%{_sysconfdir}/X11/sysconfig \
           ${RPM_BUILD_ROOT}%{_sysconfdir}/X11/applnk/System ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d \
           ${RPM_BUILD_ROOT}%{_rpmconfigdir}/macros.d
install -p -m 644 %{SOURCE2} ${RPM_BUILD_ROOT}%{_datadir}/pixmaps
install -p -m 644 %{SOURCE3} ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/cups
install -p -m 755 %{SOURCE4} ${RPM_BUILD_ROOT}%{_exec_prefix}/lib/cups/backend/ncp
install -m 0644 %{SOURCE5} ${RPM_BUILD_ROOT}%{_rpmconfigdir}/macros.d

touch ${RPM_BUILD_ROOT}%{_sysconfdir}/cups/{printers,classes,client,subscriptions}.conf
touch ${RPM_BUILD_ROOT}%{_sysconfdir}/cups/lpoptions

install -d ${RPM_BUILD_ROOT}%{_datadir}/ppd

install -d ${RPM_BUILD_ROOT}%{_tmpfilesdir}
cat > ${RPM_BUILD_ROOT}%{_tmpfilesdir}/cups.conf <<EOF
d /run/cups 0755 root lp -
d /run/cups/certs 0511 lp sys -
d /var/spool/cups/tmp - - - 30d
EOF

cat > ${RPM_BUILD_ROOT}%{_tmpfilesdir}/cups-lp.conf <<EOF
c /dev/lp0 0660 root lp - 6:0
c /dev/lp1 0660 root lp - 6:1
c /dev/lp2 0660 root lp - 6:2
c /dev/lp3 0660 root lp - 6:3
EOF

find ${RPM_BUILD_ROOT} -type f -o -type l | sed '
s:.*\('%{_datadir}'/\)\([^/_]\+\)\(.*\.po$\):%lang(\2) \1\2\3:
/^%lang(C)/d
/^\([^%].*\)/d
' > %{name}.lang

%pre

%preun
%systemd_preun %{name}.path %{name}.socket %{name}.service
%systemd_preun cups-lpd.socket

%post

%systemd_post %{name}.path %{name}.socket %{name}.service

install -d ${RPM_BUILD_ROOT}%{_localstatedir}/run/cups/certs

/bin/sed -i -e "s,^PageLogFormat,#PageLogFormat,i" %{_sysconfdir}/cups/cups-files.conf

%systemd_post cups-lpd.socket
exit 0

%post libs -p /sbin/ldconfig

%postun

%systemd_postun_with_restart %{name}.path %{name}.socket %{name}.service
%systemd_postun_with_restart cups-lpd.socket
exit 0

%postun libs -p /sbin/ldconfig

%triggerin -- samba-client
ln -sf %{_libexecdir}/samba/cups_backend_smb %{_exec_prefix}/lib/cups/backend/smb || :
exit 0

%triggerun -- samba-client
[ $2 = 0 ] || exit 0
rm -f %{_exec_prefix}/lib/cups/backend/smb

%files -f %{name}.lang
%dir %attr(0755,root,lp) %{_sysconfdir}/cups
%dir %attr(0755,root,lp) %{_localstatedir}/run/cups
%dir %attr(0511,lp,sys) %{_localstatedir}/run/cups/certs
%{_tmpfilesdir}/cups.conf
%{_tmpfilesdir}/cups-lp.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0640,root,lp) %{_sysconfdir}/cups/cupsd.conf
%attr(0640,root,lp) %{_sysconfdir}/cups/cupsd.conf.default
%verify(not md5 size mtime) %config(noreplace) %attr(0640,root,lp) %{_sysconfdir}/cups/cups-files.conf
%attr(0640,root,lp) %{_sysconfdir}/cups/cups-files.conf.default
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/client.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0600,root,lp) %{_sysconfdir}/cups/classes.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0600,root,lp) %{_sysconfdir}/cups/printers.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/snmp.conf
%attr(0640,root,lp) %{_sysconfdir}/cups/snmp.conf.default
%verify(not md5 size mtime) %config(noreplace) %attr(0640,root,lp) %{_sysconfdir}/cups/subscriptions.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/lpoptions
%dir %attr(0755,root,lp) %{_sysconfdir}/cups/ppd
%dir %attr(0700,root,lp) %{_sysconfdir}/cups/ssl
%config(noreplace) %{_sysconfdir}/pam.d/cups
%config(noreplace) %{_sysconfdir}/logrotate.d/cups
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/cups.conf

%dir %{_datadir}/cups/data
%dir %{_datadir}/cups/drv
%dir %{_datadir}/cups/mime
%dir %{_datadir}/cups/model
%dir %{_datadir}/cups/ppdc
%dir %{_datadir}/ppd
%exclude %{_mandir}/cat?
%exclude %{_mandir}/*/cat?
%exclude %{_datadir}/applications/cups.desktop
%exclude %{_datadir}/icons
%exclude %{_datadir}/cups/banners
%exclude %{_datadir}/cups/data/testprint

%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket
%{_unitdir}/%{name}.path
%{_unitdir}/cups-lpd.socket
%{_unitdir}/cups-lpd@.service
%{_bindir}/cupstestppd
%{_bindir}/cupstestdsc
%{_bindir}/ppd*
%{_bindir}/cancel*
%{_bindir}/lp*
%{_bindir}/ipptool
%{_bindir}/ippfind
%{_sbindir}/*
%{_sbindir}/lpc.cups

%{_exec_prefix}/lib/cups/backend/*
%{_exec_prefix}/lib/cups/cgi-bin
%dir %{_exec_prefix}/lib/cups/driver
%dir %{_exec_prefix}/lib/cups/daemon
%{_exec_prefix}/lib/cups/daemon/cups-deviced
%{_exec_prefix}/lib/cups/daemon/cups-driverd
%{_exec_prefix}/lib/cups/daemon/cups-exec
%{_exec_prefix}/lib/cups/notifier
%{_exec_prefix}/lib/cups/filter/*
%{_exec_prefix}/lib/cups/monitor
%{_exec_prefix}/lib/cups/daemon/cups-lpd

%{_datadir}/cups/templates/*.tmpl
%{_datadir}/cups/templates/de/*.tmpl
%{_datadir}/cups/templates/fr/*.tmpl
%{_datadir}/cups/templates/es/*.tmpl
%{_datadir}/cups/templates/ja/*.tmpl
%{_datadir}/cups/templates/ru/*.tmpl
%{_datadir}/cups/templates/pt_BR/*.tmpl
%dir %attr(1770,root,lp) %{_localstatedir}/spool/cups/tmp
%dir %attr(0710,root,lp) %{_localstatedir}/spool/cups
%dir %attr(0755,lp,sys) %{_localstatedir}/log/cups
%{_datadir}/pixmaps/cupsprinter.png

%{_datadir}/cups/drv/sample.drv
%{_datadir}/cups/examples
%{_datadir}/cups/mime/mime.types
%{_datadir}/cups/mime/mime.convs
%{_datadir}/cups/ppdc/*.defs
%{_datadir}/cups/ppdc/*.h

%{_datadir}/%{name}/www/images
%{_datadir}/%{name}/www/*.css
%dir %{_datadir}/%{name}/usb
%{_datadir}/%{name}/usb/org.cups.usb-quirks
%dir %{_datadir}/cups/ipptool
%{_datadir}/cups/ipptool/*

%files libs
%{license} LICENSE.txt
%{_libdir}/lib*.so.*

%files devel
%{_bindir}/cups-config
%{_libdir}/*.so
%{_includedir}/cups
%{_rpmconfigdir}/macros.d/macros.cups

%files help
%{_mandir}/man[1578]/*
%{_mandir}/man1/cancel-cups.1.gz
%{_mandir}/man1/cups-config.1.gz
%{_mandir}/man1/ipptool.1.gz
%{_mandir}/man1/lp*.1.gz
%{_mandir}/man5/ipptoolfile.5.gz
%{_mandir}/man8/cups-lpd.8.gz
%{_mandir}/man8/lpc-cups.8.gz

%doc README.md CREDITS.md CHANGES.md
%doc %{_datadir}/%{name}/www/index.html
%doc %{_datadir}/%{name}/www/help
%doc %{_datadir}/%{name}/www/robots.txt
%doc %{_datadir}/%{name}/www/de/index.html
%doc %{_datadir}/%{name}/www/es/index.html
%doc %{_datadir}/%{name}/www/ja/index.html
%doc %{_datadir}/%{name}/www/ru/index.html
%doc %{_datadir}/%{name}/www/pt_BR/index.html
%doc %{_datadir}/%{name}/www/apple-touch-icon.png

%changelog
* Thu Mar 26 chenzhen <chenzhen44@huawei.com> - 2.2.8-9
- Type:cves
- ID:CVE-2019-2228
- SUG:restart
- DESC: fix CVE-2019-2228

* Sat Jan 11 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.2.8-8
- Type:enhancement
- ID:NA
- SUG:NA
- DESC: delete patches

* Wed Sep 25 2019 gaoguanghui <gaoguanghui1@huawei.com> - 2.2.8-7
- Type:cves
- ID:CVE-2019-8675 CVE-2019-8696
- SUG:restart
- DESC:fix CVE-2019-8675 CVE-2019-8696

* Wed Sep 18 2019 Guan Yanjie <guanyanjie@huawei.com> - 2.2.8-6
- Package init
