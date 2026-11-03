# Related-party screening — evidence queue

Period 2022-04-01 to 2025-03-31 · rules as of period · extractor `stub` · resolver τ_high=90.0 τ_low=75.0 · graph 14 nodes / 21 edges

Counterparties screened: 4 · queue items: 3 · unresolved: 0 · resolution candidates needing a human: 0

Clauses in force: CA2013_2(76)(i)@2013-09-12, CA2013_2(76)(ii)@2013-09-12, CA2013_2(76)(iii)@2013-09-12, CA2013_2(76)(iv)@2013-09-12, CA2013_2(76)(v)@2013-09-12, CA2013_2(76)(viii)@2013-09-12, CA2013_Rule3@2014-07-17, LODR_2(1)(zb)(a)@2022-04-01, LODR_2(1)(zb)(b)@2022-04-01, LODR_2(1)(zb)(b)@2023-04-01

Not evaluated (human judgment only): CA2013_2(76)(vi) — body corporate whose board/MD/manager is accustomed to act on the advice of a director or manager; CA2013_2(76)(vii) — person on whose advice a director or manager is accustomed to act; LODR_2(1)(zc)_purpose_and_effect — transaction with an unrelated party whose purpose and effect is to benefit a related party


## Summary for the engagement partner

- 0 counterparties not on management's related-party list meet a legal definition on the evidence here (0 on registry/filing-backed paths): none
- 1 related counterparties have no audit committee approval on record: Capbridge Ventures LLP
- 0 counterparties crossed the Reg 23 materiality threshold: none
- 0 disclosed figures do not reconcile to the ledger
- 2 counterparties carry vendor risk indicators only (no legal definition met)
- 0 counterparties could not be matched to any public record and were not screened
- Every item above is evidence for the engagement team's judgment under SA 550; none is a determination.

## Ranked evidence queue

Ordering: evidence tier → undisclosed before disclosed → materiality tier → gross value → min confidence. No item is a conclusion.

| # | Counterparty | Item | Evidence tier | Materiality | Gross ₹cr | Min conf | Clause / signal | Mgmt list | Approvals |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Capbridge Ventures LLP (GV02) | rule_hit | 2 rule hit via fuzzy name merge | below | 0.0 | 0.98 | CA2013_2(76)(iii) | yes | AC none, SH not_required |
| 2 | Go-Auto Pvt Ltd (GV01) | indicator | 5 indicator only | value ≥ Reg 23 threshold (if related) | 775.0 | 0.5 | b2:thinly_capitalised_vendor_any_age, c2:unapplied_advance_at_period_end, c:advance_ahead_of_receipt | — | — |
| 3 | Wellray Solar Industries Pvt Ltd (GV03) | indicator | 5 indicator only | value ≥ Reg 23 threshold (if related) | 734.33 | 0.5 | b2:thinly_capitalised_vendor_any_age, d:circular_flow | — | — |

## Item detail

### 1. Capbridge Ventures LLP — rule_hit
- Clause: `CA2013_2(76)(iii)` (version `CA2013_2(76)(iii)@2013-09-12`), weakest origin: registry
- Path: Anmol Singh Jaggi (DIN 01293305) —PARTNER_OF→ Capbridge Venture LLP (LLPIN AAT-2035) [2020-08-02 → open]  [registry, conf 1.0]
    then Anmol Singh Jaggi (DIN 01293305) —DIRECTOR_OF→ Gensol Engineering Limited (CIN L74210GJ2012PLC129176) [2019-01-04 → 2025-05-12]  [registry, conf 1.0]
- Corroborating path (tier 2, conf 1.0): Puneet Singh Jaggi (DIN 02479868) —PARTNER_OF→ Capbridge Venture LLP (LLPIN AAT-2035) [2020-08-02 → open]  [registry, conf 1.0]
    then Puneet Singh Jaggi (DIN 02479868) —DIRECTOR_OF→ Gensol Engineering Limited (CIN L74210GJ2012PLC129176) [2012-09-25 → 2025-05-12]  [registry, conf 1.0]
