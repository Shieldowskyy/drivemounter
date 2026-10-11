Name:           drivemounter
Version:        1.0.0
Release:        1%{?dist}
Summary:        1:1 Windows Map Network Drive clone for KDE Plasma
BuildArch:      noarch

License:        MIT
URL:            https://github.com/Shieldowskyy/drivemounter
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3 >= 3.9
Requires:       python3-qt6
Requires:       cifs-utils
Requires:       samba-client
Recommends:     nfs-utils
Recommends:     davfs2
Recommends:     libnotify

%description
A pixel-perfect 1:1 recreation of the classic Windows Map Network Drive wizard,
built natively for KDE Plasma using PyQt6 and the native Breeze design system.
Seamlessly mount remote network storage (SMB, NFS, WebDAV) on Linux with the
familiar Windows workflow, drive letters (Z: down to D:), auto-reconnect,
Dolphin Places and context menu integration, and native desktop notifications.

%prep
%autosetup

%build
%py3_build

%install
%py3_install

# Install desktop shortcut
install -D -m 0644 drivemounter.desktop %{buildroot}%{_datadir}/applications/drivemounter.desktop

# Install Dolphin Service Menu
install -D -m 0644 drivemounter-service.desktop %{buildroot}%{_datadir}/kio/servicemenus/drivemounter.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/drivemounter
%{python3_sitelib}/drivemounter/
%{python3_sitelib}/drivemounter-%{version}-py*.egg-info
%{_datadir}/applications/drivemounter.desktop
%{_datadir}/kio/servicemenus/drivemounter.desktop

%changelog
* Sun Oct 11 2026 Krzysztof (Shieldziak) Tarczyński <32707076+Shieldowskyy@users.noreply.github.com> - 1.0.0-1
- Initial public RPM release of DriveMounter for Fedora / RHEL
