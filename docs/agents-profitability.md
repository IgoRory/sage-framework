# Profitability — Agent Context and Repository Guide

**Location in this repo:** `docs/agents-profitability.md` (canonical product context).

In the **Profitability application repository**, expose this content to agents via Cursor **Project Rules**, `@`-references, or a path your team agrees on. Root **`AGENTS.md`** there is reserved for the **SAGE Framework Agent Catalogue** (framework-wide agent roles), not this product guide.

This document is read by any AI agent before taking action on Profitability code. It provides orientation context, domain knowledge, coding conventions, and workflow rules. Read it completely before making changes.

---

## 1. What this product is

**Profitability** is a bank and credit union profitability analytics
platform built by Empyrean Solutions. It calculates and reports
profitability metrics at instrument, customer, department, and
enterprise levels — including FTP (Funds Transfer Pricing), NII
(Net Interest Income), expense and income allocations, capital
adequacy, credit risk, and RAROC.

The platform has two product surfaces sharing the same codebase:
- **Full Profitability** (`prof_client_type_id = 1`) — complete
  multi-step calculation engine with full allocation methodology
- **Org Profitability** (`prof_client_type_id = 2`) — organisation-
  level profitability with a subset of the calculation workflow

Behaviour, workflow links, and page validations differ between the
two surfaces. Always check which surface a feature targets before
implementing. When `prof_client_type_id` is not specified, assume
Full Profitability (1) unless the PRD states otherwise.

---

## 2. Architecture

### Dependency graph

```
Web/ProfitabilityWeb          (Angular 19 SPA)
        ↓ HTTP + WebSocket (/ws)
Services/ProfitabilityAPI     (ASP.NET Core 8 Web API)
        ↓ project references
Libraries/Empyrean.Data       (Dapper data access + DTOs)
Libraries/Empyrean.WS         (WebSocket pipeline)
        ↓
Database/                     (SQL Server — stored procedures,
                               tables, functions, views)
```

### Layer responsibilities

**`Database/`**
SQL script library. Not an SSDT project. ~47 domain folders
containing approximately 112 tables (`.tbl`), 348 stored
procedures (`.prc`), 87 functions (`.fnc`), 38 views (`.vw`),
and 76 loose migration/BI `.sql` files.

**`Libraries/Empyrean.Data`**
- Solution: `Libraries/Empyrean.Data/Empyrean.Data.sln`
- Namespace: `Empyrean.Data`
- Contains: `Empyrean.Data.Models.*` (DTOs per domain),
  `Empyrean.Data.SharedService` (~55 `*DAL.cs` files using Dapper),
  `Empyrean.Data.Helpers`, `Empyrean.Data.Services`
- Role: Data access layer and DTOs. Consumed entirely by
  `ProfitabilityAPI`. Does not reference `Empyrean.WS`.

**`Libraries/Empyrean.WS`**
- Solution: `Libraries/Empyrean.WS/Empyrean.WS.sln`
- Namespace: `Empyrean.WS`
- Contains: WebSocket middleware, handlers, connection manager,
  tasks, interfaces, models, utilities
- Role: WebSocket pipeline mounted at `/ws` in the API.
  Does not reference `Empyrean.Data`.

**`Services/ProfitabilityAPI`**
- Solution: `ProfitabilityAPI.sln` (includes all three projects)
- Namespace: `ProfitabilityAPI`
- Contains: 54 controllers (one per domain), services, DAL pairs,
  DI installer extensions
- Infrastructure: Serilog, Swashbuckle, IdentityServer4,
  Azure Key Vault, Newtonsoft.Json, `EmpyreanSolutions.Authorization`,
  `EmpyreanSolutions.Multitenant`

**`Web/ProfitabilityWeb`**
- Package: `profitability-web`
- Framework: Angular 19.2, NgModule-based (not standalone root)
- Contains: ~40+ lazy-loaded feature modules, 60+ HTTP services,
  80+ TypeScript model subfolders
