Name:           amdpp
Version:        1.0
Release:        1%{?dist}
Summary:        AMD power profile and energy preference tray control
License:        MIT
URL:            https://github.com/Wookiee-/AMDPP
BuildArch:      noarch
Source0:        %{name}-%{version}.tar.gz

Requires:       python3
Requires:       python3-pyside6
Requires:       sudo
Requires:       tuned-ppd

%description
System tray app for switching the power profile (power-saver, balanced,
performance) and the AMD energy performance preference (EPP). EPP changes go
through a root-owned helper that members of the wheel or sudo group may run
without a password.

%prep
%setup -q

%install
install -Dm0755 packaging/amdpp %{buildroot}%{_bindir}/amdpp
install -Dm0644 power-tray/power_tray.py %{buildroot}%{_datadir}/amdpp/power_tray.py
install -Dm0644 power-tray/amd.png %{buildroot}%{_datadir}/amdpp/amd.png
install -Dm0755 packaging/set-epp %{buildroot}%{_prefix}/lib/amdpp/set-epp
install -Dm0440 packaging/amdpp.sudoers %{buildroot}%{_sysconfdir}/sudoers.d/amdpp
install -Dm0644 packaging/amdpp.desktop %{buildroot}%{_sysconfdir}/xdg/autostart/amdpp.desktop

%files
%{_bindir}/amdpp
%{_datadir}/amdpp/
%{_prefix}/lib/amdpp/set-epp
%attr(0440,root,root) %{_sysconfdir}/sudoers.d/amdpp
%{_sysconfdir}/xdg/autostart/amdpp.desktop

%changelog
* Sat Nov 07 2026 Wookiee- - 1.0-1
- Initial package
