"""Seeded generator for the synthetic listed company "Meridian Agro Industries Limited".

Everything produced here is MADE UP. Names, DINs, CINs, PANs, amounts and documents
are fictional. The company is designed so that each planted case exercises one
part of the screening pipeline; two cases (12 and 13) are designed to be missed,
because the information needed to find them is not in any public record or in
the company's own books.

Outputs (all JSON) into data/synthetic/:
  registry.json          - MCA-style snapshot of entities, directors, addresses
  shareholding.json      - quarterly shareholding pattern of the listed company
  group.json             - subsidiaries / associates from AOC-1
  mbp1.json              - directors' MBP-1 declarations (prose)
  ledger.json            - FY2025-26 transactions with counterparties
  vendor_master.json     - counterparty names/identifiers as the books hold them
  management_rp_list.json- the list management gave the auditor
  indas24_note.json      - draft related-party disclosure note
  approvals.json         - audit committee / shareholder approvals
  expected.json          - planted cases and what the pipeline should do
"""
from __future__ import annotations

import json
import os
import random
from datetime import date

SEED = 20261102
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
RETRIEVED = "2026-04-15"
PERIOD_START = "2025-04-01"
PERIOD_END = "2026-03-31"

COMPANY_ID = "E0"


def d(s):
    return s


def make_people():
    return [
        {"id": "P1", "name": "Rajan Rao", "din": "00123456", "roles": [("E0", "DIRECTOR_OF", "2004-06-01", None, "Managing Director")]},
        {"id": "P2", "name": "Meera Rao", "din": "00123457", "roles": [("E0", "DIRECTOR_OF", "2010-04-01", None, "Non-Executive Director")]},
        {"id": "P3", "name": "Arvind Shah", "din": "01122334", "roles": [("E0", "DIRECTOR_OF", "2019-08-01", None, "Independent Director"), ("E3", "DIRECTOR_OF", "2015-03-01", None, "Director")]},
        {"id": "P4", "name": "Suresh Iyer", "din": "02233445", "roles": [("E0", "DIRECTOR_OF", "2017-01-15", "2025-11-15", "Whole-time Director"), ("E5", "DIRECTOR_OF", "2012-07-01", None, "Director")]},
        {"id": "P5", "name": "Nitin Kulkarni", "din": None, "roles": [("E0", "KMP_OF", "2020-05-01", None, "Chief Financial Officer")]},
        {"id": "P6", "name": "Priya Menon", "din": None, "roles": [("E0", "KMP_OF", "2021-09-01", None, "Company Secretary")]},
        {"id": "P7", "name": "Kavya Rao", "din": None, "roles": []},
        {"id": "P8", "name": "Deepak Verma", "din": "03344556", "roles": [("E15", "DIRECTOR_OF", "2018-02-01", None, "Director")]},
        {"id": "P9", "name": "Anil Desai", "din": "04455667", "roles": [("E0", "DIRECTOR_OF", "2021-02-01", None, "Independent Director"), ("E4", "DIRECTOR_OF", "2016-11-01", None, "Director")]},
        {"id": "P10", "name": "Vikram Rao", "din": "05566778", "roles": [("E7", "DIRECTOR_OF", "2014-05-01", None, "Director")]},
        {"id": "P11", "name": "Sanjay Bhatt", "din": "06677889", "roles": [("E12", "DIRECTOR_OF", "2011-01-01", None, "Director")]},
        {"id": "P12", "name": "Ritu Agarwal", "din": "07788990", "roles": [("E13", "DIRECTOR_OF", "2025-02-10", None, "Director")]},
        {"id": "P13", "name": "Mohan Pillai", "din": "08899001", "roles": [("E8", "DIRECTOR_OF", "2013-06-01", None, "Director"), ("E9", "DIRECTOR_OF", "2016-01-01", None, "Director")]},
    ]


ADDR_PROMOTER = "Rao House, 14 Marine Lines, Mumbai 400020, Maharashtra"
ADDR_HQ = "Meridian Tower, Plot 7, Bandra Kurla Complex, Mumbai 400051, Maharashtra"


