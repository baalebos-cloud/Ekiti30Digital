"""Compose cited facts with explicit missing coverage; never synthesize new facts."""
import re
from collections import defaultdict
from app.services.ask_language import message, yoruba_fact
from app.services.ask_planner import plan, entities

CITATION_KEYS = ("doc_id", "source_ids", "source_titles", "source_urls", "source_url",
                 "category", "tier", "last_verified", "path")


def response(question, language, search, category=None):
    p = plan(question, language)
    base = {"answer_status": "insufficient", "language": language, "citations": [],
            "statements": [], "coverage": "none", "missing": []}
    if p.policy:
        return dict(base, answer=message(p.policy, language), reason=p.policy)
    hits = []
    if p.queries:
        for query, ids, kind in p.queries:
            found = search(query, category=category, doc_ids=ids, fact_kind=kind, limit=20)
            hits.extend(found)
            if kind == "headquarters":
                present = {hit["doc_id"] for hit in found}
                p.missing.extend(ident.removeprefix("lga-") + " headquarters / olú ìjọba"
                                 for ident in ids if ident not in present)
    else:
        hits = search(question, category=category, doc_ids=entities(question), fact_kind=None, limit=5)
    seen = set()
    statements, citations = [], []
    for hit in hits:
        key = (hit["doc_id"], hit["content"])
        if key in seen:
            continue
        seen.add(key)
        content = hit["content"] if language == "en" else yoruba_fact(hit["content"])
        if content is None:
            p.missing.append(message("translation", language))
            continue
        citations.append({key: hit[key] for key in CITATION_KEYS})
        statements.append({"text": content, "citation_index": len(citations) - 1})
    if not statements:
        return dict(base, answer=message("insufficient", language), missing=p.missing,
                    reason="no_verified_match")
    # A numbered citation beside each fact removes ambiguity in multi-fact answers.
    answer = "\n".join(f"{item['text']} [{item['citation_index'] + 1}]" for item in statements)
    signatures = defaultdict(set)
    for hit in hits:
        signature = re.sub(r"\d+(?:[.,]\d+)*", "#", hit["content"])
        signatures[signature].add(hit["content"])
    conflict = any(len(values) > 1 for values in signatures.values())
    if conflict:
        answer += "\n" + ("The retrieved sources give different figures or dates. Compare the cited statements and their periods; no resolution is assumed."
                            if language == "en" else "Àwọn orísun tí a rí ní iye tàbí ọjọ́ tó yàtọ̀. Ṣe àfiwé àwọn ọ̀rọ̀ àti àsìkò wọn; a kò tíì pinnu èyí tó tọ́.")
    if any(term in question.casefold() for term in ("current", "today", "still operating")):
        dates = ", ".join(sorted({hit["last_verified"] for hit in hits}))
        answer += "\n" + (("Last verified: " + dates + ". This does not confirm live conditions.") if language == "en"
                            else "Ọjọ́ ìjẹ́rìí: " + dates + ". Èyí kò jẹ́rìí sí ipò ní báyìí.")
    if p.missing:
        prefix = "Not covered by the retrieved verified evidence: " if language == "en" else "Ẹ̀rí tí a rí kò bo àwọn wọ̀nyí: "
        answer += "\n" + prefix + "; ".join(dict.fromkeys(p.missing)) + "."
    return dict(base, answer=answer, answer_status="answered", citations=citations,
                statements=statements, missing=list(dict.fromkeys(p.missing)),
                coverage="partial" if p.missing else "supported", sources_differ=conflict)
