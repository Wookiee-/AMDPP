# AMDPP

A small system tray app for Fedora KDE that switches the power profile and the AMD energy performance preference (EPP) on Ryzen CPUs using `amd-pstate-epp`.

## Features

- Tray icon with a menu for the power profile: Power Saver, Balanced, Performance.
- EPP submenu with all five levels: `power`, `balance_power`, `balance_performance`, `performance`, `default`.
- Tooltip and menu header showing the current profile and EPP.
- Remembers your last choice and restores it when you log in.

## Requirements

- Fedora with KDE Plasma (tested on Fedora 45).
- An AMD CPU using `amd-pstate-epp`.
- `tuned-ppd` (provides the `org.freedesktop.UPower.PowerProfiles` D-Bus API).
- `python3-pyside6`, `sudo`.

## Installing

Build the RPM from this repo:

```sh
mkdir -p ~/rpmbuild/SOURCES
mkdir -p /tmp/amdpp-1.0 && cp -r power-tray amd.png set-epp packaging /tmp/amdpp-1.0/
tar -C /tmp -czf ~/rpmbuild/SOURCES/amdpp-1.0.tar.gz amdpp-1.0
rpmbuild -bb packaging/amdpp.spec
sudo dnf install ~/rpmbuild/RPMS/noarch/amdpp-1.0-*.fc45.noarch.rpm
```

The package installs:

- `/usr/bin/amdpp`: starts the tray app.
- `/usr/share/amdpp/`: the app and its icon.
- `/usr/libexec/set-epp`: root helper that writes the EPP value to every CPU.
- `/etc/sudoers.d/amdpp`: lets members of the `wheel` group run only the helper without a password.
- `/etc/xdg/autostart/amdpp.desktop`: starts the app at login.

## Usage

Run `amdpp`, or log out and back in. Click the tray icon to see the menu. Choose a profile or an EPP level to apply it.

Changing the profile also resets EPP to that profile's default, so set EPP after switching profiles.

## How it works

- **Profile:** set through the `ActiveProfile` property of `org.freedesktop.UPower.PowerProfiles` on the system D-Bus. No root needed.
- **EPP:** written to `/sys/devices/system/cpu/cpufreq/policy*/energy_performance_preference` by `/usr/libexec/set-epp`. The helper accepts only the five valid values and checks that the CPU supports the value. If the passwordless `sudo` call fails, the app falls back to `pkexec`, which asks for a password.
- **Saved state:** the last profile and EPP are stored in `~/.config/power-tray/state.json`.

## Uninstalling

```sh
sudo dnf remove amdpp
rm -rf ~/.config/power-tray
```

## License

MIT
