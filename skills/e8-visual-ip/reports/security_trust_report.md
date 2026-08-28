# Security Trust Report

- OK: `True`
- Scanned files: `42`
- Scripts: `4`
- Internal script modules: `0`
- Secret findings: `0`
- Network-capable scripts: `0`
- Network policy covered scripts: `0`
- Network policy missing scripts: `0`
- File-write scripts: `1`
- Permission approvals: `1 / 1`
- Permission approval gaps: `0`
- CLI help smoke checked: `4`
- CLI help smoke failures: `0`
- Interactive scripts: `0`
- Package hash scope: `source-contract-without-generated-reports`
- Package hash files: `42`
- Package SHA256: `2910f87d6eadd813b74d25163cad0f6c1e345242e4f4503e9034d3340f09da33`

## Failures

- None

## Warnings

- None

## Dependency Evidence

- Files: `requirements.txt`
- Pinned entries: `0`
- Unpinned entries: `0`

## Network Policy

- Policy file: `security/network_policy.json`
- Present: `False`
- Covered scripts: `0`
- Missing scripts: `none`
- Mismatches: `0`

## Permission Governance

- Policy file: `security/permission_policy.json`
- Present: `True`
- Required capabilities: `file_write`
- Approved capabilities: `file_write`
- Missing approvals: `none`
- Invalid approvals: `none`
- Expired approvals: `none`

## CLI Help Smoke

- Enabled: `True`
- Timeout seconds: `5.0`
- Checked scripts: `4`
- Passed scripts: `4`
- Failed scripts: `none`

## Script Surface

| Script | Interface | Declared | Argparse | Main Guard | Input | Network | File Write | Subprocess | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripts\character_pack.py | cli | True | True | True | False | False | True | False |  |
| scripts\validate_monochrome_run.py | cli | True | True | True | False | False | False | False |  |
| scripts\validate_pixel_run.py | cli | True | True | True | False | False | False | False |  |
| scripts\validate_style_registry.py | cli | True | True | True | False | False | False | False |  |