def make_entities(rng):
    ents = [
        {"id": "E0", "name": "Meridian Agro Industries Limited", "cin": "L15100MH2004PLC147001", "pan": "AAACM1234A", "address": ADDR_HQ, "incorporated_on": "2004-06-01", "paid_up_capital_cr": 120.0, "is_public": True, "listed": True},
        {"id": "E1", "name": "Meridian Logistics Private Limited", "cin": "U63000MH2012PTC231002", "pan": "AAACM5678B", "address": ADDR_HQ, "incorporated_on": "2012-03-15", "paid_up_capital_cr": 25.0, "is_public": False},
        {"id": "E2", "name": "Rao Family Holdings Private Limited", "cin": "U65990MH1998PTC116003", "pan": "AAACR9012C", "address": ADDR_PROMOTER, "incorporated_on": "1998-09-20", "paid_up_capital_cr": 5.0, "is_public": False},
        {"id": "E3", "name": "Sunrise Agro Private Limited", "cin": "U01100GJ2015PTC082004", "pan": "AABCS3456D", "address": "Plot 22, GIDC Vatva, Ahmedabad 382445, Gujarat", "incorporated_on": "2015-03-01", "paid_up_capital_cr": 2.0, "is_public": False},
        {"id": "E4", "name": "Bharat Cold Chain Private Limited", "cin": "U63020MH2016PTC284005", "pan": "AABCB7890E", "address": "Gala 9, MIDC Taloja, Navi Mumbai 410208, Maharashtra", "incorporated_on": "2016-11-01", "paid_up_capital_cr": 3.5, "is_public": False},
        {"id": "E5", "name": "Iyer Infra Private Limited", "cin": "U45200TN2012PTC086006", "pan": "AABCI1234F", "address": "18 Anna Salai, Chennai 600002, Tamil Nadu", "incorporated_on": "2012-07-01", "paid_up_capital_cr": 1.0, "is_public": False},
        {"id": "E7", "name": "Rao Warehousing Private Limited", "cin": "U63090MH2014PTC255007", "pan": "AABCR5678G", "address": "Warehouse 3, Bhiwandi 421302, Maharashtra", "incorporated_on": "2014-05-01", "paid_up_capital_cr": 4.0, "is_public": False},
        {"id": "E8", "name": "Greenfield Packaging Private Limited", "cin": "U21000MH2013PTC243008", "pan": "AABCG9012H", "address": ADDR_PROMOTER, "incorporated_on": "2013-06-01", "paid_up_capital_cr": 1.5, "is_public": False},
        {"id": "E9", "name": "Coastal Agri Ventures Private Limited", "cin": "U01400MH2016PTC271009", "pan": "AABCC3456I", "address": "Unit 5, Ratnagiri Industrial Estate, Ratnagiri 415612, Maharashtra", "incorporated_on": "2016-01-01", "paid_up_capital_cr": 10.0, "is_public": False,
         "shareholders_filing": [{"holder": "E2", "pct": 60.0}, {"holder": "P13", "pct": 40.0}]},
        {"id": "E10", "name": "Horizon Capital Partners LLP", "llpin": "AAB-1234", "pan": "AAEFH7890J", "address": "Level 9, One BKC, Mumbai 400051, Maharashtra", "incorporated_on": "2011-10-10", "paid_up_capital_cr": 50.0, "is_public": False, "kind": "llp"},
        {"id": "E11", "name": "Nordic Agri Fund", "pan": "AADCN1234K", "address": "c/o Custodian, Nariman Point, Mumbai 400021, Maharashtra", "incorporated_on": "2009-01-01", "paid_up_capital_cr": None, "is_public": False, "kind": "fpi"},
        {"id": "E12", "name": "Sunrise Agro Foods Limited", "cin": "L15400GJ2011PLC064012", "pan": "AABCS9999L", "address": "Sarkhej Road, Ahmedabad 380055, Gujarat", "incorporated_on": "2011-01-01", "paid_up_capital_cr": 40.0, "is_public": True},
        {"id": "E13", "name": "Apex Machinery Private Limited", "cin": "U29200MH2025PTC401013", "pan": "AABCA1111M", "address": "Shed 2, Chakan Industrial Area, Pune 410501, Maharashtra", "incorporated_on": "2025-02-10", "paid_up_capital_cr": 0.01, "is_public": False},
        {"id": "E15", "name": "Verma Agrotech Private Limited", "cin": "U01100MH2018PTC305015", "pan": "AABCV2222N", "address": "Office 4, Nashik Road, Nashik 422101, Maharashtra", "incorporated_on": "2018-02-01", "paid_up_capital_cr": 2.0, "is_public": False},
        {"id": "E16", "name": "Silverline Nominees Private Limited", "cin": "U67100MH2019PTC322016", "pan": "AABCS3333P", "address": "Office 11, Fort, Mumbai 400001, Maharashtra", "incorporated_on": "2019-04-01", "paid_up_capital_cr": 0.1, "is_public": False},
        {"id": "E18", "name": "Delta Seeds Private Limited", "cin": "U01110MH2010PTC201018", "pan": "AABCD4444Q", "address": "Plot 3, MIDC Jalna 431203, Maharashtra", "incorporated_on": "2010-08-08", "paid_up_capital_cr": 6.0, "is_public": False},
    ]
    # Filler vendors: ordinary, registered, unrelated directors.
    filler_words_a = ["Prime", "Shakti", "Kaveri", "Everest", "Lotus", "Narmada", "Tulsi", "Indus", "Saffron", "Vega", "Mahi", "Ashoka", "Garuda", "Krishna", "Amber", "Sahyadri", "Zenith", "Orchid", "Vindhya", "Aravali"]
    filler_words_b = ["Fertilisers", "Logistics", "Irrigation", "Packaging", "Transport", "Agrochem", "Seeds", "Engineering", "Traders", "Cold Storage"]
    cities = [("Pune", "411001", "Maharashtra"), ("Nagpur", "440001", "Maharashtra"), ("Indore", "452001", "Madhya Pradesh"), ("Surat", "395003", "Gujarat"), ("Hyderabad", "500001", "Telangana"), ("Coimbatore", "641001", "Tamil Nadu")]
    for i in range(20):
        a = filler_words_a[i]
        b = filler_words_b[i % len(filler_words_b)]
        city, pin, state = cities[i % len(cities)]
        eid = f"E{20 + i}"
        year = rng.randint(2005, 2021)
        ents.append({
            "id": eid, "name": f"{a} {b} Private Limited",
            "cin": f"U{rng.randint(10000, 99999)}MH{year}PTC{rng.randint(100000, 399999)}",
            "pan": f"AAB{chr(65 + i % 26)}{a[0]}{rng.randint(1000, 9999)}{chr(65 + (i * 7) % 26)}",
            "address": f"Plot {rng.randint(1, 99)}, Industrial Area, {city} {pin}, {state}",
            "incorporated_on": f"{year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            "paid_up_capital_cr": round(rng.uniform(0.5, 20.0), 2), "is_public": False,
            "filler_director": {"din": f"{rng.randint(10000000, 99999999)}", "name": f"Director {eid}"},
        })
    return ents


