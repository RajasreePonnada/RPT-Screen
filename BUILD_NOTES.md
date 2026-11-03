# Build notes — practicalities surfaced by building before writing

Kept as raw material for the brief's "what surprised you", "weakest point" and the appendix's
"what you rejected or corrected".

1. **One edge per quarterly filing is wrong.** Reg 31 shareholding patterns are quarterly; the
   naïve ingest made four separate PROMOTER_GROUP_OF edges and the rule picked the first, so
   five transactions were flagged "outside the relationship window". Confident, traceable, wrong.
   Fix: coalesce consecutive quarters with identical status; leave the window open if the run
   reaches the latest filing. Lesson for the brief: temporal modelling of *filings* (which state a
   position at a date) differs from temporal modelling of *events* (appointment/cessation).

2. **The MGT-7 paywall is the single largest coverage gap.** 33/36 resolved counterparties: no
   shareholding record → 2(76)(iv) member test and 2(76)(v) unevaluated. This was predicted
   abstractly in design; the build shows it is near-universal, not occasional. Design response:
   coverage report as counts; in production, buy the filings for counterparties the queue ranks
   highly.

3. **Resolver margin is thin.** True variant 98 vs decoy 87, threshold 90. Identifier coverage
   (GSTIN → PAN) in the vendor master matters more than any similarity tuning. A decoy pair the
   system *would* merge is easy to construct; the candidate lane (75–90 → human) is the safety net.

4. **Disclosed + approved items outrank undisclosed ones** when ordering is evidence tier →
   materiality → value. Added "undisclosed first" as second key. Rationale: SA 550 is about what
   management did not disclose. This is the author's decision and reversible.

5. **Hits multiply per clause.** Rao Family Holdings produced five items (two LODR + three 2(76)(iv)
   paths from the extractor). Collapsed to one per (counterparty, clause) with corroborating paths.

6. **Designed misses must be labelled as misses.** First harness called cases 12/13 "PASS"
   because "none" was expected. Relabelled "DESIGNED MISS (not detectable)". A failure table
   with zero failures would have been a red flag.

7. **Counterfactual rules need to drive materiality too.** `--rule-as-of` initially switched
   clause versions but not the Reg 23 threshold. Fixed. The counterfactual run correctly
   drops the 15% holder (20% rule in 2022).

8. **Stub extractor limits.** Regex caught "I am a director of X" but not "and hold 60 per cent of
   its shares". The LLM backend would. Keep the stub for reproducibility; say so.

9. **Relatives are name-keyed nodes.** Kavya Rao, Vikram Rao exist only via prose, with no DIN or
   PAN. Any later ledger name matching them is a fuzzy match at best. This is where identity is
   weakest and where the Rule 4 closed list of relatives earns its place as a validation check.

10. **Indicator (a) fires on exactly the Gensol-shaped cases** (shared address, promoter-side
    shareholder) and on nothing else in the synthetic set. Indicators (b)+(c) fire together on the
    legitimate capital-equipment vendor, which is the expected false positive. Three indicators were
    enough; a fourth (vendor turnover vs payments) is not computable from free data.

## From the Gensol run (real public records)

11. **A placeholder is data to the machine.** "Ahmedabad City, Gujarat (full address not retrieved)" on two
    entities produced a "shared registered address" indicator. Missing fields must be null, never descriptive
    text. Fixed in ingest.

12. **Public records found Capbridge in one hop.** Both promoters are designated partners of the LLP since
    2020, at Gensol's address. This was findable by anyone with a DIN and the MCA portal. The auditor's
    failure mode here is not "invisible", it is "nobody looked by DIN".

13. **The vendor master decides evidence quality.** The same Capbridge finding is tier 0 with an LLPIN in the
    vendor master and tier 2 without one. Identifier hygiene in the auditee's own books is a bigger lever than
    any model.

14. **Wellray is the honest negative.** The control link ran through a former employee's 99% shareholding
    (order para 58–59) and pre-2020 ownership — neither in free registry data, and the pre-2020 directors are
    paywalled. Yet the books alone show ₹424 cr out / ₹310 cr back. The pre-registered design had no indicator
    for circularity; the real document supplied it.

15. **BluSmart exposed a rulebook gap.** Director overlap plus public-company status means neither 2(76)(iv)
    nor, without shareholding data, (v) applies — yet everyone treats it as a related party. Ind AS 24's
    "controlled or jointly controlled by KMP" test is the clause that would fire, and it is not encoded.
    Adding it needs control evidence (shareholding or board majority), which again sits behind MGT-7.

16. **Capbridge had no direct Gensol transaction.** Counterparty screening would never have reached it; the
    DIN-based "related universe" sweep does. Two complementary directions: ledger → registry, and
    registry → ledger.

17. **Mirrors, not the registry.** mca.gov.in needs a captcha; every field came from a mirror and is cited as
    such. For the brief: a production system needs either MCA's paid API or a licensed data provider, and the
    provenance record must say which.

18. **LLP vs "firm".** Treating Capbridge Venture LLP as a firm under 2(76)(iii) is an interpretation, not a
    reading of the text. Recorded on the node. A reviewer will ask; the answer is that the clause fires either
    way under Ind AS 24 (entity controlled by KMP) if control can be shown.

## From the real-model run (nvidia/nemotron-3.5-lightning:free, 2 Nov 2026)

19. **Free-tier throttling is real.** Three of four chosen models returned provider 429s for the whole
    window; the extractor gained pacing and backoff. For the brief: the LLM must be at the edge, and a
    production deployment needs a paid or self-hosted model with a rate budget.

20. **"the Company" became a node.** The model correctly extracted "Meera Rao is a director of the Company";
    ingest created an entity literally named "the Company". Self-references now map to the declaring company.
    The stub never produced this, which is exactly why a regex stand-in cannot validate an LLM contract.

21. **Two words, one legal concept.** Model said SHAREHOLDER_OF, stub said MEMBER_OF, rulebook tested only
    MEMBER_OF for 2(76)(iv). Meera Rao's path failed silently under the model run and was masked by her
    husband's directorship path. Normalised at ingest. Lesson: schema vocabulary must be closed to the legal
    concepts, not to the words a model happens to choose.

22. **Zero rejections is not zero value.** The model quoted spans verbatim every time, so the validator never
    fired. The small-model run that was meant to exercise it was throttled. Record it as untested, not as proven.

23. **The nominee got a symptom indicator.** Silverline (designed miss) draws b2: Rs 35 cr lent to a Rs 10 lakh
    company. The relationship stays undetectable; the counterparty no longer passes silently. Same indicator
    fires on the promoter holding company — thin capital is the nature of a holding company, so b2 is noisy
    on exactly the disclosed promoter entities.
