# Related-party screening — evidence queue

Period 2025-04-01 to 2026-03-31 · rules as of 2022-10-01 · extractor `stub` · resolver τ_high=90.0 τ_low=75.0 · graph 104 nodes / 95 edges

Counterparties screened: 37 · queue items: 13 · unresolved: 1 · resolution candidates needing a human: 0

Clauses in force: CA2013_2(76)(i)@2013-09-12, CA2013_2(76)(ii)@2013-09-12, CA2013_2(76)(iii)@2013-09-12, CA2013_2(76)(iv)@2013-09-12, CA2013_2(76)(v)@2013-09-12, CA2013_2(76)(viii)@2013-09-12, CA2013_Rule3@2014-07-17, LODR_2(1)(zb)(a)@2022-04-01, LODR_2(1)(zb)(b)@2022-04-01

Not evaluated (human judgment only): CA2013_2(76)(vi) — body corporate whose board/MD/manager is accustomed to act on the advice of a director or manager; CA2013_2(76)(vii) — person on whose advice a director or manager is accustomed to act; LODR_2(1)(zc)_purpose_and_effect — transaction with an unrelated party whose purpose and effect is to benefit a related party


## Ranked evidence queue

Ordering: evidence tier → undisclosed before disclosed → materiality tier → gross value → min confidence. No item is a conclusion.

| # | Counterparty | Item | Evidence tier | Materiality | Gross ₹cr | Min conf | Clause / signal | Mgmt list | Approvals |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Iyer Infra Private Limited (V005) | rule_hit | 0 registry-backed rule hit | below | 47.0 | 1.0 | CA2013_2(76)(iv) | **no** | AC none, SH not_required |
| 2 | Sunrise Agro Pvt Ltd (V003) | rule_hit | 0 registry-backed rule hit | below | 45.0 | 1.0 | CA2013_2(76)(iv) | **no** | AC none, SH not_required |
| 3 | Rao Family Holdings Pvt. Ltd. (V002) | rule_hit | 1 filing/books-backed rule hit | material (Reg 23) | 1800.0 | 1.0 | LODR_2(1)(zb)(a) | yes | AC ok, SH ok |
| 4 | Rao Family Holdings Pvt. Ltd. (V002) | rule_hit | 1 filing/books-backed rule hit | material (Reg 23) | 1800.0 | 1.0 | LODR_2(1)(zb)(b) | yes | AC ok, SH ok |
| 5 | Meridian Logistics Pvt Ltd (V001) | rule_hit | 1 filing/books-backed rule hit | >=10% of threshold | 310.0 | 1.0 | CA2013_2(76)(viii) | yes | AC ok, SH not_required |
| 6 | BHARAT COLDCHAIN PVT LTD (V004) | rule_hit | 2 rule hit via fuzzy name merge | below | 17.0 | 0.98 | CA2013_2(76)(iv) | **no** | AC none, SH not_required |
| 7 | Kavya Traders (V006) | rule_hit | 3 rule hit via extractor-proposed edge | below | 13.0 | 0.75 | CA2013_2(76)(iii) | **no** | AC none, SH not_required |
| 8 | Rao Warehousing Pvt Ltd (V007) | rule_hit | 3 rule hit via extractor-proposed edge | below | 11.0 | 0.8 | CA2013_2(76)(iv) | **no** | AC none, SH not_required |
| 9 | Rao Family Holdings Pvt. Ltd. (V002) | rule_hit | 3 rule hit via extractor-proposed edge | material (Reg 23) | 1800.0 | 0.7 | CA2013_2(76)(iv) | yes | AC ok, SH ok |
| 10 | Meridian Logistics Private Limited (V001) | reconciliation | 4 reconciliation variance | >=10% of threshold | 310.0 | 1.0 | variance ₹190.0 cr (158.3%) | yes | — |
| 11 | Apex Machinery Pvt Ltd (V013) | indicator | 5 indicator only | below | 40.0 | 0.5 | b:new_thinly_capitalised_vendor, c:advance_ahead_of_receipt | — | — |
| 12 | Coastal Agri Ventures Pvt Ltd (V009) | indicator | 5 indicator only | below | 30.0 | 0.5 | a:promoter_entity_is_shareholder | — | — |
| 13 | Greenfield Packaging Private Limited (V008) | indicator | 5 indicator only | below | 14.0 | 0.5 | a:shared_registered_address | — | — |

## Item detail