def build_registry(people, ents):
    directors_by_entity = {}
    for p in people:
        for ent_id, role, frm, to, desig in p["roles"]:
            if role != "DIRECTOR_OF":
                continue
            directors_by_entity.setdefault(ent_id, []).append({"din": p["din"], "name": p["name"], "designation": desig, "from": frm, "to": to})
    records = []
    for e in ents:
        rec = {
            "entity_id": e["id"], "name": e["name"], "cin": e.get("cin"), "llpin": e.get("llpin"), "pan": e.get("pan"),
            "registered_address": e["address"], "incorporated_on": e["incorporated_on"],
            "paid_up_capital_cr": e["paid_up_capital_cr"], "is_public": e["is_public"], "kind": e.get("kind", "company"),
            "directors": directors_by_entity.get(e["id"], []),
            "retrieved_at": RETRIEVED, "source": f"mca_master_data:{e.get('cin') or e.get('llpin') or e.get('pan')}",
        }
        if "filler_director" in e:
            rec["directors"].append({"din": e["filler_director"]["din"], "name": e["filler_director"]["name"], "designation": "Director", "from": e["incorporated_on"], "to": None})
        if "shareholders_filing" in e:
            rec["shareholders_filing"] = {"source": f"mgt7_inspection:{e['cin']}:FY2024-25", "holders": e["shareholders_filing"]}
        records.append(rec)
    # KMP from the annual report (not MCA): recorded separately as a books/filing source.
    kmp = [{"person_id": p["id"], "name": p["name"], "designation": r[4], "from": r[2], "to": r[3], "source": "annual_report_FY2024-25:board_report:p.41"}
           for p in people for r in p["roles"] if r[1] == "KMP_OF"]
    return {"entities": records, "kmp": kmp, "people_dins": {p["din"]: {"person_id": p["id"], "name": p["name"]} for p in people if p["din"]}}