- Key libraries: Kendo UI, Angular Material, SpreadJS, oidc-client,
  ngx-toastr, RxJS 7.8, Azure Blob Storage client

---

## 3. Domain concepts

### Calculation engine

The calculation engine runs steps in the order defined in
`Database/Calculations/100_INSERT_ProfitabilityCalculations.sql`.
The primary calculation domains and their entry stored procedures:

| Domain | Key stored procedure(s) |
|---|---|
| Fees & Revenue | `prRunFeesAndRevenueCalculations` |
| FTP / NII | `prRunFTPNIICalculations` |
| Expense Allocation | `prRunTotalExpensesCalculations`, `prGenerateDeptLevelExpenseAllocations` |
| Income Methodology | `prRunIncomeMethodologyCalculations`, `prGenerateDeptLevelIncomeAllocations` |
| Capital & ACL | `prRunACLCalculations`, `prRunCapitalTotalCalculations`, `prRunLoanProvisionCapitalCalculations` |
| Credit Risk | `prRunCreditRiskCalculations`, `prRunGLOCreditRiskCalculations` |
| Op & Market Risk | `prRunOpAndMktRiskCalculations` |
| NIBT / NIAT | `prRunNIBTCalculations`, `prRunNIATCalculations` |
| Dept-to-Dept | `prRunDeptToDeptAllocationCalculations` |
| RAROC / Reporting | `prRunRAROCReportSummary`, `prRunExpenseReportSummary` |
| Global / Dept Results | `prCalculateGlobalResultsByDep` |

### Most important tables

**Calculation workflow:**
- `ProfitabilityCalculations` — registry of which SPs run and in
  what order
- `ProfitabilityCalculationsProcess` / `ProcessLink` / `ProcessStatus`
  — workflow state machine
- `CalculationsParameters` / `CalculationsParamLink` — parameterisation
- `CalculationActionLog` — audit trail

**Results:**
- `GlobalResult` — the wide profitability statement table with
  columns for FTP, NII, fees, capital, PPNR, NIAT, RAROC, etc.
- `Global_Result_Calc_Metadata` — expression-driven definitions for
  each GL line item (metadata-driven output — not hardcoded)
- `ReportSummaryCalculations`, `ExpenseReportSummaryCalculations_*`

**Allocation rules:**
- `Allocation_Rule*`, `Allocation_Rule_Set*`, `Allocation_Protocol`,
  `Allocation_Properties`
- `ExpenseAllocationLog`, `ExpenseAllocationLog_Instrument`,
  `ExpenseAllocationLog_Department`
- `IncomeAllocationRule*`, `IncomeAllocationLog`,
  `IncomeAllocationDefinition`
- `ExpenseMethodology*`, `IncomeMethodology`

**Dimensions:**
- `BusinessUnit`, `Department`, `Branch`, `Territory`, `Location`
- `CommercialProduct`, `RetailProduct`, `CommercialCustomerArchive`
- `RelationshipManager`, `Employee`, `Position`
- `Transactions`, `TransactionLink`

**Configuration:**
- `ProfitabilitySetting` / `ProfitabilitySettings` — key-value
  application settings
- `GlobalSettingMonthly` / `GlobalSettingMonthlyValue` — monthly
  time-scoped settings
- `Type_Codes` — admin dropdowns; `AccessFlag` values:
  1 = Full Profitability, 2 = Org Profitability, 3 = Both
- `Page`, `PageProcessLink`, `PageDependencyLink` — UI page to
  workflow linkage

### Cross-cutting key fields

