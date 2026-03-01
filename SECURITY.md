# Security Policy

## Supported Versions

Only the  branch receives security fixes.

| Branch | Supported |
|--------|----------|
| main   | Yes      |
| older  | No       |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please report vulnerabilities privately:

1. Email: security@detroitfamilyhomecare.com (or use GitHub private vulnerability reporting)
2. Include: affected version, description, reproduction steps, and potential impact.
3. You will receive acknowledgement within 72 hours and a resolution timeline.

## Basic Rules

- Do not post secrets, credentials, or tokens in issues, PRs, or comments.
- Do not include  files in commits ( is in ).
- JWT secrets and database credentials must be kept out of source control.

## Scope

In scope: authentication, authorization, data leakage, injection, misconfigurations.
Out of scope: DoS via intentional traffic flooding (no SLA at MVP stage).
