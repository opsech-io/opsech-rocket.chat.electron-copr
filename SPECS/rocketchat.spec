%{?nodejs_find_provides_and_requires}
%global debug_package %{nil}
%global _hardened_build 1
%global __requires_exclude (npm)
%global __provides_exclude (npm)
%global project Rocket.Chat.Electron
%global repo %{project}
%global node_ver 4.6.2
%global _optdir /opt

# commit
%global _commit 21425565c2f962fd2cb3800c970d4d953b12b076
%global _shortcommit %(c=%{_commit}; echo ${c:0:7})

Name:    rocketchat
Version: 1.3.3
Release: 0.git%{_shortcommit}%{?dist}
Summary: Rocket.Chat Native Cross-Platform Desktop Application via Electron.
Group:   Applications/Communications
Vendor:  Rocket.Chat Community
License: MIT
URL:     https://rocket.chat/
Source0: https://github.com/RocketChat/Rocket.Chat.Electron/archive/%{_commit}/%{repo}-%{_shortcommit}.tar.gz
AutoReq: 0

Obsoletes: rocketchat == dev
Obsoletes: rocketchat <= 1.3.2

BuildRequires: npm
BuildRequires: git-core
BuildRequires: node-gyp
BuildRequires: nodejs >= %{node_ver}
BuildRequires: nodejs-packaging
BuildRequires: fakeroot
BuildRequires: nodejs
BuildRequires: libX11-devel libXScrnSaver-devel libXext-devel
#BuildRequires: electron >= 1.4.3

%description
From group messages and video calls all the way to helpdesk killer features.
Our goal is to become the number one cross-platform open source chat solution.

%prep
%setup -q -n %repo-%{_commit}
sed -ri '/^[ ]*\.then\((packTo(Deb|Rpm)File|cleanClutter)\)$/d' tasks/release/linux.js
sed -ri -e 's|^(Icon=).*|\1%{_datadir}/icons/hicolor/128x128/apps/%{name}.png|' \
    -e 's|^(Exec=).*|\1%{_bindir}/%{name}|' \
    resources/linux/app.desktop

npm config set python=`which python2`

%build
node-gyp -v; node -v; npm -v
find . -mindepth 1 -maxdepth 2 -type d -name 'node_modules' -exec rm -rvf '{}' \+
npm install n
%ifarch i686
N_PREFIX=$PWD ./node_modules/n/bin/n -a x86 %{node_ver}
%else
N_PREFIX=$PWD ./node_modules/n/bin/n %{node_ver}
%endif
./n/versions/node/%{node_ver}/bin/npm install
./n/versions/node/%{node_ver}/bin/npm run release

%install
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_optdir}/%{name}

#pushd tmp/%{name}-v%{version}-linux*
# 1.3.1 unitl they change the manifest
pushd tmp/%{name}-v*-linux*
install -Dm644 usr/share/applications/%{name}.desktop \
    %{buildroot}%{_datadir}/applications/%{name}.desktop
install -Dm644 opt/%{name}/icon.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
rm -f opt/%{name}/icon.png
cp -r opt/%{name}/* %{buildroot}%{_optdir}/%{name}/
popd
cat <<-EOF > %{buildroot}%{_bindir}/%{name}
    #!/bin/bash
    %{_optdir}/%{name}/%{name}
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:
/usr/bin/update-desktop-database &>/dev/null ||:

%postun
if [ $1 -eq 0 ]; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:
    /usr/bin/gtk-update-icon-cache -f -t -q %{_datadir}/icons/hicolor ||:
fi
/usr/bin/update-desktop-database &>/dev/null ||:

%posttrans
/usr/bin/gtk-update-icon-cache -f -t -q %{_datadir}/icons/hicolor ||:

%files
%defattr(-,root,root,-)
#%doc README.md
%attr(755,-,-) %{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_optdir}/%{name}

%changelog
* Fri Dec 23 2016 xenithorb <mike@mgoodwin.net> - 1.3.3-100.git2142556
- Development channel ver 1.3.3
- Upgrade node version to 4.6.2
- Electron version to 1.4.3
- Spellcheck support!
* Sat Jun 4 2016 xenithorb <mike@mgoodwin.net> - 1.3.1-0.git3ed2b6d
- Release 1.3.1
- Changed build to do exactly what is done for Ubuntu deb sans building .deb pkg
* Wed Mar 23 2016 mosquito <sensor.wen@gmail.com> - 1.2.0-2.gitf74b825
- Release 1.2.0
* Sat Mar 12 2016 mosquito <sensor.wen@gmail.com> - 1.2.0-1.gitabb7b81
- Initial package