def build_shareholding():
    # Quarterly shareholding pattern of E0, as filed with the exchange (Reg 31).
    quarters = ["2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31"]
    rows = []
    for q in quarters:
        rows.extend([
            {"quarter_end": q, "category": "promoter_group", "holder": "Rajan Rao", "holder_id": "P1", "pct": 10.0},
            {"quarter_end": q, "category": "promoter_group", "holder": "Meera Rao", "holder_id": "P2", "pct": 5.0},
            {"quarter_end": q, "category": "promoter_group", "holder": "Rao Family Holdings Private Limited", "holder_id": "E2", "pct": 32.0},
            {"quarter_end": q, "category": "public", "holder": "Horizon Capital Partners LLP", "holder_id": "E10", "pct": 9.5},
            {"quarter_end": q, "category": "public", "holder": "Nordic Agri Fund", "holder_id": "E11", "pct": 15.0},
            {"quarter_end": q, "category": "public", "holder": "Silverline Nominees Private Limited", "holder_id": "E16", "pct": 8.0},
            {"quarter_end": q, "category": "public", "holder": "Other public", "holder_id": None, "pct": 20.5},
        ])
    return {"company_id": COMPANY_ID, "source": "exchange_filing:reg31_shareholding_pattern", "retrieved_at": RETRIEVED, "rows": rows}


def build_group():
    return {"company_id": COMPANY_ID, "source": "annual_report_FY2024-25:AOC-1", "retrieved_at": RETRIEVED,
            "subsidiaries": [{"entity_id": "E1", "name": "Meridian Logistics Private Limited", "pct": 100.0, "since": "2012-03-15"}],
            "associates": [],
            "consolidated_turnover_cr_FY2024_25": 25000.0}


def build_mbp1():
    # Directors' declarations of interest (Section 184, Form MBP-1), as prose.
    return {"source": "books:mbp1_declarations_FY2025-26", "declarations": [
        {"director_id": "P1", "director": "Rajan Rao", "date": "2025-04-05",
         "text": ("I, Rajan Rao, hereby declare my concern or interest in the following: I am a director and shareholder of "
                  "Rao Family Holdings Private Limited. My wife Meera Rao is a director of the Company. My brother Vikram Rao is a "
                  "director of Rao Warehousing Private Limited. My daughter Kavya Rao is a partner in the firm Kavya Traders.")},
        {"director_id": "P2", "director": "Meera Rao", "date": "2025-04-05",
         "text": ("I, Meera Rao, hereby declare that I am a shareholder of Rao Family Holdings Private Limited and hold no other "
                  "directorships or partnerships.")},
        {"director_id": "P3", "director": "Arvind Shah", "date": "2025-04-07",
         "text": "I, Arvind Shah, declare that I hold directorships in the following bodies corporate: Shah Advisory Services LLP."},
        {"director_id": "P4", "director": "Suresh Iyer", "date": "2025-04-06",
         "text": "I, Suresh Iyer, declare that I am a director of Iyer Infra Private Limited and hold 60 per cent of its shares."},
        {"director_id": "P9", "director": "Anil Desai", "date": "2025-04-08",
         "text": "I, Anil Desai, declare that I have no concern or interest in any body corporate or firm other than the Company."},
    ]}


