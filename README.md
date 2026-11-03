# rpt-screen: related-party screening from the auditor's seat

A prototype that builds an independent related-party graph for a listed Indian company from
public registry data plus the company's own books, screens every ledger counterparty against
the legal definitions, and hands the statutory auditor a **ranked evidence queue** — never a
verdict.

Design rule enforced in code: probabilistic parts (name resolution, prose extraction, vendor
indicators) can only *propose*; the rule engine applies law to what they propose; a human forms
every conclusion. The system sees exactly what the auditor sees — the company's books and public
records — and nothing from behind a counterparty's wall.

## Run it

```bash
pip install -r requirements.txt
python synth/generate.py           # regenerate the synthetic company (seeded; all data made up)
python run_synthetic.py            # run, write out/synthetic/{report.md, evidence_pack.json, test_results.md}
python run_synthetic.py --rule-as-of 2022-10-01   # counterfactual: evaluate under the rules of that date
python calibrate_resolver.py       # similarity scores behind the resolver thresholds
python run_gensol.py               # Gensol public-record set (filled 2026-11-02 from MCA mirrors; see data/gensol/RESULTS.md)
```

No API key is needed. The default `--extractor stub` is a deterministic regex stand-in for the
LLM so results are reproducible offline. `--extractor openrouter` calls a free-tier model via
OpenRouter (`OPENROUTER_API_KEY`, optional `RPT_MODEL`; default `google/gemma-4-31b-it:free`
— check the current free list, rate limits apply). The OpenRouter path has the same output
contract and validation and it was run once live; see ‘Real-model extraction run’ below.; see "Honest status" below.

## What is in here

```
rptscreen/
  models.py      pydantic schemas: Node, Edge (temporal, provenance), MatchRecord, RuleHit, QueueItem
  canon.py       name/address canonicalisation; PAN derived from GSTIN
  resolver.py    identifier > exact canonical name > fuzzy (rapidfuzz); TAU_HIGH=90, TAU_LOW=75
  extractor.py   prose -> proposed edges; span must appear verbatim; fixed confidence by edge type
  ingest.py      adapters: MCA registry, Reg 31 shareholding (quarters coalesced), AOC-1 group, extractor output
  graph.py       networkx MultiDiGraph with validity windows and provenance on every edge
  rulebook.py    legal definitions as effective-dated graph predicates; Reg 23 materiality incl. Schedule XII
  reconcile.py   ledger gross flows vs draft Ind AS 24 note
  indicators.py  vendor risk signals: (a) promoter-side link, (b) new thin vendor, (c) advance ahead of receipt;
                 post-registration (b2) thin capital any age, (c2) unapplied advance, (d) circular flow
  ranking.py     one queue, lexicographic order, every component kept visible
  report.py      evidence pack JSON + markdown
  pipeline.py    end to end
synth/generate.py      the synthetic listed company and its 16 planted cases
data/synthetic/        generated inputs (JSON)      data/gensol/   templates + pre-registered expectations
out/synthetic/         report.md, evidence_pack.json, test_results.md
```

## Jurisdiction and rules encoded

India, listed company. Related party = Companies Act 2013 s.2(76) with s.2(77)/Rules 3–4 ∪
SEBI LODR Reg 2(1)(zb) deeming provisos ∪ Ind AS 24. Materiality = Reg 23(1): 10% of turnover
(pre-Apr-2022), lower of ₹1,000 cr or 10% (1 Apr 2022 – 17 Dec 2025), Schedule XII tiers
(from 18 Dec 2025). Each clause in `rulebook.py` carries `valid_from`/`valid_to`; an audit
period is evaluated against the clauses in force then, and `--rule-as-of` runs a counterfactual.

Clauses that exist in law but are not record-testable — 2(76)(vi)/(vii) "accustomed to act" and
LODR's "purpose and effect" — are listed in the report as *not evaluated*, not silently skipped.

For an unlisted company: drop the LODR provisos and the shareholding-pattern source. For another
jurisdiction: swap the clause predicates and the registry adapter; graph, resolver and queue are unchanged.

## The synthetic company and the 16 planted cases

