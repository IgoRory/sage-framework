# SAGE Security Standards

**Authority:** Empyrean Solutions SDLC Policy (sections 3.1, 3.7–3.12, Appendix 1)
**Framework:** OWASP Secure Coding Practices / OWASP Top 10
**Stack:** SQL Server / T-SQL · C# / .NET · Angular / TypeScript · Dataverse

These standards are read by the `security-reviewer` agent. Each rule cites the policy section that mandates it and carries a default severity used when the rule is violated. Severity may be upgraded to Critical if the violation is directly exploitable in context.

---

## Design intent (§3.1) — apply to all phases

Before reviewing code, consider these questions about the feature:

- How can this feature be misused?
- Does it cause unnecessary data exposure or unavailability?
- Does it expose an attack vector?
- Are data sources trusted or untrusted?
- Does it follow data minimisation — is only strictly necessary personal information collected, used, stored, and transferred?

Flag any implementation pattern that violates these principles regardless of which layer it appears in.

---

## Input validation (§3.7) — OWASP A03 Injection

| Rule | Default severity |
|------|-----------------|
| All user-supplied input must be validated for: character encoding, acceptable header/cookie values, expected data types / ranges / lengths / allowed characters | Major |
| User-supplied data must never be passed to any dynamic execution function — SQL strings, OS commands, eval() | Critical |
| SQL: all parameters passed via parameterised queries or `sp_executesql` with `@params` — no string concatenation | Critical |
| Angular: no direct assignment to `innerHTML`, `outerHTML`, or `document.write()` | Critical |
| Angular: `DomSanitizer.bypassSecurityTrust*` must not be used except in explicitly documented utility wrappers | Critical |
| Server-side validation is the definitive source — client-side validation is supplementary, never the sole check | Major |

---

## Authentication (§3.8) — OWASP A07 Identification and Authentication Failures

| Rule | Default severity |
|------|-----------------|
| Authentication is required for all resources except those explicitly and intentionally public — no implicit anonymous access | Critical |
| Authentication must be enforced on a trusted system (server), not on the client | Critical |
| Authentication must fail securely — failed auth must not reveal which part of the credential was wrong | Major |
| Credentials must not appear in source code, configuration files, or scripts — no hardcoded passwords or API keys | Critical |
| Account disabling after repeated invalid login attempts must not be bypassed or skipped in new auth paths | Major |

---

## Access management (§3.9) — OWASP A01 Broken Access Control

| Rule | Default severity |
|------|-----------------|
| Access controls must fail securely — denied by default, not permitted by default | Critical |
| ACL must be enforced on all API requests, including org context — a user authenticated for org A must not be able to access org B data | Critical |
| Authorisation must be resource-level, not just route-level — check that the authenticated user owns or has rights to the specific record | Critical |
| Access tokens must be created on a trusted system with sufficiently random identifiers | Major |
| Access tokens must not be exposed on insecure channels | Major |
| Logout paths must destroy active access tokens | Major |
| No passwords or credentials hardcoded in scripts, configuration, or source code (§3.9, §3.11) | Critical |

---

## Error handling and logging (§3.10) — OWASP A09 Security Logging and Monitoring Failures

| Rule | Default severity |
|------|-----------------|
| Sensitive information must not be disclosed in error responses — no stack traces, internal paths, schema details, or connection strings returned to clients | Major |
| Passwords, credentials, tokens, and session identifiers must never appear in log entries | Major |
| All significant system events must be logged (authentication, authorisation failures, data mutations) | Major |
| SQL error handling blocks must not swallow exceptions silently when they affect financial correctness | Major |

---

## Data protection (§3.11) — OWASP A02 Cryptographic Failures

| Rule | Default severity |
|------|-----------------|
| Principle of least privilege: user access restricted to required functionality and data | Major |
| All temporary copies of sensitive data must be removed once processing is complete | Major |
| Sensitive data must not be included in GET parameters or URL paths that may be logged or cached | Major |
| Caching must be disabled on pages or responses containing sensitive information | Major |
| No production data in non-production environments without explicit approval and access restriction | Major |
| Application comments must be removed from client-side code before deployment — do not leave debug notes, TODOs, or internal logic descriptions in Angular templates or compiled JS | Minor |
| PII and financial identifiers must not appear in log entries, error messages, or API URLs | Major |

---

## Communication security (§3.12) — OWASP A02 Cryptographic Failures

| Rule | Default severity |
|------|-----------------|
| All data transmission must use TLS — no plaintext HTTP for any authenticated or data-bearing endpoint | Critical |
| Failed TLS connections must not fall back to an insecure connection — `HttpClient` must not bypass SSL certificate validation | Critical |
| CORS configuration must not use wildcard origins (`*`) on authenticated endpoints | Major |

---

## SQL Server / T-SQL specifics

| Rule | Default severity |
|------|-----------------|
| Procedures must run under the minimum required permission set — avoid `WITH EXECUTE AS OWNER` unless explicitly justified | Major |
| `NOLOCK` / `READUNCOMMITTED` must not be used on financial balance or position tables | Major |
| No PII or financial data written to log tables in plaintext | Major |
| Dataverse boundary: no direct writes to GL or reference data from Profitability calculation logic unless an explicitly approved scoped contract requires it | Critical |
| Calculation or financial results written to Dataverse or equivalent result stores must include the process/execution ID and revision date context required by the scoped contract | Major |
| Audit trail fields (`CreatedBy`, `ModifiedBy`, timestamps) must be populated for all financial record writes | Major |

---

## C# / .NET specifics

| Rule | Default severity |
|------|-----------------|
| `BinaryFormatter` must not be used | Critical |
| JSON deserialisation of untrusted input must not enable polymorphic type handling without explicit allow-listing | Major |
| `Random` must not be used for security-sensitive values — use `RandomNumberGenerator` | Major |
| All controller actions must have an explicit `[Authorize]` or `[AllowAnonymous]` attribute | Critical |
| Financial mutations must be idempotent or protected against duplicate submissions | Major |

---

## Open source and third-party dependencies (§3.2.2, Appendix 1)

Any new dependency introduced in the scoped files must be checked against the following:

**Permitted licences (general):** Apache 2.0, BSD, MIT, ISC, Zlib, WTFPL, 0BSD, CC0

**Permitted licences (Python API only):** MPL 2.0, LGPL, LGPL 2.0, LGPL 3.0, PSF-2.0

**Prohibited without approval:** AGPL-3.0, GPL-3.0, CPAL-1.0, EUPL-1.2

| Rule | Default severity |
|------|-----------------|
| New dependency introduced without a pinned version (`>` or `*` version strings are prohibited) | Major |
| New dependency with a prohibited licence added without documented approval | Critical |
| New dependency introduced without an assigned owner documented in the PR or implementation plan | Minor |

---

## Scope notes

- Apply SQL standards to `.sql` files, stored procedure wrappers, and any raw SQL calls in DAL classes
- Apply C# standards to all `.cs` files in scope
- Apply Angular standards to `.ts` component/service files and `.html` templates
- Apply API standards to all controller classes and endpoint registrations
- Apply Dataverse / cross-cutting standards to any file that writes financial records, writes calculation results, or calls Dataverse-adjacent services
- Apply open source checks only when the implementation plan lists new dependencies or when package files are in the scoped file list
- If a scoped file does not touch a layer, skip that layer's checks for that file
