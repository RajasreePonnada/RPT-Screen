# Planted cases vs pipeline output

| Case | Counterparty | Expected | Got | Verdict |
|---|---|---|---|---|
| 1 | Disclosed subsidiary (V001) | rule_hit CA2013_2(76)(viii) tier 1 | rule_hit:CA2013_2(76)(viii):tier1,reconciliation::tier4 | PASS |
| 2 | Undisclosed vendor sharing a director (Arvind Shah) (V003) | rule_hit CA2013_2(76)(iv) tier 0 | rule_hit:CA2013_2(76)(iv):tier0 | PASS |
| 3 | Relative's firm named only in MBP-1 prose (Kavya Traders) (V006) | rule_hit CA2013_2(76)(iii) tier 3 | rule_hit:CA2013_2(76)(iii):tier3 | PASS |
| 3 | Relative (brother, prose) is director (registry) of vendor (V007) | rule_hit CA2013_2(76)(iv) tier 3 | rule_hit:CA2013_2(76)(iv):tier3 | PASS |
| 4 | Name variant, no identifier (BHARAT COLDCHAIN PVT LTD) (V004) | rule_hit CA2013_2(76)(iv) tier 2 | rule_hit:CA2013_2(76)(iv):tier2 | PASS |
| 5 | Common registered address with promoter entity (V008) | indicator tier 5 | indicator::tier5 | PASS |
| 6 | Two-hop: 60% owned by promoter-group entity (V009) | indicator tier 5 | indicator::tier5 | PASS |
| 7 | 9.5% holder, just under LODR threshold (V010) | none | none | PASS |
| 8 | Director resigned 15 Nov 2025; transactions before and after (V005) | rule_hit CA2013_2(76)(iv) tier 0 | rule_hit:CA2013_2(76)(iv):tier0 | PASS |
| 9 | Legitimate new vendor with large advance (V013) | indicator tier 5 | indicator::tier5 | PASS |
| 10 | Decoy: Sunrise Agro Foods Ltd (V012) | none | none | PASS |
| 11 | Disclosed but understated (120 cr disclosed, 310 cr in ledger) (V001) | reconciliation tier 4 | rule_hit:CA2013_2(76)(viii):tier1,reconciliation::tier4 | PASS |
| 12 | Undeclared relative (Meera Rao's brother) directs vendor (V015) | none | none | DESIGNED MISS (not detectable) |
| 13 | Nominee holding 8% for promoter, undeclared (V016) | none | indicator | DESIGNED MISS (not detectable) |
| 14 | 15% holder: RP only under post-Apr-2023 10% rule (V011) | rule_hit LODR_2(1)(zb)(b) tier 1 | rule_hit:LODR_2(1)(zb)(b):tier1 | PASS |
| 15 | Sole proprietor with no registry record (V017) | unresolved | unresolved | PASS |
| 16 | Materiality: 1,800 cr with promoter entity, two regimes in one FY (V002) | rule_hit LODR_2(1)(zb)(a) tier 1 | rule_hit:LODR_2(1)(zb)(a):tier1,rule_hit:LODR_2(1)(zb)(b):tier1,rule_hit:CA2013_2(76)(iv):tier3,indicator::tier5 | PASS |

15 pass, 0 fail, 2 designed misses (relationship exists but is not discoverable from the auditor's vantage point), 0 unexpected hits.
