# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 2: ISO to DVD burning functionality
- Burn speed selection
- Post-burn verification
- Command-line interface
- Multi-session disc support

## [1.2.0] - 2025-01-04

### Added
- **ISO → USB Feature**: Create bootable USB drives from ISO images
- Mode selector UI to toggle between DVD→ISO and ISO→USB modes
- Automatic ISO type detection (Windows vs Linux hybrid) by mounting and checking for Windows markers
- Support for Linux hybrid ISOs using direct DD write method
- **Full Windows ISO support** with dual partition scheme (FAT32 EFI + NTFS/ExFAT data)
- Handles Windows install.wim files >4GB that exceed FAT32 limits
- Boot mode selection (BIOS + UEFI / UEFI only / BIOS only)
- USB drive detection with device name, size, and path display
- Safety confirmation dialog before erasing USB drive data
- Real-time progress tracking for USB creation
- Cross-platform USB detection and writing (Windows, macOS, Linux)

### Changed
- Renamed application to "DVD & ISO Tool" to reflect expanded functionality
- Restructured UI with tabbed mode interface
- Increased window size to 650x850 for better layout
- Updated version to 1.2.0

### Technical
- Added `detect_iso_type()` for ISO classification (mounts ISO to check for sources/install.wim)
- Platform-specific USB detection: `_detect_usb_drives_windows()`, `_detect_usb_drives_macos()`, `_detect_usb_drives_linux()`
- DD write methods for all platforms: `_write_usb_dd_windows()`, `_write_usb_dd_macos()`, `_write_usb_dd_linux()`
- Windows ISO extract methods: `_write_usb_extract_windows()`, `_write_usb_extract_macos()`, `_write_usb_extract_linux()`
- Dual partition creation: 1GB FAT32 (EFI boot) + remaining space NTFS/ExFAT (Windows files)
- New instance variables for ISO→USB mode management
- Mode switching with `switch_mode()` using pack_forget/pack pattern

## [1.1.0] - 2025-01-04

### Added
- Three-level verbosity logging system (Normal/Verbose/Debug)
- Real-time transfer speed display (MB/s)
- ETA (estimated time remaining) calculation
- Bytes copied / total bytes display
- Disc information display (type, label, size, filesystem)
- Post-copy ISO verification option
- Auto-eject disc option after completion
- Average speed reporting on completion

### Changed
- Enhanced progress section with speed and ETA labels
- Improved Windows PowerShell script to output byte counts
- Linux dd monitoring now shows detailed progress
- macOS conversion gets disc size before starting

### Technical
- Added `format_size()`, `format_speed()`, `format_eta()` helper methods
- New `_monitor_with_bytes()` method for detailed progress tracking
- Platform-specific `get_disc_info()` and `eject_disc()` methods
- `verify_iso()` method for post-copy verification

## [1.0.0] - 2025-01-04

### Added
- Initial release with Phase 1 functionality
- DVD/CD to ISO conversion
- Cross-platform support for Windows, Linux, and macOS
- Graphical user interface using tkinter
- Automatic optical drive detection
- Real-time progress bar and status updates
- Detailed logging panel
- Cancel operation functionality
- Output file size reporting
- Drive refresh capability

### Technical
- Windows: PowerShell-based sector reading
- Linux: `dd` command with progress monitoring
- macOS: `hdiutil` integration

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.2.0 | 2025-01-04 | ISO → USB - Create bootable USB drives from ISO images |
| 1.1.0 | 2025-01-04 | Phase 1 Enhanced - Verbose logging, speed/ETA, verification |
| 1.0.0 | 2025-01-04 | Initial release - DVD to ISO conversion |

[Unreleased]: https://github.com/kphanideepak/DVD2ISO2DVD/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/kphanideepak/DVD2ISO2DVD/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/kphanideepak/DVD2ISO2DVD/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/kphanideepak/DVD2ISO2DVD/releases/tag/v1.0.0