def build_vendor_master():
    # How the books refer to counterparties. Identifiers are present for some, absent for others.
    return {"source": "books:vendor_master", "counterparties": [
        {"ledger_id": "V001", "name": "Meridian Logistics Pvt Ltd", "pan": "AAACM5678B", "cin": "U63000MH2012PTC231002", "gstin": "27AAACM5678B1Z5"},
        {"ledger_id": "V002", "name": "Rao Family Holdings Pvt. Ltd.", "pan": "AAACR9012C", "cin": None, "gstin": None},
        {"ledger_id": "V003", "name": "Sunrise Agro Pvt Ltd", "pan": None, "cin": "U01100GJ2015PTC082004", "gstin": "24AABCS3456D1Z2"},
        {"ledger_id": "V004", "name": "BHARAT COLDCHAIN PVT LTD", "pan": None, "cin": None, "gstin": None},
        {"ledger_id": "V005", "name": "Iyer Infra Private Limited", "pan": "AABCI1234F", "cin": None, "gstin": None},
        {"ledger_id": "V006", "name": "Kavya Traders", "pan": "AAFFK5678R", "cin": None, "gstin": "27AAFFK5678R1ZQ"},
        {"ledger_id": "V007", "name": "Rao Warehousing Pvt Ltd", "pan": None, "cin": None, "gstin": "27AABCR5678G1Z1"},
        {"ledger_id": "V008", "name": "Greenfield Packaging Private Limited", "pan": "AABCG9012H", "cin": None, "gstin": None},
        {"ledger_id": "V009", "name": "Coastal Agri Ventures Pvt Ltd", "pan": "AABCC3456I", "cin": None, "gstin": None},
        {"ledger_id": "V010", "name": "Horizon Capital Partners LLP", "pan": "AAEFH7890J", "cin": None, "gstin": None},
        {"ledger_id": "V011", "name": "Nordic Agri Fund", "pan": "AADCN1234K", "cin": None, "gstin": None},
        {"ledger_id": "V012", "name": "Sunrise Agro Foods Ltd", "pan": None, "cin": None, "gstin": None},
        {"ledger_id": "V013", "name": "Apex Machinery Pvt Ltd", "pan": "AABCA1111M", "cin": None, "gstin": None},
        {"ledger_id": "V015", "name": "Verma Agrotech Pvt Ltd", "pan": "AABCV2222N", "cin": None, "gstin": None},
        {"ledger_id": "V016", "name": "Silverline Nominees Pvt Ltd", "pan": "AABCS3333P", "cin": None, "gstin": None},
        {"ledger_id": "V017", "name": "Ramesh Transport", "pan": None, "cin": None, "gstin": None},
        {"ledger_id": "V018", "name": "Delta Seeds Pvt Ltd", "pan": "AABCD4444Q", "cin": None, "gstin": None},
    ]}


def add_filler_vendors(vm, ents):
    n = 20
    for e in ents:
        if not e["id"].startswith("E") or int(e["id"][1:]) < 20:
            continue
        vm["counterparties"].append({"ledger_id": f"V0{n}", "name": e["name"].replace("Private Limited", "Pvt Ltd"), "pan": e["pan"], "cin": None, "gstin": None})
        n += 1


