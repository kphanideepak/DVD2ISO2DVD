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
| 1.1.0 | 2025-01-04 | Phase 1 Enhanced - Verbose logging, speed/ETA, verification |
| 1.0.0 | 2025-01-04 | Initial release - DVD to ISO conversion |

[Unreleased]: https://github.com/kphanideepak/DVD2ISO2DVD/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/kphanideepak/DVD2ISO2DVD/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/kphanideepak/DVD2ISO2DVD/releases/tag/v1.0.0
