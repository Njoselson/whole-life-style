<!--
Sync Impact Report:
Version change: 1.2.0 → 1.3.0
Modified principles:
  - III. Financial Accuracy & Auditability: Added hybrid model calculations (term + permanent life, property NOI, rental income)
  - V. Documentation & Record-Keeping: Added cooperative governance, property management, rental income documentation
Added sections:
  - Hybrid Model Requirements (new subsection under Financial Modeling)
  - Property Acquisition & Management Requirements (new subsection)
  - Cooperative Governance Principles (new subsection)
Removed sections: None
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section exists and aligns
  ✅ spec-template.md - No principle-specific references found
  ✅ tasks-template.md - No principle-specific references found
  ✅ checklist-template.md - No principle-specific references found
  ✅ agent-file-template.md - No principle-specific references found
Follow-up TODOs: None
-->

# Whole Life Style Constitution

**Project Purpose**: This project facilitates cooperative property acquisition through a hybrid insurance model. Two tiers: (1) regular members carry term life at $20/mo, pooling death benefits as group collateral; (2) founders/whales carry permanent life through a Life Insurance LLC, building cash value as secondary collateral. The combined borrowing power enables the cooperative to acquire real estate, with rental income and carrying charges creating sustainable revenue.

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

TDD mandatory: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. All features MUST have corresponding tests before implementation begins. Financial calculations MUST have verified test cases with known expected results. Legal workflow processes MUST be testable and verifiable. Integration tests required for financial calculations, regulatory compliance checks, and document generation workflows.

**Rationale**: Financial accuracy and legal process correctness are non-negotiable. Tests ensure calculations are correct, workflows comply with regulations, and prevent costly errors in insurance policy management and mortgage applications.

### II. Legal & Regulatory Compliance (NON-NEGOTIABLE)

All features MUST comply with applicable laws and regulations including: insurance regulations (state and federal), corporate law (formation, governance, documentation), mortgage/finance regulations, tax compliance requirements. Legal reviews required for features affecting corporate structure, policy ownership, or collateral arrangements. Regulatory changes MUST be tracked and incorporated promptly. Document generation MUST produce legally valid forms and filings.

**Rationale**: Non-compliance risks legal liability, regulatory penalties, and invalidates the entire strategy. Legal compliance is foundational to the project's purpose.

### III. Financial Accuracy & Auditability

All financial calculations MUST be accurate, traceable, and verifiable. Financial data MUST maintain complete audit trails with timestamps, source documents, and calculation methodologies. Policy values, cash value calculations, and collateral assessments MUST be based on authoritative sources (policy documents, insurance company statements). Financial reports MUST be reproducible and verifiable by third parties (lenders, auditors, regulators).

**Specific Calculation Requirements:**
- Policy cash value tracking and projections (guaranteed rates, actual performance, tax-deferred growth)
- Loan amortization schedules (principal, interest, balloon payments, remaining balance)
- Debt Service Coverage Ratio (DSCR) calculations: traditional (NOI-based) and adjusted (member contribution-based)
- Loan-to-cash-value ratios (must not exceed 90% for collateral loans)
- Member contribution calculations (bifurcated: loan service + insurance premiums)
- Premium allocation modeling (age-based fairness, cost distribution)
- Buyout funding gap analysis (equity stake vs. available cash value)
- Policy growth rate vs. loan interest rate analysis (prevents policy lapse risk)

**Rationale**: Financial accuracy is critical for insurance policy management, collateral valuation, and mortgage qualification. Lenders rely on these calculations to assess loan viability. Audit trails enable verification, dispute resolution, and regulatory compliance.

### IV. Data Privacy & Security

Financial and legal documents MUST be protected with industry-standard security practices. Encrypt sensitive information at rest and in transit: policy numbers, Social Security Numbers, financial account details, corporate documents. Implement proper access controls and audit logging for all document access. Comply with applicable regulations (HIPAA for health information in insurance applications, financial privacy regulations). Security vulnerabilities must be addressed immediately. Never log sensitive financial or personal identifiers.