| Field | Role |
|---|---|
| `AsOfDate` / `as_of_date` | Monthly run date — primary time key across nearly every table |
| `process_id` | Two distinct meanings: (1) workflow step ID in `ProfitabilityCalculationsProcess`, (2) GL posting flavour in `Adjusted_GL` (resolved via `fnGetAdjustedGLProcessID('...')`) |
| `prof_client_type_id` | 1 = Full Profitability, 2 = Org Profitability — controls which workflow links, pages, and wrappers fire |
| `*_sid` keys | Surrogate keys throughout: `business_unit_sid`, `department_sid`, `allocation_group_sid`, `global_result_sid`, `instrument_*_sid`, etc. |
| `row_sid`, `user_id_created/modified`, `record_status` | Standard audit / row-identity pattern across most tables |
| `Adjusted_GL` | Core integration point for FTP, capital, provisions, and departmental allocations. DDL lives outside this repo but is heavily referenced. Always use `fnGetAdjustedGLProcessID('...')` to resolve the correct `process_id` for GL flavour operations. |
| Measure column suffixes | `_SumAll`, `FTPCredit_SumAll`, `FTPCharge_SumAll`, `RAROC_All` — aligned with `GlobalResult` output columns |

### Two important architectural patterns

**Metadata-driven results:** `GlobalResult` columns are driven by
expression and GL-account definitions in `Global_Result_Calc_Metadata`.
Profitability statement lines are configurable, not hardcoded.
Never hardcode a result line — reference the metadata table.

**Dual product surface:** `prof_client_type_id` 1 vs 2 differentiates
Full Profitability from Org Profitability. Same underlying tables and
SPs; different process links and page validations. Features that affect
both surfaces must be tested against both.

---

## 4. Tech stack

| Layer | Technology |
|---|---|
| Frontend framework | Angular 19.2, TypeScript 5.8 |
| UI components | Kendo UI for Angular 19, Angular Material 19.2, GrapeCity SpreadJS 18 |
| Frontend state | RxJS 7.8 |
| Authentication (frontend) | `oidc-client` — OIDC/OAuth |
| Frontend unit tests | Vitest 4 (`@analogjs/vitest-angular`) |
| Frontend E2E tests | Playwright 1.56 |
| Frontend build | Angular CLI 19.2, Vite 6 (`@analogjs/vite-plugin-angular`) |
| Backend framework | ASP.NET Core 8 Web API |
| Data access | Dapper 2.1 + Dapper.FluentMap 2.0 → SQL Server |
| Serialisation | Newtonsoft.Json 13 |
| Logging | Serilog 4 with AspNetCore, File, Async sinks |
| API docs | Swashbuckle 6.6 (Swagger/OpenAPI) |
| Authentication (backend) | IdentityServer4 4.1.2, `AccessTokenValidation` |
| Secrets | Azure Key Vault (`Azure.Security.KeyVault.Secrets 4.2`) |
| Internal auth/tenancy | `EmpyreanSolutions.Authorization` 5.0.22, `EmpyreanSolutions.Multitenant` 5.0.2 |
| WebSocket | `Empyrean.WS` (custom library, mounted at `/ws`) |
| Idle detection | `@ng-idle/core` |
| File export | `file-saver`, Azure Blob Storage client |

---

## 5. Coding conventions

### .NET — Controllers

- Class naming: `PascalCase` + `Controller` suffix
  (`DepartmentController`, `ExpenseAllocationRuleController`)
- Location: `Services/ProfitabilityAPI/ProfitabilityAPI/Controllers/`
- Inherit from `Controller` (not `ControllerBase`)
- Route attribute: `[Route("api/[controller]")]`
  → URLs become `api/Department`, `api/CalculationRunner`, etc.
- Most use `[ApiController]`; a few older controllers omit it —
  match the existing pattern in the controller you are working in
- Sub-actions use explicit path strings:
  `[HttpGet("DepartmentsForPostingAccounts")]`, `[HttpPost("Run")]`
- Authorization: `[Authorize(Policy = ProfitabilityPolicies...)]`
- DI via C# 12 primary constructors:
  `DepartmentController(DepartmentService _service, ILogger<Department> _logger)`

### .NET — Services and DALs

- Naming: `XxxService.cs` paired with `XxxDAL.cs`
- Location: `Services/ProfitabilityAPI/ProfitabilityAPI/Services/`
- Most services are concrete classes without interfaces — registered
  directly: `AddScoped<ConcreteService>()`