def build_ledger(rng, vm):
    rows = []
    counter = [0]

    def add(ledger_id, name, dt, kind, amount):
        counter[0] += 1
        rows.append({"row_id": f"GL{counter[0]:05d}", "date": dt, "counterparty_id": ledger_id, "counterparty_name": name, "kind": kind, "amount_cr": round(amount, 2)})

    names = {c["ledger_id"]: c["name"] for c in vm["counterparties"]}
    # E1 subsidiary: disclosed purchases 120 cr but ledger gross 310 cr (case 11)
    for m, amt in [("2025-04-20", 60), ("2025-06-15", 55), ("2025-08-10", 70), ("2025-10-05", 45), ("2025-12-20", 40), ("2026-02-14", 40)]:
        add("V001", names["V001"], m, "service", amt)
    # E2 promoter entity: 1,800 cr purchases across year (materiality demonstration)
    for m, amt in [("2025-05-10", 300), ("2025-07-12", 350), ("2025-09-18", 400), ("2025-11-22", 250), ("2026-01-15", 300), ("2026-03-10", 200)]:
        add("V002", names["V002"], m, "purchase", amt)
    # E3 undisclosed vendor, director overlap
    for m, amt in [("2025-05-02", 12), ("2025-09-09", 18), ("2026-01-20", 15)]:
        add("V003", names["V003"], m, "purchase", amt)
    # E4 fuzzy name
    for m, amt in [("2025-06-01", 8), ("2025-12-01", 9)]:
        add("V004", names["V004"], m, "service", amt)
    # E5 resigned director: transactions before and after cessation (2025-11-15)
    add("V005", names["V005"], "2025-08-05", "service", 22)
    add("V005", names["V005"], "2026-02-18", "service", 25)
    # E6 relative's firm (prose only)
    add("V006", names["V006"], "2025-07-07", "purchase", 6)
    add("V006", names["V006"], "2026-01-11", "purchase", 7)
    # E7 relative director
    add("V007", names["V007"], "2025-10-10", "rent", 11)
    # E8 common address
    add("V008", names["V008"], "2025-06-20", "purchase", 14)
    # E9 two-hop via promoter entity
    add("V009", names["V009"], "2025-09-01", "purchase", 30)
    # E10 9.5% holder: a consulting fee
    add("V010", names["V010"], "2025-08-15", "service", 2)
    # E11 15% holder: loan taken
    add("V011", names["V011"], "2025-06-30", "loan_taken", 150)
    # E12 decoy
    add("V012", names["V012"], "2025-11-11", "sale", 20)
    # E13 legit new vendor: large advance, GRN later
    add("V013", names["V013"], "2025-06-12", "advance", 40)
    add("V013", names["V013"], "2026-01-25", "grn", 38)
    # E15 undeclared relative
    add("V015", names["V015"], "2025-09-15", "purchase", 19)
    # E16 nominee, 8%
    add("V016", names["V016"], "2025-10-01", "loan_given", 35)
    # E17 unresolved sole proprietor
    add("V017", names["V017"], "2025-05-25", "service", 1.2)
    # E18 clean negative
    add("V018", names["V018"], "2025-07-01", "purchase", 9)
    # fillers
    for c in vm["counterparties"]:
        if int(c["ledger_id"][1:]) >= 20:
            for _ in range(rng.randint(1, 3)):
                dt = f"2025-{rng.randint(4, 12):02d}-{rng.randint(1, 28):02d}"
                add(c["ledger_id"], c["name"], dt, rng.choice(["purchase", "service", "purchase"]), rng.uniform(0.5, 12))
    rows.sort(key=sort_by_date)
    return {"source": "books:general_ledger_FY2025-26", "period": [PERIOD_START, PERIOD_END], "rows": rows}


def sort_by_date(r):
    return r["date"]


def build_mgmt_list():
    return {"source": "books:management_related_party_list_FY2025-26", "parties": [
        {"name": "Rajan Rao", "relationship": "Managing Director, promoter"},
        {"name": "Meera Rao", "relationship": "Director, promoter"},
        {"name": "Arvind Shah", "relationship": "Independent Director"},
        {"name": "Suresh Iyer", "relationship": "Whole-time Director (till 15 Nov 2025)"},
        {"name": "Anil Desai", "relationship": "Independent Director"},
        {"name": "Nitin Kulkarni", "relationship": "CFO"},
        {"name": "Priya Menon", "relationship": "Company Secretary"},
        {"name": "Meridian Logistics Private Limited", "relationship": "Wholly owned subsidiary"},
        {"name": "Rao Family Holdings Private Limited", "relationship": "Promoter group entity"},
    ]}