**Rationale**: Financial and legal documents contain highly sensitive information. Breaches could result in identity theft, financial fraud, or legal exposure.

### V. Documentation & Record-Keeping

All corporate actions, policy transactions, and mortgage applications MUST be fully documented. Maintain version control for all legal documents and corporate records. Generate required corporate minutes, resolutions, and filings. Preserve complete records of policy ownership, beneficiary designations, and collateral assignments. Documentation MUST meet legal requirements for corporate governance and mortgage underwriting.

**Required Legal Documents:**
- LLC Operating Agreement (member rights, premium allocation, governance structure)
- Buy-Sell Agreement (member exit scenarios: death, disability, retirement, voluntary departure)
- Lifecycle Buy-Sell provisions (cash value-based living buyouts)
- Collateral Assignment documentation (lender beneficiary rights, assignment amounts)
- Premium Allocation Plan (fair distribution addressing age disparity)
- Member Admission/Exit documentation (process, capital contributions, ownership interests)
- Corporate governance records (minutes, resolutions, filings)

**Loan Application Package Requirements:**
- Comprehensive business plan (explains member-contribution model, policy strategy)
- Financial pro forma projections (integrated real estate + life insurance model)
- Unified financial statements (collective LLC + individual member summaries)
- Legal document compilation (operating agreement, buy-sell agreement, collateral assignments)
- Risk mitigation documentation (buy-sell funding, policy portfolio diversification)
- Member financial stability evidence (credit scores, net worth, contribution capacity)

**Rationale**: Proper documentation is legally required for corporate operations, policy administration, and mortgage qualification. Lenders require comprehensive documentation to evaluate non-traditional loan structures. Incomplete records can invalidate corporate protections or mortgage applications.

### VI. Observability & Monitoring

Structured logging required for all operations with special attention to financial transactions and legal workflows. Application MUST emit metrics for policy value tracking, corporate compliance status, and mortgage application progress. Errors MUST be logged with sufficient context for debugging. Financial transactions MUST be traceable through correlation IDs. Audit logs MUST be tamper-evident and retained per regulatory requirements.

**Rationale**: Financial and legal processes require complete visibility. Audit logs support compliance verification and dispute resolution. Monitoring enables proactive issue detection.

### VII. Simplicity & Maintainability