- Suggested procedure: no audit committee approval on record — test Reg 23(2) / s.188 compliance; identity rests on a name match — obtain the counterparty's PAN/CIN from the vendor master or an invoice; obtain external confirmation of balances and terms; evaluate arm's length and disclosure in the Ind AS 24 note
- Relationship window within period: 2022-04-01 → 2025-03-31
- Resolution: fuzzy — fuzzy 'capbridge ventures llp' ~ 'capbridge venture llp' score 98
- Materiality: no transactions with this counterparty in the ledger provided (relationship exists; transactions, if any, may be routed elsewhere)
- Approvals: {'audit_committee': 'none', 'shareholder': 'not_required', 'refs': []}
- On management's related-party list: True
  - source: mirror:infyner.com/finance/capbridge-venture-llp/AAT-2035 · signatory_details:din=01293305 · retrieved 2026-11-02
  - source: mirror:thecompanycheck.com/company/gensol-engineering-limited/L74210GJ2012PLC129176 (data dated 2025-09-03) · signatory_details:din=01293305 · retrieved 2026-11-02

### 2. Go-Auto Pvt Ltd — indicator
- (b2) thinly_capitalised_vendor_any_age: incorporated 2008-08-28, first payment 2022-10-03 (170 months); paid Rs 775.0 cr vs paid-up capital Rs 2.9 cr (ratio 267x)
- (c) advance_ahead_of_receipt: advance Rs 93.88 cr on 2022-10-03; first receipt 2024-03-31 (545 days later); received Rs 567.7 cr in total
- (c) advance_ahead_of_receipt: advance Rs 54.62 cr on 2023-02-01; first receipt 2024-03-31 (424 days later); received Rs 567.7 cr in total
- (c) advance_ahead_of_receipt: advance Rs 134.14 cr on 2023-09-29; first receipt 2024-03-31 (184 days later); received Rs 567.7 cr in total
- (c) advance_ahead_of_receipt: advance Rs 95.3 cr on 2023-12-27; first receipt 2024-03-31 (95 days later); received Rs 567.7 cr in total
- (c2) unapplied_advance_at_period_end: advances Rs 775.00 cr vs goods/services received Rs 567.73 cr; Rs 207.27 cr (27%) unapplied
- Resolution: identifier — cin = U34300DL2008PTC182562
- These are reasons to look, not relationships. No clause fired.
- Suggested procedure: trace the advance to delivery: GRNs, contracts, bank statement; consider whether the advance is in substance a loan; counterparty's paid-up capital is tiny relative to what it was paid — obtain its financials; consider whether it is a pass-through

### 3. Wellray Solar Industries Pvt Ltd — indicator
- (b2) thinly_capitalised_vendor_any_age: incorporated 2017-07-10, first payment 2023-03-31 (68 months); paid Rs 424.1 cr vs paid-up capital Rs 0.01 cr (ratio 42414x)
- (d) circular_flow: paid Rs 424.14 cr, received back Rs 310.19 cr (ratio 0.73); net Rs 113.95 cr on gross Rs 734.33 cr
- Resolution: exact_name — canonical names identical: 'wellray solar industries private limited'
- These are reasons to look, not relationships. No clause fired.
- Suggested procedure: counterparty's paid-up capital is tiny relative to what it was paid — obtain its financials; consider whether it is a pass-through; money went out and most came back — obtain the commercial rationale for each leg; consider round-tripping and whether the net is a loan


## Unresolved counterparties (absence of evidence, not a finding)

None.

## Registry-derived related entities with no recorded transactions

Entities connected to the company's directors/KMP in public records that are not in the vendor master. Counterparty screening cannot see these; search payments and bank statements for them.

- Gensol Ventures Private Limited — via Anmol Singh Jaggi (DIRECTOR_OF, registry) [… → open]
- Gensol Ventures Private Limited — via Puneet Singh Jaggi (DIRECTOR_OF, registry) [… → open]

## Coverage gaps

Clauses that could not be evaluated for lack of data, so a non-hit is not a clearance.

- 3 of 4 resolved counterparties — 2(76)(iv) member test and 2(76)(v): no shareholding record for this counterparty (MGT-7 not inspected)
  - GV01, GV03, GV04

## Extraction log

