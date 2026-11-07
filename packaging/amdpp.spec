Name:           amdpp
Version:        1.0
Release:        3%{?dist}
Summary:        AMD power profile and energy preference tray control
License:        MIT
BuildArch:      noarch
Source0:        %{name}-%{version}.tar.gz

Requires:       python3
Requires:       python3-pyside6
Requires:       sudo
Requires:       tuned-ppd

%description
System tray app for switching the power profile (power-saver, balanced,
performance) and the AMD energy performance preference (EPP). EPP changes go
through a root-owned helper that members of the wheel group may run without a
password.

%prep
%setup -q

%install
install -d %{buildroot}%{_datadir}/%{name}
install -m 0644 power-tray/power_tray.py %{buildroot}%{_datadir}/%{name}/power_tray.py
install -m 0644 amd.png %{buildroot}%{_datadir}/%{name}/amd.png

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/sh
exec python3 %{_datadir}/%{name}/power_tray.py "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

install -d %{buildroot}%{_libexecdir}
install -m 0755 set-epp %{buildroot}%{_libexecdir}/set-epp

install -d %{buildroot}%{_sysconfdir}/sudoers.d
install -m 0440 packaging/amdpp.sudoers %{buildroot}%{_sysconfdir}/sudoers.d/%{name}

install -d %{buildroot}%{_sysconfdir}/xdg/autostart
install -m 0644 packaging/amdpp.desktop %{buildroot}%{_sysconfdir}/xdg/autostart/%{name}.desktop

%files
%{_datadir}/%{name}/
%{_bindir}/%{name}
%{_libexecdir}/set-epp
%config(noreplace) %attr(0440,root,root) %{_sysconfdir}/sudoers.d/%{name}
%{_sysconfdir}/xdg/autostart/%{name}.desktop

%changelog
* Sat Nov 07 2026 tagmanpro - 1.0-1
- Initial package
