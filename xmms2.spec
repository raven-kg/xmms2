%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?ruby_sitearch: %global ruby_sitearch %(ruby -rrbconfig -e 'puts Config::CONFIG["sitearchdir"] ')}

%global codename DrNo

Name:			xmms2
Summary: 		A modular audio framework and plugin architecture
Version:		0.7
Release:		1%{?dist}
License:		LGPLv2+ and GPLv2+ and BSD
Group:			Applications/Multimedia
# We can't use the upstream source tarball as-is, because it includes an mp4 decoder.
# http://downloads.sourceforge.net/xmms2/%{name}-%{version}%{codename}.tar.bz2
# Cleaning it is simple, just rm -rf src/plugins/mp4
Source0:		%{name}-%{version}%{codename}-clean.tar.bz2
Source1:		xmms2-client-launcher.sh
# Use libdir properly for multilib
Patch1:			xmms2-0.7DrNo-use-libdir.patch
# Set default output to pulse
Patch2:			xmms2-0.6DrMattDestruction-pulse-output-default.patch
# Don't add extra CFLAGS, we're smart enough, thanks.
Patch4:			xmms2-0.7DrNo-no-O0.patch
# More sane versioning
Patch5:			xmms2-0.7DrNo-moresaneversioning.patch
URL:			http://wiki.xmms2.xmms.se/
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:		sqlite-devel, flac-devel, libofa-devel
BuildRequires:		libcdio-devel, libdiscid-devel, libsmbclient-devel
BuildRequires:		libmpcdec-devel, gnome-vfs2-devel, jack-audio-connection-kit-devel
BuildRequires:		fftw-devel, libsamplerate-devel, libxml2-devel, alsa-lib-devel
BuildRequires:		libao-devel, libshout-devel, Pyrex, ruby-devel, ruby
BuildRequires:		perl-devel, boost-devel, pulseaudio-libs-devel, avahi-glib-devel
BuildRequires:		libmodplug-devel, ecore-devel, gamin-devel
BuildRequires:		avahi-compat-libdns_sd-devel, doxygen
BuildRequires:		libvisual-devel, wavpack-devel, SDL-devel
BuildRequires:		glib2-devel, readline-devel, ncurses-devel

%description
XMMS2 is an audio framework, but it is not a general multimedia player - it 
will not play videos. It has a modular framework and plugin architecture for 
audio processing, visualisation and output, but this framework has not been 
designed to support video. Also the client-server design of XMMS2 (and the 
daemon being independent of any graphics output) practically prevents direct 
video output being implemented. It has support for a wide range of audio 
formats, which is expandable via plugins. It includes a basic CLI interface 
to the XMMS2 framework, but most users will want to install a graphical XMMS2 
client (such as gxmms2 or esperanza).

%package devel
Summary:	Development libraries and headers for XMMS2
Group:		Development/Libraries
Requires:	glib2-devel, boost-devel
Requires:	pkgconfig
Requires:	%{name} = %{version}-%{release}

%description devel
Development libraries and headers for XMMS2. You probably need this to develop
or build new plugins for XMMS2.

%package docs
Summary:	Development documentation for XMMS2
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description docs
API documentation for the XMMS2 modular audio framework architecture.

%package python
Summary:	Python support for XMMS2
Group:		Applications/Multimedia
Requires:	%{name} = %{version}-%{release}

%description python
Python bindings for XMMS2.

%package perl
Summary:	Perl support for XMMS2
License:	GPL+ or Artistic
Group:		Applications/Multimedia
Requires:	%{name} = %{version}-%{release}
Requires:	perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description perl
Perl bindings for XMMS2.

%package ruby
Summary:	Ruby support for XMMS2
Group:		Applications/Multimedia
Requires:	%{name} = %{version}-%{release}
Requires:	ruby(abi) = 1.8

%description ruby
Ruby bindings for XMMS2.

