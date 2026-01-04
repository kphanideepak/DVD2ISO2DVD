# DVD ↔ ISO Tool

A cross-platform graphical utility for converting DVDs to ISO images, with planned support for burning ISOs back to DVD.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### Phase 1 (Current)
- ✅ Convert physical DVD/CD to ISO image
- ✅ Cross-platform GUI using tkinter
- ✅ Automatic DVD drive detection
- ✅ Real-time progress tracking with speed & ETA
- ✅ Three-level verbosity logging (Normal/Verbose/Debug)
- ✅ Disc information display (type, size, filesystem)
- ✅ Post-copy ISO verification
- ✅ Auto-eject option after completion
- ✅ Cancel operation support

### Phase 2 (Planned)
- ⬜ Burn ISO images to DVD/CD
- ⬜ Burn speed selection
- ⬜ Post-burn verification
- ⬜ Multi-session disc support

## Requirements

### Python
- Python 3.8 or higher
- tkinter (usually included with Python)

### Operating System Dependencies

#### Windows
No additional software required. The tool uses built-in Windows components:
- PowerShell (included in Windows 7+)
- Windows API for drive detection

#### Linux
Install the following packages:

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install python3-tk genisoimage coreutils
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3-tkinter genisoimage coreutils
```

**Arch Linux:**
```bash
sudo pacman -S tk cdrtools coreutils
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python with tkinter support
brew install python-tk
```

## Installation

### Option 1: Direct Download
1. Download `dvd_iso_tool.py`
2. Run with Python (see Usage section)

### Option 2: Clone Repository
```bash
git clone https://github.com/kphanideepak/DVD2ISO2DVD.git
cd DVD2ISO2DVD
```

### Verify Installation
```bash
# Check Python version
python --version  # Should be 3.8+

# Check tkinter is available
python -c "import tkinter; print('tkinter OK')"
```

## Usage

### Running the Application

#### Windows
```powershell
# Using python command
python dvd_iso_tool.py

# Or double-click the file if .py is associated with Python
```

#### Linux
```bash
# Make executable (first time only)
chmod +x dvd_iso_tool.py

# Run with Python
python3 dvd_iso_tool.py

# Or run directly
./dvd_iso_tool.py
```

#### macOS
```bash
python3 dvd_iso_tool.py
```

### Converting a DVD to ISO

1. **Insert DVD** - Place the DVD you want to convert into your optical drive

2. **Launch the application** - Run the script using the commands above

3. **Select source drive** - The application auto-detects DVD drives. Click "Refresh" if your drive isn't listed

4. **Choose output location** - Click "Browse..." to select where to save the ISO file

5. **Configure options** (optional):
   - Enable "Verify ISO after copy" to verify the created ISO
   - Enable "Auto-eject" to eject the disc when done
   - Set log level to "Verbose" or "Debug" for detailed progress

6. **Start conversion** - Click "Start Conversion" to begin

7. **Monitor progress** - Watch the progress bar showing:
   - Transfer speed (MB/s)
   - ETA (estimated time remaining)
   - Bytes copied / total bytes
   - Detailed log output (based on verbosity level)

8. **Complete** - A success message appears when finished, showing the ISO file size and average speed

### Command Line Arguments

Currently, the tool operates through its GUI only. Command-line support is planned for future releases.

## Troubleshooting

### Common Issues

#### "No DVD drives detected"
- **Cause**: No optical drive found or disc not inserted
- **Solution**: 
  - Insert a disc into the drive
  - Click the "Refresh" button
  - On Linux, check if user has permission to access `/dev/sr0`

#### Permission Denied (Linux)
```bash
# Add user to cdrom group
sudo usermod -aG cdrom $USER

# Log out and back in, or run:
newgrp cdrom
```

#### tkinter Not Found
**Windows:**
```powershell
# Reinstall Python, ensuring "tcl/tk and IDLE" is checked
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

**macOS:**
```bash
brew reinstall python-tk
```

#### Conversion Fails Immediately
- Ensure the disc is not scratched or damaged
- Try cleaning the disc
- Check if the disc is copy-protected (some commercial DVDs have protection)

#### Slow Conversion Speed
- Normal DVD read speeds vary from 1x to 16x
- A full single-layer DVD (~4.7GB) takes approximately:
  - 1x speed: ~60 minutes
  - 8x speed: ~8 minutes
  - 16x speed: ~4 minutes

### Platform-Specific Notes

#### Windows
- Run as Administrator if encountering permission issues
- Windows Defender may briefly scan the application on first run

#### Linux
- Requires read access to `/dev/sr*` devices
- Some distributions may require `wodim` package for future burn functionality

#### macOS
- Grant "Full Disk Access" in System Preferences if prompted
- On Apple Silicon Macs, ensure Rosetta 2 is installed for some dependencies

## Technical Details

### How It Works

| Platform | Read Method | Write Method (Phase 2) |
|----------|-------------|------------------------|
| Windows  | PowerShell direct sector read | IMAPI2 COM interface |
| Linux    | `dd` with progress | `wodim` / `cdrecord` |
| macOS    | `hdiutil` | `hdiutil burn` |

### File Format

The tool creates standard ISO 9660 images with Joliet extensions for long filename support. These ISO files are compatible with:
- Virtual drive software (VirtualBox, VMware, etc.)
- Disc burning software
- Operating system mount features

### Supported Disc Types

| Type | Read | Write (Phase 2) |
|------|------|-----------------|
| DVD-ROM | ✅ | N/A |
| DVD-R | ✅ | ✅ |
| DVD+R | ✅ | ✅ |
| DVD-RW | ✅ | ✅ |
| DVD+RW | ✅ | ✅ |
| CD-ROM | ✅ | N/A |
| CD-R | ✅ | ✅ |
| CD-RW | ✅ | ✅ |

## Project Structure

```
dvd-iso-tool/
├── dvd_iso_tool.py    # Main application
├── README.md          # This file
├── LICENSE            # MIT License
└── CHANGELOG.md       # Version history
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/kphanideepak/DVD2ISO2DVD.git
cd DVD2ISO2DVD

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run the application
python dvd_iso_tool.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.1.0 (Phase 1 Enhanced)
- Three-level verbosity logging (Normal/Verbose/Debug)
- Real-time speed and ETA display
- Disc information display (type, size, filesystem)
- Post-copy ISO verification option
- Auto-eject option after completion
- Enhanced progress tracking with bytes copied

### v1.0.0 (Phase 1)
- Initial release
- DVD to ISO conversion
- Cross-platform support (Windows, Linux, macOS)
- GUI with progress tracking

## Acknowledgments

- Built with Python and tkinter
- Uses native OS tools for reliable disc operations

## Support

- **Issues**: [GitHub Issues](https://github.com/kphanideepak/DVD2ISO2DVD/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kphanideepak/DVD2ISO2DVD/discussions)

---

**Note**: This tool is intended for backing up discs you own. Please respect copyright laws in your jurisdiction.