YAGNI (You Aren't Gonna Need It) principles apply. Start simple and add complexity only when justified. Code MUST be readable and self-documenting. Complexity violations MUST be documented in implementation plans with justification. Prefer clear, straightforward solutions over clever abstractions, especially for financial calculations and legal processes where clarity prevents errors.

**Rationale**: Simple, clear code reduces errors in critical financial and legal calculations. Maintainability ensures the system remains accurate and compliant as regulations evolve.

## Development Workflow

### Code Review Process

All code changes require review before merge. Reviews MUST verify constitution compliance, test coverage, and code quality. Financial calculations require special scrutiny for accuracy. Legal workflow changes require verification of regulatory compliance. Reviewers should check that tests pass and that new features align with user stories from specifications.

### Quality Gates

Before any feature is considered complete:
- All tests MUST pass (especially financial calculation tests)
- Code review approval obtained
- Constitution compliance verified
- Legal/regulatory compliance confirmed (for applicable features)
- Documentation updated (required for legal/document features)
- Financial accuracy verified (for calculation features)
- User acceptance criteria met

### Branch Strategy

Feature branches follow the pattern: `[###-feature-name]`. Main branch remains deployable at all times. Hotfixes follow the same review process as features. Financial or legal workflow hotfixes require expedited but thorough review.

## Security Requirements

### Authentication & Authorization

Implement secure authentication mechanisms appropriate for the platform. Multi-factor authentication REQUIRED for all financial and legal document access. Role-based access control (RBAC) required: separate roles for corporate officers, policy administrators, and auditors. Principle of least privilege: users have minimum necessary access.

### Data Handling

Encrypt sensitive data at rest and in transit using industry-standard encryption (AES-256 minimum). Never log passwords, tokens, SSNs, policy numbers, or other sensitive credentials. Implement proper input validation and sanitization to prevent injection attacks. Use parameterized queries for database operations. Secure document storage with access controls and audit logging.

### Financial Data Protection

Financial documents and calculations MUST be protected with additional safeguards:
- Separate encryption keys for financial data
- Access logs for all financial document views/modifications
- Secure backup and recovery procedures
- Compliance with financial data retention requirements

### Dependency Management

Keep dependencies up to date and scan for known vulnerabilities. Use dependency pinning and security advisories. Review and approve new dependencies before adding to the project. Financial calculation libraries MUST be from reputable sources with verified accuracy.

### Incident Response

Security incidents involving financial or legal data must be reported immediately. Maintain an incident response procedure. Document all security-related changes and vulnerabilities. For financial data breaches, follow applicable breach notification requirements.

## Regulatory Compliance

### Insurance Compliance

Features handling insurance policies MUST comply with state and federal insurance regulations. Track policy state of domicile requirements. Maintain compliance with policy loan regulations and disclosure requirements.

### Corporate Compliance

Corporate structure features MUST comply with state corporate law (Delaware, New York, or applicable jurisdiction). Maintain proper corporate documentation: articles of incorporation, bylaws, minutes, resolutions. Track corporate governance requirements and filing deadlines.

### Mortgage/Finance Compliance

Mortgage application features MUST comply with mortgage lending regulations (TILA, RESPA, etc.). Maintain compliance with underwriting requirements. Document collateral valuation methodologies per lender requirements.

### Tax Compliance

Track tax implications of policy ownership, corporate structure, and property acquisition. Consult tax professionals for tax-related features. Maintain records required for tax reporting. Ensure LLC partnership taxation to avoid transfer-for-value rule. Track tax-deferred cash value growth and tax-free policy loans.

## Financial Modeling Requirements

### Pro Forma Financial Models

All financial models MUST integrate real estate assets with life insurance components. Models MUST include:
- Revenue/Expenses (property income, operating expenses)
- Debt Service (loan amortization schedules, interest calculations)
- Member Contributions (bifurcated allocation: loan service + insurance premiums)
- Cash Value Projections (policy growth, tax-deferred accumulation)
- Tiered Analysis Support (model different property value scenarios)

### Hybrid Model Requirements

The system MUST support the unified two-tier model:
- Term life pool for regular members ($20/mo, death benefit collateral only)
- Permanent life pool for founders/whales (higher premiums, cash value + death benefit)
- Combined borrowing power calculation: pool leverage + death benefit leverage + cash value leverage
- Founder premium funding from lump sum contributions (drawn from pool)
- Property acquisition model with rental income and carrying charges
- Net operating income (NOI) from mixed-use units (housing members + rental)

### Property Acquisition & Management Requirements

Property models MUST include:
- Purchase price, down payment, mortgage amortization
- Unit mix: housing member units (carrying charges) vs rental units (market rent)
- Carrying charge calculation: total building cost / total units
- Rental income projection from non-member units
- Net cashflow: total income - total expenses (including mortgage)
- DSCR calculations: traditional (NOI / debt service) and adjusted (NOI + contributions / debt service)
- Housing member economics: savings vs market rent, share purchase cost

### Lender Presentation Requirements

Financial models MUST support lender evaluation by:
- Calculating Adjusted DSCR (member contributions / debt service)
- Demonstrating member financial capacity (individual and collective)
- Showing policy portfolio diversification (risk mitigation)
- Modeling buyout funding adequacy (cash value vs. equity stake)
- Projecting policy performance vs. loan requirements (prevents lapse scenarios)

### Risk Assessment Modeling

Models MUST quantify and mitigate risks:
- Member financial stability tracking (credit scores, net worth, contribution capacity)
- Premium payment compliance monitoring
- Policy performance vs. loan interest rate analysis
- Buyout funding gap identification and solutions
- Insurance company rating tracking (insurer financial stability)

## Cooperative Governance Principles

### Democratic Control
- One member, one vote (not dollar-weighted)
- Board elected annually by membership
- Supermajority required for major decisions (property, loans, amendments)

### Member Tiers
- Tier 1 (Base): $20/mo, term life, voting, pool equity, credit building
- Tier 2 (Housing): Tier 1 + unit in property, carrying charges
- Tier 3 (Founder/Whale): Tier 1 + permanent life, enhanced equity, board seat eligibility

### Micro-Cooperative Bootstrap Path
- Cooperative may start with as few as 2 founding members (e.g., a married couple)
- Group insurance discounts scale with membership: none under 10, partial at 10-24, full at 25+
- Growth modeled in named waves: Inner Circle, Word of Mouth, Track Record, Community, Full Scale
- Financial projections MUST be honest about small-group economics (higher per-person premiums)
- Property readiness milestones tracked at each growth stage

### Entity Structure
- Fraternal Benefit Society [501(c)(8)] as parent
- Life Insurance LLC (partnership taxed) for permanent policies
- Property Holding LLC for real estate
- Cooperative Pool as operating account of parent society

### Revenue Model
- Property rental income from non-member units
- Carrying charges from housing members (below-market)
- Net operating income reinvested into cooperative
- No speculative returns — revenue from being a landlord

## Lender Readiness Requirements

### Corporate Structure Integrity

The system MUST ensure the LLC structure meets lender expectations:
- Separate LLC for policy ownership (creditor protection, centralized administration)
- Partnership taxation (avoids transfer-for-value rule, provides stepped-up basis)
- Proper corporate governance (articles, bylaws, minutes, resolutions)
- Creditor insulation (policies protected from member and business creditors)

### Buy-Sell Agreement Robustness

The system MUST support comprehensive buy-sell agreements that address:
- Death scenarios (death benefit funding)
- Disability scenarios (funding mechanisms)
- Retirement scenarios (lifecycle buyout using cash value)
- Voluntary departure (living buyout process)
- Member admission procedures (new member integration)
- Premium allocation fairness (age-based cost distribution)

### Collateral Documentation

The system MUST generate and maintain collateral assignment documentation:
- Formal collateral assignment forms (lender beneficiary rights)
- Assignment amount tracking (loan balance vs. policy value)
- Remaining death benefit calculation (for LLC beneficiaries)
- Collateral valuation reports (cash value, death benefit)
- Policy status monitoring (active, premium payment compliance)

## Governance

This constitution supersedes all other development practices and guidelines. When conflicts arise, this document takes precedence.

### Amendment Procedure

Constitution amendments require:
1. Documentation of the proposed change and rationale
2. Review and approval by project maintainers
3. Legal review if amendment affects regulatory compliance principles
4. Version bump according to semantic versioning:
   - **MAJOR**: Backward incompatible principle removals or redefinitions
   - **MINOR**: New principles added or materially expanded guidance
   - **PATCH**: Clarifications, wording improvements, typo fixes
5. Update of affected templates and documentation
6. Communication of changes to all contributors

### Compliance Review

All pull requests and code reviews MUST verify compliance with constitution principles. Implementation plans MUST include a "Constitution Check" section that validates alignment. Financial calculations MUST be verified for accuracy. Legal workflows MUST be verified for regulatory compliance. Violations must be justified in complexity tracking tables or resolved before merge.

### Runtime Guidance

For day-to-day development guidance, refer to the agent development guidelines file (auto-generated from feature plans) and relevant feature specifications in `/specs/`.

**Version**: 1.4.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2026-03-07