def build_indas24():
    return {"source": "books:draft_financial_statements_FY2025-26:note_38_related_parties", "categories": [
        {"category": "Subsidiary", "party": "Meridian Logistics Private Limited", "ledger_id": "V001", "transaction_type": "Services availed", "disclosed_amount_cr": 120.0},
        {"category": "Promoter group entity", "party": "Rao Family Holdings Private Limited", "ledger_id": "V002", "transaction_type": "Purchase of goods", "disclosed_amount_cr": 1800.0},
        {"category": "KMP", "party": "Key managerial personnel", "ledger_id": None, "transaction_type": "Remuneration", "disclosed_amount_cr": 9.4},
    ]}


def build_approvals():
    return {"source": "books:audit_committee_minutes_FY2025-26", "approvals": [
        {"party": "Meridian Logistics Private Limited", "ledger_id": "V001", "type": "omnibus", "limit_cr": 400.0, "date": "2025-04-10", "minute_ref": "AC/2025-26/01/item4"},
        {"party": "Rao Family Holdings Private Limited", "ledger_id": "V002", "type": "omnibus", "limit_cr": 2500.0, "date": "2025-04-10", "minute_ref": "AC/2025-26/01/item5"},
        {"party": "Rao Family Holdings Private Limited", "ledger_id": "V002", "type": "shareholder", "limit_cr": 2500.0, "date": "2025-09-26", "minute_ref": "AGM/2025/resolution7"},
    ]}


