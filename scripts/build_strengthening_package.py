"""Build an allowlisted, deterministic public review ZIP; never include private data."""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
from pathlib import Path, PurePosixPath, PureWindowsPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = 'outputs/publication_archive_20260926'
OUTER_MANIFEST_SHA256 = '945518494e4d0fb4ea4865046470be0242178a39a504e676d03351f78e611093'
AUDIT = 'outputs/strengthening_20260926'
AUDIT_FILES = (
    'README.md', 'CLAIM_AUDIT.md', 'claims_audit.json',
    'REFERENCE_ROBUSTNESS.md', 'reference_robustness.json',
    'FAIRBANKS_REAUDIT.md', 'EPA_NATIVE_RECONSTRUCTION.md',
    'epa_native_reconstruction.json', 'SOURCE_RECOVERY_STATUS.md',
    'source_recovery.json', 'LEGACY_TEST_STATUS.md', 'legacy_test_status.json',
    'QA_SUMMARY.json', 'requirements.txt',
)
SCRIPTS = (
    'audit_strengthening_claims.py', 'audit_reference_robustness.py',
    'audit_fairbanks_strengthening.py', 'audit_epa_native_strengthening.py',
    'audit_strengthening_legacy.py', 'recover_strengthening_sources.py',
    'build_strengthening_package.py',
)
TESTS = (
    'test_strengthening_claims.py', 'test_reference_robustness.py',
    'test_fairbanks_strengthening.py', 'test_epa_native_strengthening.py',
    'test_source_recovery.py', 'test_strengthening_package.py',
)
BASE = ('.gitattributes', '.gitignore', 'PROJECT_STATE.md',
        'scripts/.gitattributes', 'tests/.gitattributes', 'tasks/.gitattributes',
        'outputs/cycle02/.gitattributes', f'{AUDIT}/.gitattributes',
        'tasks/CODEX_EVIDENCE_STRENGTHENING_20260926.md',
        'outputs/cycle02/appendix_c_2008_2009_daily.csv')


def safe_member(name):
    path = PurePosixPath(name)
    if (path.is_absolute() or '..' in path.parts or '\\' in name
            or PureWindowsPath(name).drive or ':' in name):
        raise ValueError('unsafe archive path')
    if any(part.lower() in ('private', 'raw', 'third_party', '__pycache__') for part in path.parts):
        raise ValueError('private/raw path prohibited')
    if path.suffix.lower() in ('.xlsx', '.xls', '.pdf', '.docx', '.zip', '.eml', '.msg'):
        raise ValueError('restricted artifact type prohibited')


def payload(root=ROOT):
    names = [*BASE, *(f'{AUDIT}/{p}' for p in AUDIT_FILES),
             *(f'scripts/{p}' for p in SCRIPTS), *(f'tests/{p}' for p in TESTS)]
    outer_manifest = root / ARCHIVE / 'SHA256SUMS.txt'
    if sha256(outer_manifest.read_bytes()).hexdigest() != OUTER_MANIFEST_SHA256:
        raise ValueError('frozen outer manifest identity changed')
    entries = []
    for line in outer_manifest.read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        safe_member(name)
        data = (root / ARCHIVE / name).read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f'frozen public archive hash mismatch: {name}')
        entries.append(f'{ARCHIVE}/{name}')
    if len(entries) != 29 or len(set(entries)) != 29:
        raise ValueError('frozen public archive membership changed')
    names += entries + [f'{ARCHIVE}/SHA256SUMS.txt']
    result = {}
    for name in names:
        safe_member(name)
        file_path = root / name
        if file_path.is_symlink():
            raise ValueError('symlink in public package')
        data = file_path.read_bytes()
        # New audit text is LF-normalized for cross-platform reproducibility.
        # The complete frozen archive is copied byte-for-byte, never normalized.
        if not name.startswith(ARCHIVE + '/'):
            data = data.replace(b'\r\n', b'\n')
        if name in result:
            raise ValueError('duplicate package member')
        result[name] = data
    result['START_HERE.md'] = (
        '# PFFLS evidence-strengthening return\n\n'
        'Read outputs/strengthening_20260926/README.md first.\n'
        'Candidate evidence only; no manuscript baseline change or merge.\n'
        'Raw EPA archives and private Fairbanks inputs/row ledgers are excluded.\n'
        'SHA256SUMS.txt authenticates every payload member; the sidecar hashes the ZIP.\n'
    ).encode()
    manifest = ''.join(f'{sha256(data).hexdigest()}  {name}\n'
                       for name, data in sorted(result.items()))
    result['SHA256SUMS.txt'] = manifest.encode()
    return result


def zip_bytes(members):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(members.items()):
            safe_member(name)
            info = zipfile.ZipInfo(name, (2026, 9, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compresslevel=9)
    return buffer.getvalue()


def build(destination, root=ROOT):
    destination = Path(destination).resolve()
    if destination.is_relative_to(root.resolve()):
        raise ValueError('build destination must be outside the repository')
    data = zip_bytes(payload(root))
    if destination.exists() and destination.read_bytes() != data:
        raise ValueError('different existing review ZIP; choose a new destination')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    digest = sha256(data).hexdigest()
    sidecar = destination.with_name(destination.name + '.sha256.txt')
    sidecar.write_text(f'{digest}  {destination.name}\n', encoding='ascii', newline='\n')
    return digest, len(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    digest, size = build(args.destination)
    print(f'SHA-256 {digest}; {size} bytes; {args.destination.name}')
