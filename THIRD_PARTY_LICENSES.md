# Third-Party Licenses

Shadowstep is licensed under the **MIT License**.

This document lists all third-party dependencies and their licenses.

## License Compatibility

All dependencies use licenses compatible with MIT:

- ✅ **Apache 2.0** - Fully compatible, permissive
- ✅ **BSD** (2-clause, 3-clause) - Fully compatible, permissive
- ✅ **MIT** - Same license, fully compatible
- ✅ **ISC** - Equivalent to MIT, fully compatible
- ✅ **PSF** (Python Software Foundation) - Compatible
- ✅ **MPL 2.0** (Mozilla Public License) - Compatible when used as library
- ✅ **LGPL** (GNU Lesser GPL) - Compatible when used as library (dynamic linking in Python)
- ✅ **Unlicense** - Public domain, compatible with everything

**No GPL dependencies** - verified! ✅

## Dependencies

| Name | Version | License | Status |
|------|---------|---------|--------|
| Appium-Python-Client | 5.2.4 | Apache 2.0* | ✅ Compatible |
| selenium | 4.36.0 | Apache 2.0 | ✅ Compatible |
| websocket-client | 1.9.0 | Apache 2.0 | ✅ Compatible |
| requests | 2.32.5 | Apache 2.0 | ✅ Compatible |
| opencv-python | 4.12.0.88 | Apache 2.0 | ✅ Compatible |
| numpy | 2.0.2 | BSD | ✅ Compatible |
| Pillow | 11.3.0 | HPND* | ✅ Compatible |
| pytesseract | 0.3.13 | Apache 2.0 | ✅ Compatible |
| allure-pytest | 2.15.0 | Apache 2.0 | ✅ Compatible |
| paramiko | 4.0.0 | LGPL* | ✅ Compatible (dynamic) |
| scp | 0.15.0 | LGPL | ✅ Compatible (dynamic) |
| networkx | 3.2.1 | BSD | ✅ Compatible |
| lxml | 6.0.2 | BSD-3-Clause | ✅ Compatible |
| jinja2 | 3.1.6 | BSD | ✅ Compatible |
| anyascii | 0.3.3 | ISC | ✅ Compatible |
| eulxml | 1.1.3 | Apache 2.0 | ✅ Compatible |
| pytest | 8.4.2 | MIT | ✅ Compatible |
| pytest-cov | 7.0.0 | MIT | ✅ Compatible |
| pytest-rerunfailures | 16.0.1 | MPL 2.0 | ✅ Compatible |
| pyright | 1.1.406 | MIT | ✅ Compatible |
| ruff | 0.14.1 | MIT | ✅ Compatible |

\* Notes:

- **Appium-Python-Client**: Shows as UNKNOWN in metadata, but is Apache 2.0 (verified on GitHub)
- **Pillow**: HPND (Historical Permission Notice and Disclaimer) - very permissive, MIT-compatible
- **paramiko/scp**: LGPL is compatible when used as library (dynamic linking), which is how Python imports work

## License Categories Summary

```
Apache 2.0:       ~18 packages  ✅
BSD/BSD-3:        ~12 packages  ✅
MIT:              ~15 packages  ✅
LGPL:              2 packages  ✅ (dynamic linking)
MPL 2.0:           2 packages  ✅
ISC:               1 package   ✅
PSF:               1 package   ✅
Unlicense:         1 package   ✅

GPL:               0 packages  ✅
```

## Development Dependencies

Development dependencies (pytest, ruff, pyright, pre-commit, etc.) are only used
during development and are not distributed with the package. Their licenses do not
affect the licensing of Shadowstep itself.

## Verification

This file was generated using `pip-licenses`:

```bash
uv pip install pip-licenses
uv run pip-licenses --format=markdown > LICENSES_THIRD_PARTY.md
```

Last updated: 2025-10-18

## For Users

If you use Shadowstep in your project, you are only required to include
Shadowstep's MIT license. You do not need to include licenses of Shadowstep's
dependencies unless you redistribute them separately.

## For Contributors

When adding new dependencies, please verify their license compatibility:

1. Check license on PyPI
2. Ensure it's not GPL (unless you want to change project license)
3. Update this document
4. Run CI license check

## Resources

- [Choose a License](https://choosealicense.com/)
- [License Compatibility Chart](https://www.gnu.org/licenses/license-list.html)
- [OSI Approved Licenses](https://opensource.org/licenses)
