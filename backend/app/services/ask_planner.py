"""Small query planner for approved date and LGA facts; no invented factual data."""
import re
from dataclasses import dataclass, field
from app.services.ask_language import normalized

# Search identifiers, not factual answers. Names resolve to ingested document IDs.
LGA_NAMES = ["ado ekiti", "aiyekire", "efon", "ekiti east", "ekiti south west",
             "ekiti west", "emure", "ido osi", "ijero", "ikere", "ikole", "ilejemeje",
             "irepodun ifelodun", "ise orun", "moba", "oye"]


CATEGORY_PATTERNS = {
    "tourism": (
        r"\b(tourism|tourist|attraction|attractions|waterfall|waterfalls|"
        r"spring|springs|resort|resorts|memorial park|tourist sites?)\b"
    ),
    "culture": (
        r"\b(culture|cultural|festival|festivals|tradition|traditional|"
        r"heritage|custom|customs)\b"
    ),
    "education": (
        r"\b(education|school|schools|university|universities|polytechnic|"
        r"polytechnics|college|colleges|institution|institutions)\b"
    ),
    "health": (
        r"\b(health|healthcare|hospital|hospitals|medical|medicine|"
        r"health programme|health program|ulerawa)\b"
    ),
    "agriculture": (
        r"\b(agriculture|agricultural|farming|farmer|farmers|farm|farms|"
        r"cassava|crop|crops)\b"
    ),
    "statistics": (
        r"\b(statistics|statistical|population|census|unemployment|"
        r"figures|data)\b"
    ),
    "history": (
        r"\b(history|historical|state creation|statehood)\b"
    ),
    "lgas": (
        r"\b(lga|lgas|local government|local governments)\b"
    ),
}


def topic_category(question):
    """Infer one explicit knowledge-base category from the question.

    If a question clearly spans more than one domain, return None so the
    caller does not silently discard part of the user's request.
    """
    q = normalized(question)

    matches = [
        category
        for category, pattern in CATEGORY_PATTERNS.items()
        if re.search(pattern, q)
    ]

    if len(matches) == 1:
        return matches[0]

    return None


def entities(question):
    remaining = " " + normalized(question) + " "
    found = []
    for name in sorted(LGA_NAMES, key=len, reverse=True):
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, remaining):
            found.append("lga-" + name.replace(" ", "-"))
            remaining = re.sub(pattern, " ", remaining)
    if re.search(r"\bgbonyin\b", remaining):
        found.append("lga-aiyekire")
    return sorted(set(found))


@dataclass
class Plan:
    queries: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    policy: str | None = None
    count: bool = False
    # Each query: (query text, exact doc IDs, fact kind)


def plan(question, language="en"):
    q = normalized(question)
    p = Plan()
    if not q or len(question.strip()) < 3:
        p.policy = "empty"
    elif len(question) > 1000:
        p.policy = "long"
    elif any(term in q for term in ("ignore your rules", "without sources", "pretend the knowledge",
                                   "you are now dan", "as if it s true")):
        p.policy = "injection"
    elif any(term in q for term in ("citizen story", "citizen stories", "community think", "2056")):
        p.policy = "citizen"
    elif any(term in q for term in ("governor then", "those population figures", "what about then")):
        p.policy = "clarify"
    elif language == "en" and ("jorwo" in q or "jowo" in q or "nipa" in q):
        p.policy = "mixed"
    elif "ghana" in q and "ekiti" not in q:
        p.policy = "scope"
    if p.policy:
        return p
    ids = entities(question)
    creation = (any(scope in q for scope in ("ekiti state", "ekiti become a state", "ipinle ekiti")) and any(term in q for term in
        ("created", "creation", "become a state", "established", "founded", "da ipinle ekiti sile")))
    if "ekiti state university" in q:
        creation = False
    # Keep unsupported constraints explicit rather than silently dropping them.
    fields = [(r"\b(population|census|olugbe|ikaniyan)\b", "population / iye olùgbé"),
              (r"\b(governor|governors|administrator|administrators)\b", "officeholders / àwọn alákóso"),
              (r"\b(tourism|tourist|springs|landmarks)\b", "tourism / ìrìn àjò afẹ́"),
              (r"\b(universities|university|institutions)\b", "education / ẹ̀kọ́"),
              (r"\b(hospitals|health)\b", "health / ìlera"),
              (r"\b(agricultural|agriculture)\b", "agriculture / iṣẹ́ àgbẹ̀"),
              (r"\b(unemployment|oil|borders|border|coordinates)\b", "other requested details / àwọn àlàyé mìíràn")]
    if creation:
        p.queries.append(("Ekiti State created", ["history-state-creation-1996"], "creation"))
        if re.search(r"\bwho\b", q) and not re.search(r"\bwhen\b", q):
            p.missing.append("who created the state / ẹni tí ó dá ìpínlẹ̀ sílẹ̀")
    has_hq = bool(re.search(r"\b(headquarters|headquarter|olu ijoba)\b", q))
    if has_hq and ids:
        p.queries.append(("headquarters", ids, "headquarters"))
    lga_topic = bool(re.search(r"\b(lgas?|local government|ijoba ibile)\b", q))
    p.count = lga_topic and any(term in q for term in ("how many", "list", "which", "melo")) and not has_hq
    if p.count and not ids and not any(re.search(pattern, q) for pattern, _ in fields):
        p.queries.append(("local government area", [], "identity"))
    elif p.count:
        p.count = False
    if q in {"tell me about ekiti", "about ekiti", "so fun mi nipa ekiti"}:
        p.queries.append(("Ekiti State created", ["history-state-creation-1996"], "creation"))
    if p.queries:
        p.missing.extend(label for pattern, label in fields if re.search(pattern, q))
        if ids and re.search(r"\bhistory\b", q):
            p.missing.append("LGA history / ìtàn ìjọba ìbílẹ̀")
    return p