def build_expected():
    return {"period": [PERIOD_START, PERIOD_END], "cases": [
        {"case": 1, "ledger_id": "V001", "title": "Disclosed subsidiary", "expect": "rule_hit", "clause": "CA2013_2(76)(viii)", "evidence_tier": 1, "designed_miss": False,
         "note": "Should be found and marked as disclosed by management."},
        {"case": 2, "ledger_id": "V003", "title": "Undisclosed vendor sharing a director (Arvind Shah)", "expect": "rule_hit", "clause": "CA2013_2(76)(iv)", "evidence_tier": 0, "designed_miss": False,
         "note": "CIN present in ledger; registry-backed path; not on management list."},
        {"case": 3, "ledger_id": "V006", "title": "Relative's firm named only in MBP-1 prose (Kavya Traders)", "expect": "rule_hit", "clause": "CA2013_2(76)(iii)", "evidence_tier": 3, "designed_miss": False,
         "note": "No registry record for the firm; depends on extractor reading the MBP-1 text."},
        {"case": 3, "ledger_id": "V007", "title": "Relative (brother, prose) is director (registry) of vendor", "expect": "rule_hit", "clause": "CA2013_2(76)(iv)", "evidence_tier": 3, "designed_miss": False,
         "note": "Mixed path: RELATIVE_OF from LLM, DIRECTOR_OF from MCA."},
        {"case": 4, "ledger_id": "V004", "title": "Name variant, no identifier (BHARAT COLDCHAIN PVT LTD)", "expect": "rule_hit", "clause": "CA2013_2(76)(iv)", "evidence_tier": 2, "designed_miss": False,
         "note": "Fuzzy merge then registry path via Anil Desai."},
        {"case": 5, "ledger_id": "V008", "title": "Common registered address with promoter entity", "expect": "indicator", "clause": None, "evidence_tier": 5, "designed_miss": False,
         "note": "Not a related party under any clause; indicator (a) only."},
        {"case": 6, "ledger_id": "V009", "title": "Two-hop: 60% owned by promoter-group entity", "expect": "indicator", "clause": None, "evidence_tier": 5, "designed_miss": False,
         "note": "Shares a shareholder with promoter group; purpose-and-effect candidate, human decides."},
        {"case": 7, "ledger_id": "V010", "title": "9.5% holder, just under LODR threshold", "expect": "none", "clause": None, "evidence_tier": None, "designed_miss": False,
         "note": "Hard negative: must not fire."},
        {"case": 8, "ledger_id": "V005", "title": "Director resigned 15 Nov 2025; transactions before and after", "expect": "rule_hit", "clause": "CA2013_2(76)(iv)", "evidence_tier": 0, "designed_miss": False,
         "note": "Related for part of period; window must end 2025-11-15 and the Feb 2026 transaction flagged as outside."},
        {"case": 9, "ledger_id": "V013", "title": "Legitimate new vendor with large advance", "expect": "indicator", "clause": None, "evidence_tier": 5, "designed_miss": False,
         "note": "Indicators (b) and (c) fire; expected reviewer rejection (false positive by design)."},
        {"case": 10, "ledger_id": "V012", "title": "Decoy: Sunrise Agro Foods Ltd", "expect": "none", "clause": None, "evidence_tier": None, "designed_miss": False,
         "note": "Resolver must not merge with Sunrise Agro Private Limited."},
        {"case": 11, "ledger_id": "V001", "title": "Disclosed but understated (120 cr disclosed, 310 cr in ledger)", "expect": "reconciliation", "clause": None, "evidence_tier": 4, "designed_miss": False,
         "note": "Coffee Day pattern."},
        {"case": 12, "ledger_id": "V015", "title": "Undeclared relative (Meera Rao's brother) directs vendor", "expect": "none", "clause": None, "evidence_tier": None, "designed_miss": True,
         "note": "Relationship exists but appears in no record available to the auditor. Designed miss."},
        {"case": 13, "ledger_id": "V016", "title": "Nominee holding 8% for promoter, undeclared", "expect": "none", "clause": None, "evidence_tier": None, "designed_miss": True,
         "note": "Below threshold and beneficial interest undeclared. Designed miss."},
        {"case": 14, "ledger_id": "V011", "title": "15% holder: RP only under post-Apr-2023 10% rule", "expect": "rule_hit", "clause": "LODR_2(1)(zb)(b)", "evidence_tier": 1, "designed_miss": False,
         "note": "Would not fire under the 20% rule in force before 1 Apr 2023."},
        {"case": 15, "ledger_id": "V017", "title": "Sole proprietor with no registry record", "expect": "unresolved", "clause": None, "evidence_tier": None, "designed_miss": False,
         "note": "Must appear on the unresolved list, not silently pass."},
        {"case": 16, "ledger_id": "V002", "title": "Materiality: 1,800 cr with promoter entity, two regimes in one FY", "expect": "rule_hit", "clause": "LODR_2(1)(zb)(a)", "evidence_tier": 1, "designed_miss": False,
         "note": "Crosses old threshold (1,000 cr) on 2025-09-18; Schedule XII tier (2,250 cr) not crossed. Approvals on record."},
    ]}


def main():
    rng = random.Random(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)
    people = make_people()
    ents = make_entities(rng)
    registry = build_registry(people, ents)
    vm = build_vendor_master()
    add_filler_vendors(vm, ents)
    outputs = {
        "registry.json": registry,
        "shareholding.json": build_shareholding(),
        "group.json": build_group(),
        "mbp1.json": build_mbp1(),
        "vendor_master.json": vm,
        "ledger.json": build_ledger(rng, vm),
        "management_rp_list.json": build_mgmt_list(),
        "indas24_note.json": build_indas24(),
        "approvals.json": build_approvals(),
        "expected.json": build_expected(),
    }
    for fname, obj in outputs.items():
        with open(os.path.join(OUT_DIR, fname), "w") as f:
            json.dump(obj, f, indent=2)
    print(f"wrote {len(outputs)} files to {os.path.abspath(OUT_DIR)}")
    print(f"entities: {len(registry['entities'])}, ledger rows: {len(outputs['ledger.json']['rows'])}, counterparties: {len(vm['counterparties'])}")


if __name__ == "__main__":
    main()
