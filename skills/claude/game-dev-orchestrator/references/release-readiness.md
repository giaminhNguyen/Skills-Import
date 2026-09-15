# Workflow: Release Readiness Review

## Goal

Make an evidence-based ship/no-ship assessment for a candidate build.

## Review areas

1. Build identity: branch/commit, version, platform, configuration.
2. Required automated test results and smoke tests.
3. Known blockers and accepted known issues.
4. Crash/error telemetry available from candidate testing.
5. Performance against target budgets on representative hardware.
6. Save/data migration and backward/forward compatibility where applicable.
7. Networking/backend compatibility where applicable.
8. Content completeness, localization, platform services, entitlements, DLC/IAP as applicable.
9. Packaging/signing/store/platform requirements.
10. Rollback/hotfix path for live releases when applicable.

## Decision classes

- **READY** — required gates pass; remaining issues are accepted and non-blocking.
- **READY WITH ACCEPTED RISK** — release owner has explicitly accepted documented risk.
- **NOT READY** — one or more release blockers remain or required evidence is missing.

Do not convert missing critical evidence into a pass. Missing evidence for a mandatory gate is `NOT READY` unless the project's release policy explicitly allows an exception.

## Output

Return:

- candidate identity
- decision
- passed gates
- blockers
- accepted risks
- required actions before ship
- post-release monitoring focus