Meridian Agro Industries Limited (fictional; consolidated turnover ₹25,000 cr so the pre- and
post-Dec-2025 materiality regimes differ), one subsidiary, promoters, directors, KMP, relatives,
37 counterparties, 67 ledger rows for FY2025-26. **Every name, DIN, CIN, PAN, amount and document is
made up.** `synth/generate.py` is seeded and committed.

| Case | Tests | Result |
|---|---|---|
| 1 | Disclosed subsidiary (AOC-1) | hit 2(76)(viii), tier 1 |
| 2 | Undisclosed vendor sharing a director; CIN in ledger | hit 2(76)(iv), tier 0 |
| 3 | Relative's firm named only in MBP-1 prose; relative (prose) is director (registry) of another vendor | hits 2(76)(iii) and (iv), tier 3 |
| 4 | Name variant, no identifier ("BHARAT COLDCHAIN PVT LTD") | fuzzy merge (98) then hit, tier 2 |
| 5 | Common registered address with promoter entity | indicator (a) only |
| 6 | Vendor 60% owned by promoter-group entity (two-hop) | indicator (a) only — purpose-and-effect candidate for the human |
| 7 | 9.5% holder, just under the 10% LODR threshold | no hit (hard negative) |
| 8 | Director resigned mid-period | hit with window ending 15 Nov 2025; the Feb 2026 transaction flagged as outside it |
| 9 | Legitimate new vendor with a large advance | indicators (b),(c) fire — false positive by design, for the reviewer to reject |
| 10 | Decoy "Sunrise Agro Foods Ltd" vs "Sunrise Agro Private Limited" | kept apart |
| 11 | Disclosed party, ₹120 cr in note vs ₹310 cr in ledger | reconciliation variance ₹190 cr |
| 12 | Undeclared relative (director's brother) directs a vendor | **designed miss** — in no record the auditor can see |
| 13 | 8% nominee holding for a promoter, undeclared | **designed miss** — below threshold, beneficial interest undeclared |
| 14 | 15% holder | hit under the post-Apr-2023 10% rule; correctly *absent* under `--rule-as-of 2022-10-01` |
| 15 | Sole proprietor with no registry record | unresolved list |
| 16 | ₹1,800 cr with promoter entity across two materiality regimes | material from 18 Sep 2025 under the ₹1,000 cr rule; Schedule XII threshold (₹2,250 cr) not crossed; approvals matched |

Current run: 15 pass, 0 fail, 2 designed misses. See `out/synthetic/test_results.md`.

## Where it fails, and what the build taught us

* **Designed misses are real misses.** Cases 12 and 13 exist in the synthetic world and the system
  cannot find them. Nothing short of a declaration or a Section 89 filing would expose them. The
  report's job is to make that visible (unresolved list, coverage gaps), not to pretend otherwise.
* **The registry gap is systematic, not occasional.** 33 of 36 resolved counterparties have no
  shareholding record, because private-company MGT-7 filings sit behind MCA's paid inspection.
  The 2(76)(iv) *member* test and 2(76)(v) therefore go unevaluated for almost every vendor. The
  report states this as a count. In production the auditor pays for the filings of the counterparties
  that matter; the prototype shows which ones those are.
* **Name similarity has a thin margin.** True variant 98 vs decoy 87 with `TAU_HIGH=90`
  (`python calibrate_resolver.py`). A different decoy could cross. Identifiers (GSTIN → PAN,
  CIN) are what make resolution safe; the vendor master's identifier coverage is the real lever.
* **Quarterly filings need coalescing.** First run produced one edge per quarter and flagged
  transactions as "outside the relationship window" wrongly. Fixed in `ingest.py`; a good example
  of a temporal-modelling bug that would have produced confident wrong output.
* **Multiple paths per clause flood the queue.** Now one item per (counterparty, clause), with
  corroborating paths listed.
* **Stub extractor is narrow.** It missed "hold 60 per cent of its shares" in one declaration; an
  LLM would get it. The stub exists for reproducibility, not as a claim about extraction quality.
* **Disclosed, approved items ranked above undisclosed ones** at the same evidence tier in the first
  run. Added "undisclosed first" as the second sort key. This is a design decision, recorded as such.

## Gensol retrospective (real public records)

Entity list from SEBI's interim order of 15 April 2025; registry fields from public mirrors of MCA
master data (mca.gov.in needs a captcha), each cited with date in `data/gensol/registry.json` and to be
verified against the portal. Expectations were written and timestamped before retrieval
(`data/gensol/EXPECTATIONS.md`); outcomes are in `data/gensol/RESULTS.md`. In short:

* **Capbridge Venture LLP** — both promoters are designated partners since incorporation, at Gensol's
  own registered address. Registry-backed rule hit under 2(76)(iii). Tier 2 only because the vendor
  master had no LLPIN, so identity rested on a 98-point name match ("Ventures" vs "Venture").
* **Go-Auto** — no relationship in public records (its directors are paywalled). Indicators: ₹775 cr
  paid, ₹567.73 cr of vehicles delivered, ₹207.27 cr unapplied; ₹2.9 cr paid-up capital.
* **Wellray** — no relationship in free registry data (the link ran through a former employee's
  shareholding and pre-2020 ownership). Gensol's own books show ₹424 cr out, ₹310 cr back, with a
  ₹1-lakh company: circular-flow indicator.
* **BluSmart** — both promoters are directors, but it is a public limited company, so 2(76)(iv) does
  not apply and (v) needs a shareholding we cannot see. Reported as a coverage gap. Exposes that the
  rulebook does not encode Ind AS 24's "entity controlled by KMP" test.

Three indicators and one output (the registry-derived "related entities with no recorded transactions"
list) were **added after retrieval** because the real data showed signals the pre-registered design
could not express. They are tagged `post_registration` in the evidence pack and listed in RESULTS.md.

## Real-model extraction run (OpenRouter free tier)

Run on 2 Nov 2026 by the author from her machine with `--extractor openrouter`. Model:
**`nvidia/nemotron-3.5-lightning:free`**. `google/gemma-4-31b-it:free`, `google/gemma-4-26b-a4b-it:free`
and `liquid/lfm-2.5-2.6b:free` returned provider-side 429s for the whole attempt window, so the planned
small-model comparison could not be made; a free-tier model is workable for a five-document test and
not for an audit with hundreds of declarations.

Planted-case results: identical to the stub run (15 pass, 0 fail, 2 designed misses). Extraction differed:

| | Stub (regex) | Nemotron 3.5 Lightning |
|---|---|---|
| Edges proposed across 5 declarations | 9 | 12 |
| Validator rejections (span not verbatim / bad schema / relative kind) | 0 | 0 |
| "hold 60 per cent of its shares" (Suresh Iyer) | missed | caught as shareholding |
| "My wife Meera Rao is a director of the Company" | missed | caught; exposed that ingest created a junk node named "the Company" — fixed (self-references now map to the company node) |
| Word used for "shareholder of" | `MEMBER_OF` | `SHAREHOLDER_OF` — exposed that 2(76)(iv) only tested `MEMBER_OF`; fixed by normalising at ingest |
| Over-extraction | — | none observed; "Shah Advisory Services LLP" extracted as a directorship, which is correct and harmless |

Two code defects were therefore found only by running a real model, which is the argument for the
validation layer being a contract rather than a hope. The model's prose inputs were synthetic; no real
declaration text was sent to a third-party model.

## Honest status

* Synthetic end-to-end: runs, tested, reproducible.
* Gensol retrospective: executed on mirror data; verification against mca.gov.in and BSE filings pending;
  Ind AS 24 amounts not retrieved, so reconciliation produced nothing on this set.
* OpenRouter extractor: run once live with `nvidia/nemotron-3.5-lightning:free` (see above).
* No real client, personal or non-public data anywhere in this repo. The only real names are the
  entities and promoters named in SEBI's public orders, used solely as a public-record test set.

## Thresholds the author chose (not from any standard)

`TAU_HIGH=90`, `TAU_LOW=75` (resolver); `NEW_VENDOR_MONTHS=18`, `CAPITAL_RATIO=20`,
`ADVANCE_GRACE_DAYS=90` (indicators); `TOLERANCE_PCT=5`, `TOLERANCE_ABS_CR=1` (reconciliation);
fixed extractor-edge confidences in `models.LLM_EDGE_CONFIDENCE`. All are in one place each and
are reported in the evidence pack.