%package -n nyxmms2
Summary:	Commandline client for XMMS2
Group:		Applications/Multimedia
Requires:	%{name} = %{version}-%{release}

%description -n nyxmms2
nyxmms2 is the new official commandline client for XMMS2. It can be run in
either shell-mode (if started without arguments), or in inline-mode where
it executes the command passed as argument directly.

%prep
%setup -q -n %{name}-%{version}%{codename}
%patch1 -p1 -b .plugins-use-libdir
%patch2 -p1 -b .default-output-pulse
%patch4 -p1 -b .noO0
%patch5 -p1 -b .versionsanity

# This header doesn't need to be executable
chmod -x src/include/xmmsclient/xmmsclient++/dict.h

# Clean up paths in wafadmin
WAFADMIN_FILES=`find wafadmin/ -type f`
for i in $WAFADMIN_FILES; do
	sed -i 's|/usr/lib|%{_libdir}|g' $i
done
sed -i 's|"lib"|"%{_lib}"|g' wscript

%build
export CFLAGS="%{optflags}"
export CPPFLAGS="%{optflags}"
export LIBDIR="%{_libdir}"
./waf configure --prefix=%{_prefix} --libdir=%{_libdir} --with-ruby-libdir=%{ruby_sitearch} --with-perl-archdir=%{perl_archlib} --with-pkgconfigdir=%{_libdir}/pkgconfig -j1
./waf build -v %{?_smp_mflags}
# make the docs
doxygen

%install
rm -rf %{buildroot}
export LIBDIR="%{_libdir}"
export python_LIBDEST="%{python_sitearch}"
./waf install --destdir=%{buildroot} --prefix=%{_prefix} --libdir=%{_libdir} --with-ruby-libdir=%{ruby_sitearch} --with-perl-archdir=%{perl_archlib} --with-pkgconfigdir=%{_libdir}/pkgconfig

# exec flags for debuginfo
chmod +x %{buildroot}%{_libdir}/%{name}/* %{buildroot}%{_libdir}/libxmmsclient*.so* %{buildroot}%{python_sitearch}/xmmsclient/xmmsapi.so \
	%{buildroot}%{perl_archlib}/auto/Audio/XMMSClient/XMMSClient.so %{buildroot}%{ruby_sitearch}/xmmsclient_*.so

# Convert to utf-8
for i in %{buildroot}%{_mandir}/man1/*.gz; do
	gunzip $i;
done
for i in %{buildroot}%{_mandir}/man1/*.1 ChangeLog; do
	iconv -o $i.iso88591 -f iso88591 -t utf8 $i
	mv $i.iso88591 $i
done

install -m0755 %{SOURCE1} %{buildroot}%{_bindir}

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING COPYING.GPL COPYING.LGPL README TODO
%{_bindir}/%{name}*
%{_bindir}/vistest*
%{_libdir}/libxmmsclient*.so.*
%{_libdir}/%{name}
%{_mandir}/man1/%{name}*
%{_datadir}/pixmaps/%{name}*
%{_datadir}/%{name}

%files devel
%defattr(-,root,root,-)
%{_includedir}/%{name}/
%{_libdir}/libxmmsclient*.so
%{_libdir}/pkgconfig/%{name}-*.pc

%files docs
%defattr(-,root,root,-)
%doc doc/xmms2/html

%files perl
%defattr(-,root,root,-)
%{perl_archlib}/Audio/
%{perl_archlib}/auto/Audio/

%files python
%defattr(-,root,root,-)
%{python_sitearch}/xmmsclient/

%files ruby
%defattr(-,root,root,-)
%{ruby_sitearch}/xmmsclient*

%files -n nyxmms2
%defattr(-,root,root,-)
%{_bindir}/nyxmms2
%{_mandir}/man1/nyxmms2.*

%changelog
* Mon Jan 07 2013 Raven <raven_kg@megaline.kg> - 0.7-1
- Initial packaging for RERemix