### 1. Iyer Infra Private Limited — rule_hit
- Clause: `CA2013_2(76)(iv)` (version `CA2013_2(76)(iv)@2013-09-12`), weakest origin: registry
- Path: P4 -DIRECTOR_OF(registry,1.0)→ E5 [2012-07-01→…]; P4 -DIRECTOR_OF(registry,1.0)→ E0 [2017-01-15→2025-11-15]
- Corroborating path (tier 3, conf 0.7): P4 -DIRECTOR_OF(llm,0.7)→ E5; P4 -DIRECTOR_OF(registry,1.0)→ E0 [2017-01-15→2025-11-15]
- Relationship window within period: 2025-04-01 → 2025-11-15
- Transactions outside the relationship window: GL00019
- Resolution: identifier — pan = AABCI1234F
- Materiality: gross ₹47.0 cr, below ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'none', 'shareholder': 'not_required', 'refs': []}
- On management's related-party list: False
  - source: mca_master_data:U45200TN2012PTC086006 · signatory_details:din=02233445 · retrieved 2026-04-15
  - source: mca_master_data:L15100MH2004PLC147001 · signatory_details:din=02233445 · retrieved 2026-04-15

### 2. Sunrise Agro Pvt Ltd — rule_hit
- Clause: `CA2013_2(76)(iv)` (version `CA2013_2(76)(iv)@2013-09-12`), weakest origin: registry
- Path: P3 -DIRECTOR_OF(registry,1.0)→ E3 [2015-03-01→…]; P3 -DIRECTOR_OF(registry,1.0)→ E0 [2019-08-01→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: identifier — cin = U01100GJ2015PTC082004
- Materiality: gross ₹45.0 cr, below ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'none', 'shareholder': 'not_required', 'refs': []}
- On management's related-party list: False
  - source: mca_master_data:U01100GJ2015PTC082004 · signatory_details:din=01122334 · retrieved 2026-04-15
  - source: mca_master_data:L15100MH2004PLC147001 · signatory_details:din=01122334 · retrieved 2026-04-15

### 3. Rao Family Holdings Pvt. Ltd. — rule_hit
- Clause: `LODR_2(1)(zb)(a)` (version `LODR_2(1)(zb)(a)@2022-04-01`), weakest origin: filing
- Path: E2 -PROMOTER_GROUP_OF(filing,1.0)→ E0 [2024-04-01→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: identifier — pan = AAACR9012C
- Materiality: crossed on 2025-09-18 (cumulative ₹1050.0 cr > ₹1000.0 cr; Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover); threshold at period end ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'ok', 'shareholder': 'ok', 'refs': ['AC/2025-26/01/item5', 'AGM/2025/resolution7']}
- On management's related-party list: True
  - source: exchange_filing:reg31_shareholding_pattern · reg31:quarters=2024-06-30..2026-03-31:holder=Rao Family Holdings Private Limited:category=promoter_group · retrieved 2026-04-15

### 4. Rao Family Holdings Pvt. Ltd. — rule_hit
- Clause: `LODR_2(1)(zb)(b)` (version `LODR_2(1)(zb)(b)@2022-04-01`), weakest origin: filing
- Path: E2 -SHAREHOLDER_OF(filing,1.0)→ E0 [2024-04-01→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: identifier — pan = AAACR9012C
- Materiality: crossed on 2025-09-18 (cumulative ₹1050.0 cr > ₹1000.0 cr; Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover); threshold at period end ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'ok', 'shareholder': 'ok', 'refs': ['AC/2025-26/01/item5', 'AGM/2025/resolution7']}
- On management's related-party list: True
  - source: exchange_filing:reg31_shareholding_pattern · reg31:quarters=2024-06-30..2026-03-31:holder=Rao Family Holdings Private Limited · retrieved 2026-04-15

### 5. Meridian Logistics Pvt Ltd — rule_hit
- Clause: `CA2013_2(76)(viii)` (version `CA2013_2(76)(viii)@2013-09-12`), weakest origin: filing
- Path: E1 -SUBSIDIARY_OF(filing,1.0)→ E0 [2012-03-15→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: identifier — cin = U63000MH2012PTC231002
- Materiality: gross ₹310.0 cr, below ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'ok', 'shareholder': 'not_required', 'refs': ['AC/2025-26/01/item4']}
- On management's related-party list: True
  - source: annual_report_FY2024-25:AOC-1 · AOC-1:Meridian Logistics Private Limited · retrieved 2026-04-15

