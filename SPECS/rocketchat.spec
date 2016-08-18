%{?nodejs_find_provides_and_requires}
%global debug_package %{nil}
%global _hardened_build 1
%global __requires_exclude (npm)
%global __provides_exclude (npm)

%global project Rocket.Chat.Electron
%global repo %{project}
%global node_ver 0.12
%global _optdir /opt

# commit
%global _commit df2dfb6ff8b4cbb2e8172954267ba5add8480ab0
%global _shortcommit %(c=%{_commit}; echo ${c:0:7})

Name:    rocketchat
Version: 1.3.1
Release: 4.git%{_shortcommit}%{?dist}
Summary: Rocket.Chat Native Cross-Platform Desktop Application via Electron.
Group:   Applications/Communications
Vendor:  Rocket.Chat Community
License: MIT
URL:     https://rocket.chat/
Source0: https://github.com/xenithorb/Rocket.Chat.Electron/archive/%{_commit}/%{repo}-%{_shortcommit}.tar.gz
AutoReq: 0
# npm after F24 is included in nodejs
%if 0%{?fedora} < 24
BuildRequires: npm
%endif
BuildRequires: git-core
BuildRequires: node-gyp
BuildRequires: nodejs >= 0.10.0
BuildRequires: nodejs-packaging
#Provides: libnode.so()(%{__isa_bits}bit), libffmpeg.so()(%{__isa_bits}bit)
#BuildRequires: electron <= 0.37.8

%description
From group messages and video calls all the way to helpdesk killer features.
Our goal is to become the number one cross-platform open source chat solution.

%prep
%setup -q -n %repo-%{_commit}
#sed -i '/electron-prebuilt/d' package.json
sed -ri 's|("electron-prebuilt.*?").*?(".*)|\10.37.8\2|' package.json
sed -ri '/^[ ]*\.then\((packToDebFile|cleanClutter)\)$/d' tasks/release/linux.js
#sed -ri 's|node_modules/electron-prebuilt/dist|%{_libdir}/electron|' tasks/release/linux.js
sed -ri -e 's|^(Icon=).*|\1%{_datadir}/icons/hicolor/128x128/apps/%{name}.png|' \
		-e 's|^(Exec=).*|\1%{_bindir}/%{name}|' \
		resources/linux/app.desktop

git clone https://github.com/creationix/nvm.git .nvm
source .nvm/nvm.sh
nvm install %{node_ver}
npm config set python=`which python2`

%build
node-gyp -v; node -v; npm -v
source .nvm/nvm.sh
nvm use %{node_ver}
pushd app/
npm install spellchecker --save
popd
npm install --loglevel error
node_modules/.bin/gulp release --env=production

%install
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_optdir}/%{name}

pushd tmp/%{name}-v%{version}-linux*
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
* Sat Jun 4 2016 xenithorb <mike@mgoodwin.net> - 1.3.1-0.git3ed2b6d
- Release 1.3.1
- Changed build to do exactly what is done for Ubuntu deb sans building .deb pkg
* Wed Mar 23 2016 mosquito <sensor.wen@gmail.com> - 1.2.0-2.gitf74b825
- Release 1.2.0
* Sat Mar 12 2016 mosquito <sensor.wen@gmail.com> - 1.2.0-1.gitabb7b81
- Initial package
