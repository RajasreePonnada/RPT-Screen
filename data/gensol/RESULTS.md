# Gensol retrospective — results against the pre-registered expectations

Run date: 2026-11-02. Pre-registration: `EXPECTATIONS.md` (finalised 12:20 IST, before retrieval).
Output: `out/gensol/report.md`, `out/gensol/evidence_pack.json`.

## Data actually obtained

mca.gov.in requires an interactive captcha, so registry fields were taken from public mirrors of
MCA master data (infyner, thecompanycheck, instafinancials, falconebiz) and the Reg 31 shareholding
pattern from a market-data mirror. Each record carries its mirror and date in `registry.json`. All
of it must be verified against the MCA portal and BSE filings before it is relied on. Gensol-side
transaction figures come from paragraphs of the SEBI interim order (cited per row in `ledger.json`);
no onward hop that happened in another company's bank account was included.

Not obtainable from free sources: Go-Auto's directors; Wellray's directors before April 2020;
BluSmart's and Gensol Ventures' addresses and capital; Gensol's Ind AS 24 note amounts.

## Prediction vs outcome

| # | Counterparty | Predicted | Outcome | Verdict |
|---|---|---|---|---|
| G-1 | Capbridge Ventures LLP | Rule hit if MCA lists a Jaggi as designated partner | **Rule hit 2(76)(iii)**: both promoters are designated partners since incorporation (2 Aug 2020); registered address identical to Gensol's. Two registry-backed paths. Evidence tier 2 only because the vendor master had no LLPIN and the resolver merged "Ventures"/"Venture" by name (score 98). | Prediction's first branch confirmed |
| G-2 | Wellray Solar Industries | Indicator (a) at most, unless a Jaggi is a registered director | **No relationship path.** Sole current director unrelated; the order says the link ran through a former Gensol employee's 99% holding and pre-2020 promoter ownership — neither visible in free registry data. But Gensol's own books show ₹424 cr out and ₹310 cr back with a ₹1-lakh company: fired post-registration indicators (d) circular flow and (b2) thin capital. | Honest negative on the registry; symptom visible in the books |
| G-3 | Go-Auto | No relationship; indicator (c) MUST fire | **No relationship** (as predicted; directors not retrievable anyway). Indicator (c) fired on every advance (receipt dates are a period-end placeholder, so timing is indicative only); post-registration (c2) fired on the quantity: ₹775 cr paid, ₹567.73 cr of EVs, ₹207.27 cr unapplied — the figure SEBI itself computed. (b2) fired: ₹2.9 cr capital vs ₹775 cr received. | Confirmed |
| G-4 | BluSmart Mobility | Rule hit if filings name it; else indicator (a) | **Nothing fired, correctly reported as a coverage gap.** Both promoters are directors, but the entity is now a public limited company, so 2(76)(iv) does not apply and 2(76)(v) needs a >2% shareholding we cannot see. It is on management's list. | Exposed a rulebook gap (Ind AS 24 "controlled by KMP" not encoded) |
| G-5 | Onward hops | Nothing | Nothing — excluded from the ledger by design | As designed |
| G-6 | Unresolved list | Empty if identifiers found | Empty: Go-Auto by CIN, the other three by canonical name | Confirmed |

Additional output: the registry-derived "related entities with no recorded transactions" list surfaced
Gensol Ventures Pvt Ltd via both promoters' directorships. Had Capbridge not been placed in the vendor
master for the test, it would have appeared here — which is the realistic case, since the order shows no
direct Gensol→Capbridge payment.

## What this run changed in the design (recorded, not hidden)

Three additions were made AFTER retrieval, because real data showed signals the pre-registered design
could not express. They are tagged `post_registration: true` in the evidence pack:

1. **Indicator (d) circular flow** — paid vs received with the same counterparty (Wellray 0.73).
2. **Indicator (c2) unapplied advance at period end** — quantity-based, independent of receipt dates (Go-Auto 27%).
3. **Indicator (b2) thin capital regardless of age** — the original (b) required a *new* vendor; Go-Auto is from 2008 and Wellray from 2017.
4. **Registry-derived related universe** — entities connected to directors that have no ledger presence.
5. **LLP treated as a "firm" for 2(76)(iii)** — an interpretive choice; the Act's text says "firm" and whether an LLP falls under (iii) is contested. Flagged on the node.

The honest reading: the pre-registered design would have produced the Capbridge finding and the
Go-Auto timing indicator; it would have missed the Wellray circularity and the ₹207 cr shortfall as
explicit signals. The real document improved the design; that is the point of testing on one.

## The thesis, restated by the data

Everything that connected to the promoters *through a registry record* (Capbridge) was found on
registry-backed paths. Everything that connected through a *former employee's shareholding*, a
*bank-to-bank onward transfer*, or a *public company's unseen shareholding* (Wellray, Go-Auto's hops,
BluSmart) was not — and could not be, from the auditor's seat. What the auditor's seat *does* show is
the symptom in the company's own books: money out and back, advances unapplied, a ₹1-lakh counterparty
handling hundreds of crores. SEBI found the rest with bank statements the auditor never has.