### 6. BHARAT COLDCHAIN PVT LTD — rule_hit
- Clause: `CA2013_2(76)(iv)` (version `CA2013_2(76)(iv)@2013-09-12`), weakest origin: registry
- Path: P9 -DIRECTOR_OF(registry,1.0)→ E4 [2016-11-01→…]; P9 -DIRECTOR_OF(registry,1.0)→ E0 [2021-02-01→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: fuzzy — fuzzy 'bharat coldchain private limited' ~ 'bharat cold chain private limited' score 98
- Materiality: gross ₹17.0 cr, below ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'none', 'shareholder': 'not_required', 'refs': []}
- On management's related-party list: False
  - source: mca_master_data:U63020MH2016PTC284005 · signatory_details:din=04455667 · retrieved 2026-04-15
  - source: mca_master_data:L15100MH2004PLC147001 · signatory_details:din=04455667 · retrieved 2026-04-15

### 7. Kavya Traders — rule_hit
- Clause: `CA2013_2(76)(iii)` (version `CA2013_2(76)(iii)@2013-09-12`), weakest origin: llm
- Path: PERSON:kavya_rao -PARTNER_OF(llm,0.75)→ FIRM:kavya_traders; P1 -RELATIVE_OF(llm,0.8)→ PERSON:kavya_rao; P1 -DIRECTOR_OF(registry,1.0)→ E0 [2004-06-01→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: exact_name — canonical names identical: 'kavya traders'
- Materiality: gross ₹13.0 cr, below ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'none', 'shareholder': 'not_required', 'refs': []}
- On management's related-party list: False
  - source: books:mbp1_declarations_FY2025-26:P1 · extractor=stub;span="My daughter Kavya Rao is a partner in the firm Kavya Traders" · retrieved 2025-04-05
  - source: books:mbp1_declarations_FY2025-26:P1 · extractor=stub;span="My daughter Kavya Rao is a partner in the firm Kavya Traders" · retrieved 2025-04-05
  - source: mca_master_data:L15100MH2004PLC147001 · signatory_details:din=00123456 · retrieved 2026-04-15

### 8. Rao Warehousing Pvt Ltd — rule_hit
- Clause: `CA2013_2(76)(iv)` (version `CA2013_2(76)(iv)@2013-09-12`), weakest origin: llm
- Path: P10 -DIRECTOR_OF(registry,1.0)→ E7 [2014-05-01→…]; P1 -RELATIVE_OF(llm,0.8)→ P10; P1 -DIRECTOR_OF(registry,1.0)→ E0 [2004-06-01→…]
- Corroborating path (tier 3, conf 0.7): P10 -DIRECTOR_OF(llm,0.7)→ E7; P1 -RELATIVE_OF(llm,0.8)→ P10; P1 -DIRECTOR_OF(registry,1.0)→ E0 [2004-06-01→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: identifier — pan derived from gstin 27AABCR5678G1Z1 = AABCR5678G
- Materiality: gross ₹11.0 cr, below ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'none', 'shareholder': 'not_required', 'refs': []}
- On management's related-party list: False
  - source: mca_master_data:U63090MH2014PTC255007 · signatory_details:din=05566778 · retrieved 2026-04-15
  - source: books:mbp1_declarations_FY2025-26:P1 · extractor=stub;span="My brother Vikram Rao is a director of Rao Warehousing Private Limited" · retrieved 2025-04-05
  - source: mca_master_data:L15100MH2004PLC147001 · signatory_details:din=00123456 · retrieved 2026-04-15

### 9. Rao Family Holdings Pvt. Ltd. — rule_hit
- Clause: `CA2013_2(76)(iv)` (version `CA2013_2(76)(iv)@2013-09-12`), weakest origin: llm
- Path: P1 -DIRECTOR_OF(llm,0.7)→ E2; P1 -DIRECTOR_OF(registry,1.0)→ E0 [2004-06-01→…]
- Corroborating path (tier 3, conf 0.7): P1 -MEMBER_OF(llm,0.7)→ E2; P1 -DIRECTOR_OF(registry,1.0)→ E0 [2004-06-01→…]
- Corroborating path (tier 3, conf 0.7): P2 -MEMBER_OF(llm,0.7)→ E2; P2 -DIRECTOR_OF(registry,1.0)→ E0 [2010-04-01→…]
- Relationship window within period: 2025-04-01 → 2026-03-31
- Resolution: identifier — pan = AAACR9012C
- Materiality: crossed on 2025-09-18 (cumulative ₹1050.0 cr > ₹1000.0 cr; Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover); threshold at period end ₹1000.0 cr (Reg23(1) 2022-04-01..2025-12-17: lower of Rs 1,000 cr or 10% of turnover)
- Approvals: {'audit_committee': 'ok', 'shareholder': 'ok', 'refs': ['AC/2025-26/01/item5', 'AGM/2025/resolution7']}
- On management's related-party list: True
  - source: books:mbp1_declarations_FY2025-26:P1 · extractor=stub;span="I am a director and shareholder of Rao Family Holdings Private Limited" · retrieved 2025-04-05
  - source: mca_master_data:L15100MH2004PLC147001 · signatory_details:din=00123456 · retrieved 2026-04-15