- Use interfaces selectively and only where they already exist
  (e.g. `IExpenseAllocationMethodologyRepository`) — do not add
  `IXxxService` interfaces unless the PRD or architect requires it
- All DI registrations go in `Extensions/Installers/DataAccessInstaller.cs`
  via the `InstallDataAccess(this IServiceCollection services)`
  extension method
- Namespace: `ProfitabilityAPI.Services` (use this consistently;
  avoid `OrgProfitabilityAPI.Services`)

### .NET — DAL patterns

- Use Dapper for all data access
- Use `Dapper.FluentMap` for column → property mapping
- All SQL calls invoke stored procedures — no inline SQL
- Connection strings resolved via `EmpyreanSolutions.Multitenant`
  (multi-tenant connection management) — do not hardcode
  connection strings

### Angular — Components

- File naming: `kebab-case` for files and folders
- Class naming: `PascalCase` + `Component` suffix
  (`expense-allocation-method.component.ts` →
  `ExpenseAllocationMethodComponent`)
- Always three files per component:
  `.component.ts` · `.component.html` · `.component.scss`
- Folder structure: feature-nested kebab-case directories:
  `components/expense-allocation/expense-allocation-rules/
  expense-allocation-method/`
- **Existing components:** `standalone: false`, declared in NgModules
- **New components:** `standalone: true` per workspace standards
  (the codebase is in transition — check the feature module you are
  working in and match the pattern in that module)
- Selectors: `app-*` prefix for feature components,
  `emp-*` for core/shared components
- Use path aliases — never use relative `../../` imports across
  feature boundaries:
  `@core/*`, `@components/*`, `@models/*`, `@services/*`,
  `@shared/*`, `@guards/*`, `@routes/*`

### Angular — Services

- File naming: `name.service.ts`
- Class naming: `XxxService`
- Always `@Injectable({ providedIn: 'root' })` for singletons
- HTTP calls use `HttpClient` with typed observables
- All service files in `src/app/services/` or co-located in
  feature module where domain-specific

### Angular — Routing

- URL segments: `kebab-case`
  (`calculation-workflow`, `summarized-reports/detail`)
- Lazy-loaded via `loadChildren` pointing to `*.module.ts`
- Route guards: `AuthGuardService`, `AsOfDateGuard`
- Route `data: { page: ... }` for page titles and metadata

### SQL — Stored procedures

- Naming prefix: `pr` for procedures, `fn` for functions,
  `vw` for views
- All Adjusted_GL process_id values resolved via
  `fnGetAdjustedGLProcessID('...')` — never pass a raw integer
- All procedures should include `SET NOCOUNT ON`
- Error handling: use `TRY...CATCH` blocks with `RAISERROR` or
  `THROW` for meaningful error propagation
- Audit fields: always populate `user_id_created`,
  `user_id_modified`, `date_created`, `date_modified` where the
  target table has them
- Use surrogate key `*_sid` for all FK references — never join
  on business keys directly

---

## 6. Workflow context

This repository uses an AI-assisted Sprint development
workflow. The workflow is governed by two directories:

**`.cursor/`** — Cursor agent definitions, skills, hooks, and rules.
All AI agents operating in this repo are defined in `agents/`.
All hook scripts that enforce build gates live in `hooks/`.
All skills (prd-completeness-check, prd-interviewer, kickoff-dev-review,
phase-splitter, dev-plan, session-performance-evaluator, skill-effectiveness-evaluator)
live in `skills/`.

**`.sage/`** — Workflow runtime. Session manifests live in
`.sage/sessions/[LIN-feature-id]/`. Workflow policy lives in
`.sage/workflow-config.json`. The active session path is in
`.sage/sessions/active-session.txt`.

All new feature work is tracked in Linear (not ADO). Linear issue IDs
appear in branch names (`LIN-[id]-phase-N-[objective]`) and commit
messages. ADO is used for CI/CD pipeline execution only.

