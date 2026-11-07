# AMDPP

A small system tray app that switches the power profile and the AMD energy performance preference (EPP) on Ryzen CPUs using `amd-pstate-epp`.

## Features

- Tray icon with a menu for the power profile: Power Saver, Balanced, Performance.
- EPP submenu with all five levels: `power`, `balance_power`, `balance_performance`, `performance`, `default`.
- Tooltip and menu header showing the current profile and EPP.
- Remembers your last choice and restores it when you log in.

## Requirements

- An AMD CPU using `amd-pstate-epp`.
- A D-Bus power profiles service: `power-profiles-daemon` or `tuned-ppd`.
- Python 3 with PySide6, and `sudo`.

## Installing

Packages are published on the [Releases](https://github.com/Wookiee-/AMDPP/releases) page:

- **Fedora/RHEL:** `amdpp-<version>-1.noarch.rpm`
- **Arch Linux:** `amdpp-<version>-1-any.pkg.tar.zst`
- **Debian/Ubuntu:** `amdpp_<version>_all.deb`

Install with your package manager, for example `sudo dnf install ./amdpp-*.noarch.rpm` on Fedora.

The packages install:

- `/usr/bin/amdpp`: starts the tray app.
- `/usr/share/amdpp/`: the app and its icon.
- `/usr/lib/amdpp/set-epp`: root helper that writes the EPP value to every CPU.
- `/etc/sudoers.d/amdpp`: lets members of the `wheel` or `sudo` group run only the helper without a password.
- `/etc/xdg/autostart/amdpp.desktop`: starts the app at login.

## Building

From a checkout, build every package format at once:

```sh
./scripts/build-packages.sh
```

Or pick one or more formats: `--rpm`, `--arch`, `--deb`. The output goes to `dist/packages/`. Building the RPM needs `rpmbuild`, the Arch package needs `makepkg`, and the DEB needs `dpkg-deb`.

Pushing a version tag such as `v1.0.0` runs the GitHub Actions workflow in `.github/workflows/build.yml`. It builds each format in its own container and publishes the packages to a GitHub release.

## Usage

Run `amdpp`, or log out and back in. Click the tray icon to see the menu. Choose a profile or an EPP level to apply it.

Changing the profile also resets EPP to that profile's default, so set EPP after switching profiles.

## How it works

- **Profile:** set through the `ActiveProfile` property of `org.freedesktop.UPower.PowerProfiles` on the system D-Bus. No root needed.
- **EPP:** written to `/sys/devices/system/cpu/cpufreq/policy*/energy_performance_preference` by `/usr/lib/amdpp/set-epp`. The helper accepts only the five valid values and checks that the CPU supports the value. If the passwordless `sudo` call fails, the app falls back to `pkexec`, which asks for a password.
- **Saved state:** the last profile and EPP are stored in `~/.config/power-tray/state.json`.

## Uninstalling

Remove the package with your package manager (`sudo dnf remove amdpp`, `sudo pacman -R amdpp`, or `sudo apt remove amdpp`). To delete saved settings as well:

```sh
rm -rf ~/.config/power-tray
```

## License

MIT