### 10. Meridian Logistics Private Limited — reconciliation
- Subsidiary / Services availed: disclosed ₹120.0 cr vs ledger gross ₹310.0 cr → variance ₹190.0 cr (158.3%)
- Ledger rows: GL00001, GL00002, GL00003, GL00004, GL00005, GL00006 · note source: books:draft_financial_statements_FY2025-26:note_38_related_parties
- Ind AS 24 para 18 requires gross transaction amounts; a balance-based figure or an omission would show here.

### 11. Apex Machinery Pvt Ltd — indicator
- (b) new_thinly_capitalised_vendor: incorporated 2025-02-10, first payment 2025-06-12 (4 months); paid Rs 40.0 cr vs paid-up capital Rs 0.01 cr (ratio 4000x)
- (c) advance_ahead_of_receipt: advance Rs 40.0 cr on 2025-06-12; first receipt 2026-01-25 (227 days later); received Rs 38.0 cr in total
- Resolution: identifier — pan = AABCA1111M
- These are reasons to look, not relationships. No clause fired.

### 12. Coastal Agri Ventures Pvt Ltd — indicator
- (a) promoter_entity_is_shareholder: 60.0% — with Rao Family Holdings Private Limited
- Resolution: identifier — pan = AABCC3456I
- These are reasons to look, not relationships. No clause fired.

### 13. Greenfield Packaging Private Limited — indicator
- (a) shared_registered_address: Rao House, 14 Marine Lines, Mumbai 400020, Maharashtra — with Rao Family Holdings Private Limited
- Resolution: identifier — pan = AABCG9012H
- These are reasons to look, not relationships. No clause fired.


## Unresolved counterparties (absence of evidence, not a finding)

- Ramesh Transport (V017), gross ₹1.2 cr — best candidate 'lotus transport private limited' scored only 72

## Coverage gaps

Clauses that could not be evaluated for lack of data, so a non-hit is not a clearance.

- 33 of 36 resolved counterparties — 2(76)(iv) member test and 2(76)(v): no shareholding record for this counterparty (MGT-7 not inspected)

## Extraction log

- P1 (stub): 6 accepted, 0 rejected
  - Rajan Rao -RELATIVE_OF(brother)→ Vikram Rao · span: “My brother Vikram Rao is a director of Rao Warehousing Private Limited”
  - Vikram Rao -DIRECTOR_OF→ Rao Warehousing Private Limited · span: “My brother Vikram Rao is a director of Rao Warehousing Private Limited”
  - Rajan Rao -RELATIVE_OF(daughter)→ Kavya Rao · span: “My daughter Kavya Rao is a partner in the firm Kavya Traders”
  - Kavya Rao -PARTNER_OF→ Kavya Traders · span: “My daughter Kavya Rao is a partner in the firm Kavya Traders”
  - Rajan Rao -DIRECTOR_OF→ Rao Family Holdings Private Limited · span: “I am a director and shareholder of Rao Family Holdings Private Limited”
  - Rajan Rao -MEMBER_OF→ Rao Family Holdings Private Limited · span: “I am a director and shareholder of Rao Family Holdings Private Limited”
- P2 (stub): 1 accepted, 0 rejected
  - Meera Rao -MEMBER_OF→ Rao Family Holdings Private Limited · span: “I am a shareholder of Rao Family Holdings Private Limited”
- P3 (stub): 1 accepted, 0 rejected
  - Arvind Shah -DIRECTOR_OF→ Shah Advisory Services LLP · span: “I hold directorships in the following bodies corporate: Shah Advisory Services LLP.”
- P4 (stub): 1 accepted, 0 rejected
  - Suresh Iyer -DIRECTOR_OF→ Iyer Infra Private Limited · span: “I am a director of Iyer Infra Private Limited”
- P9 (stub): 0 accepted, 0 rejected