The legacy session artifacts from prior mob sessions are in
`docs/sage-session/` and `docs/sage-session/` — do not write
new session artifacts there. All new session artifacts go to
`.sage/sessions/[LIN-id]/`.

---

## 7. What agents must not do

Read this section carefully before taking any action.

**Do not modify Pyramid Analytics or IMDB.**
The Pyramid Analytics data model and IMDB are separate systems
maintained by a different team (Sriyanka). They are explicitly
out of scope for all Profitability build phases unless the PRD
explicitly states otherwise with Sriyanka's sign-off.
If you identify that a feature requires Pyramid changes, stop
and surface it — do not implement it.

**Do not write to files outside your phase scope.**
In a Sprint build sprint, each phase owns specific
files listed in `manifest.phases[N].definition.scopedFiles`.
You own only those files. If you identify that a file outside
your scope needs to change, record it in your completion report
under "items requiring coordination" — do not make the change.

**Do not write inline SQL.**
All data access goes through stored procedures called via Dapper.
Never write inline SQL strings in C# code. If a required stored
procedure does not exist, it belongs in a database phase.

**Do not add IXxxService interfaces speculatively.**
The codebase uses concrete service classes without interfaces
by default. Do not add an interface unless it already exists
for that service or the PRD explicitly requires it.

**Do not hardcode connection strings.**
Connection management is handled by `EmpyreanSolutions.Multitenant`.
Never hardcode a SQL Server connection string anywhere in the codebase.

**Do not skip the required_references check.**
Before writing any implementation code in S5, every file listed
in `manifest.phases[N].definition.requiredReferences` must be
read. The `beforeShellExecution` hook enforces this — you will
be blocked if you attempt to write code before reading the
required files. This is not optional.

**Do not combine S7 and S8.**
S7 (agent testing) and S8 (completion report) are separate steps.
The S8 stop hook will block completion report generation unless
`phase-N-test-results.md` exists with `STATUS: PASS`. There is
no path to S8 without S7 completing successfully.

**Do not modify `Adjusted_GL` schema.**
The `Adjusted_GL` DDL lives outside this repository. You can
read from and write to `Adjusted_GL` following the established
patterns (via `fnGetAdjustedGLProcessID` and the relevant stored
procedures), but you cannot create or alter the table itself.

**Do not use `OrgProfitabilityAPI.Services` as a namespace.**
Use `ProfitabilityAPI.Services` consistently. The `OrgProfitabilityAPI`
namespace exists as a minor inconsistency in a few older files —
do not propagate it.

---

## 8. Code standards references

All generated code must conform to:

- **Angular standards:** `docs/cursor/angularStandards.md`
- **SQL standards:** `docs/cursor/sqlStandards.md`

Read these files before generating any Angular TypeScript or
SQL stored procedure code. They are not suggestions — they are
required conventions. If this is your first action in this repo,
read both files now.

---

## 9. Quick reference

| Item | Value |
|---|---|
| API base route | `api/[ControllerName]` |
| WebSocket endpoint | `/ws` |
| Angular path aliases | `@core/*` `@components/*` `@models/*` `@services/*` `@shared/*` |
| DI registration | `Extensions/Installers/DataAccessInstaller.cs` |
| Calculation engine entry | `Database/Calculations/100_INSERT_ProfitabilityCalculations.sql` |
| Session artifacts | `.sage/sessions/[LIN-id]/` |
| Active session pointer | `.sage/sessions/active-session.txt` |
| Workflow policy | `.sage/workflow-config.json` |
| Agent definitions | `agents/` |
| Hook scripts | `hooks/scripts/` |
| Skills | `skills/` |
| Angular standards | `docs/cursor/angularStandards.md` |
| SQL standards | `docs/cursor/sqlStandards.md` |
| Tech stack doc | `docs/techStack.md` |
| Testing strategy | `docs/testingStrategy.md` |
