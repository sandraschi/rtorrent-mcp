# 📋 Changelog

All notable changes to **RTorrent MCP Server** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of RTorrent MCP Server
- rTorrent SCGI API integration
- NYAA.si anime search with quality scoring
- Austrian legal compliance checking
- Natural language command processing (English/German)
- MCPB packaging support
- Comprehensive CI/CD pipeline
- Security scanning and vulnerability assessment
- Code quality tools (Black, isort, mypy, flake8)
- Unit and integration test suites
- Self-documenting tools with JSON schemas
- Claude Desktop integration guides

### Changed
- Switched from qBittorrent to rTorrent backend
- Updated to FastMCP 2.12 for better Claude integration
- Improved error handling and logging
- Enhanced security and privacy features

### Technical Details
- **Framework**: FastMCP 2.12
- **Backend**: rTorrent SCGI API
- **Search Engine**: NYAA.si
- **Legal Compliance**: Austria-focused
- **Languages**: English/German NLP support
- **Packaging**: MCPB bundles
- **CI/CD**: GitHub Actions with security scanning

---

## [1.0.0] - 2025-09-23

### Added
- Complete RTorrent MCP Server implementation
- Austrian legal compliance framework
- Multi-language natural language processing
- MCPB packaging for Claude Desktop
- Comprehensive documentation and guides
- Security and code quality tooling
- GitHub Actions CI/CD pipeline

### Changed
- Migrated from qBittorrent to rTorrent backend
- Updated to modern MCP standards (2.12)
- Improved user experience and error handling

### Technical Improvements
- Async/await implementation for better performance
- Structured logging throughout the application
- Type hints and comprehensive error handling
- Self-documenting API with JSON schemas
- Extensive test coverage (unit and integration)

---

## [0.1.0] - 2025-09-01

### Added
- Initial qBittorrent MCP Server prototype
- Basic torrent management functionality
- NYAA.si search integration
- Austrian legal compliance checks
- Natural language command processing

### Known Issues
- Limited to qBittorrent WebUI API
- Basic error handling
- Minimal test coverage

---

<!-- Release Notes Template

## [x.y.z] - YYYY-MM-DD

### Added
- New features and functionalities

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security-related changes

### Performance
- Performance improvements

### Documentation
- Documentation updates

### Dependencies
- Dependency updates

-->

---

## 📝 Release Notes

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process

1. **Development**: Features developed on `develop` branch
2. **Staging**: Merged to `main` for testing
3. **Release**: Tagged versions create GitHub releases
4. **Distribution**: MCPB packages published to registry

### Support

- **Latest**: Most recent stable release
- **LTS**: Long-term support versions (if applicable)
- **Nightly**: Development builds (not recommended for production)

### Migration Guide

#### From qBittorrent to rTorrent (v1.0.0)
- Update configuration to use rTorrent SCGI settings
- Install rTorrent with SCGI support
- Update MCP server configuration
- Test torrent operations with new backend

---

**Legend:**
- 🚀 New features
- 🔧 Improvements
- 🐛 Bug fixes
- 📚 Documentation
- 🔒 Security
- ⚡ Performance

---

*This changelog is automatically updated via CI/CD pipeline.*
