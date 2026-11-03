# Gensol retrospective — pre-registered expectations

Finalised 2026-11-02 12:20 IST, before any registry data was retrieved. Confirmed by Rajasree Ponnada.

Purpose: written down BEFORE pulling public records, so the
result cannot be tuned to the answer. Edit this file, commit it, then fill the JSON
templates from MCA / exchange filings, then run `python run_gensol.py`.

Source of the entity list: SEBI interim order WTM/AB/CFID/CFID-SEC1/31379/2025-26 dated
15 April 2025 and the confirmatory order dated 30 July 2025. Everything below is a
prediction about what the public registry will show, not a claim about the facts of the case.

## Known limitation stated up front
MCA records are retrieved in 2026. Directors who resigned in May 2025 will show cessation
dates; promoter-entity structures may have changed. We reconstruct "as of FY2023-24 /
FY2024-25" using appointment and cessation dates where the registry gives them, and say
where it does not.

## Predictions

| # | Counterparty | What we expect the pipeline to produce | Why |
|---|---|---|---|
| G-1 | Capbridge Ventures LLP | Rule hit under 2(76)(iii)/(iv)-equivalent if MCA signatory details list either Jaggi as designated partner; otherwise indicator (a) if a promoter-side address or shareholder is visible; otherwise NO FINDING | The order describes Capbridge as controlled by the promoters; whether that control is visible in registry data is exactly the test |
| G-2 | Wellray Solar Industries Pvt Ltd | Indicator (a) at most (shared address / director with a promoter entity), unless a Jaggi is a registered director — then 2(76)(iv) | Order says "deep links" to promoters; registry may or may not show them |
| G-3 | Go-Auto Pvt Ltd | NO relationship finding; indicator (c) MUST fire (advances ahead of receipts: ₹207.27 cr paid but not used for vehicles; 4,704 of 6,400 EVs delivered) | This is the key test: the intermediary is unrelated on paper, but the company's own books showed the symptom |
| G-4 | BluSmart Mobility Pvt Ltd | Rule hit if Gensol's own Ind AS 24 note or shareholding pattern names it as promoter-group / common-control; else indicator (a) | Widely described as the promoters' affiliate; depends on filings |
| G-5 | Any onward hop (Go-Auto → Capbridge → DLF) | NOTHING — these rows are not in Gensol's books and are deliberately excluded from the ledger file | The design's boundary; not a failure |
| G-6 | Unresolved list | Expected empty if CINs/LLPINs are found for all four; any entity without a findable registry record goes here | Tests the absence-of-evidence path on real data |

## What would count as a strong result
Indicator (c) fires on Go-Auto from Gensol-side data alone, AND at least one of Capbridge /
Wellray / BluSmart connects to a promoter through a registry-backed path (tier 0).

## What would count as an honest negative
Registry data shows no path from Capbridge or Wellray to the promoters. Then the brief says:
"public records did not expose the control relationship; the system surfaced only the
vendor-side symptom (advance-ahead-of-receipt on Go-Auto). SEBI found the rest from bank
statements the auditor cannot see." That is still the thesis.

## Fields to fill (do not run until these are resolved)
See `python run_gensol.py` — it lists every remaining TO_FILL placeholder and refuses to run.
