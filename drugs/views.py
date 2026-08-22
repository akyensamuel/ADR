"""
Drug catalog views — powered by OpenFDA and RxNorm APIs.

drug_list  → Search OpenFDA drug labels by name/keyword.
drug_detail → Fetch full OpenFDA label + RxNorm concept info for a drug.
"""

from __future__ import annotations

import urllib.parse

import requests
from django.shortcuts import render

# ── API base URLs ─────────────────────────────────────────────────────────────
OPENFDA_LABEL_URL = "https://api.fda.gov/drug/label.json"
RXNORM_SEARCH_URL = "https://rxnav.nlm.nih.gov/REST/drugs.json"
RXNORM_RELATED_URL = "https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/related.json"

_TIMEOUT = 8  # seconds


# ── Helpers ───────────────────────────────────────────────────────────────────

def _openfda_search(query: str, limit: int = 20) -> list[dict]:
    """Search OpenFDA drug labels. Returns a list of result dicts."""
    try:
        params = {
            "search": f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"',
            "limit": limit,
        }
        resp = requests.get(OPENFDA_LABEL_URL, params=params, timeout=_TIMEOUT)
        if resp.status_code == 200:
            return resp.json().get("results", [])
        # Fallback: broader full-text search
        params["search"] = query
        resp = requests.get(OPENFDA_LABEL_URL, params=params, timeout=_TIMEOUT)
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except requests.RequestException:
        pass
    return []


def _openfda_by_name(name: str) -> dict | None:
    """Fetch the first OpenFDA label result for an exact brand/generic name."""
    results = _openfda_search(name, limit=1)
    return results[0] if results else None


def _rxnorm_lookup(name: str) -> dict:
    """Return RxNorm concept info (rxcui, synonyms) for a drug name."""
    info: dict = {"rxcui": None, "synonyms": []}
    try:
        resp = requests.get(
            RXNORM_SEARCH_URL,
            params={"name": name},
            timeout=_TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json()
            concept_group = data.get("drugGroup", {}).get("conceptGroup", [])
            for group in concept_group:
                for prop in group.get("conceptProperties", []):
                    if not info["rxcui"]:
                        info["rxcui"] = prop.get("rxcui")
                    info["synonyms"].append(prop.get("name", ""))
    except requests.RequestException:
        pass
    return info


def _extract_label_field(label: dict, *keys: str) -> str:
    """
    Extract the first non-empty value from a list of label section keys.
    OpenFDA label fields are lists of strings; we join them.
    """
    for key in keys:
        val = label.get(key, [])
        if val:
            return " ".join(val)
    return ""


def _parse_drug_card(label: dict) -> dict:
    """Turn a raw OpenFDA label result into a simplified card dict."""
    fda = label.get("openfda", {})
    brand_names = fda.get("brand_name", [])
    generic_names = fda.get("generic_name", [])
    name = brand_names[0] if brand_names else (generic_names[0] if generic_names else "Unknown")

    return {
        "name": name.title(),
        "brand_names": [n.title() for n in brand_names[:3]],
        "generic_names": [n.title() for n in generic_names[:3]],
        "manufacturer": (fda.get("manufacturer_name") or [""])[0].title(),
        "route": (fda.get("route") or [""])[0].title(),
        "slug": urllib.parse.quote(name, safe=""),
        "purpose": _extract_label_field(label, "purpose", "indications_and_usage")[:300],
    }


# ── Views ─────────────────────────────────────────────────────────────────────

def drug_list(request):
    query = request.GET.get("q", "").strip()
    drugs = []
    error = ""

    search_term = query or "common medication"
    raw = _openfda_search(search_term, limit=24)
    if raw:
        seen: set[str] = set()
        for label in raw:
            card = _parse_drug_card(label)
            key = card["name"].lower()
            if key not in seen:
                seen.add(key)
                drugs.append(card)
    elif query:
        error = f'No results found for "{query}". Try a different drug name.'

    return render(request, "drugs/drug_list.html", {
        "drugs": drugs,
        "query": query,
        "error": error,
    })


def drug_detail(request, slug: str):
    name = urllib.parse.unquote(slug)
    label = _openfda_by_name(name)
    error = ""
    drug = {}

    if label:
        fda = label.get("openfda", {})
        brand_names = fda.get("brand_name", [])
        generic_names = fda.get("generic_name", [])
        display_name = brand_names[0] if brand_names else (generic_names[0] if generic_names else name)

        drug = {
            "name": display_name.title(),
            "brand_names": [n.title() for n in brand_names],
            "generic_names": [n.title() for n in generic_names],
            "manufacturer": (fda.get("manufacturer_name") or [""])[0],
            "route": (fda.get("route") or [""])[0].title(),
            "dosage_form": (fda.get("dosage_form") or [""])[0].title(),
            "product_type": (fda.get("product_type") or [""])[0].title(),
            "purpose": _extract_label_field(label, "purpose"),
            "indications": _extract_label_field(label, "indications_and_usage"),
            "warnings": _extract_label_field(label, "warnings", "warnings_and_cautions"),
            "adverse_reactions": _extract_label_field(label, "adverse_reactions"),
            "drug_interactions": _extract_label_field(label, "drug_interactions"),
            "dosage": _extract_label_field(label, "dosage_and_administration"),
            "contraindications": _extract_label_field(label, "contraindications"),
        }

        # Enrich with RxNorm data
        rxnorm = _rxnorm_lookup(display_name)
        drug["rxcui"] = rxnorm["rxcui"]
        drug["synonyms"] = rxnorm["synonyms"][:8]
    else:
        error = f'No OpenFDA data found for "{name}".'

    return render(request, "drugs/drug_detail.html", {
        "drug": drug,
        "slug": slug,
        "error": error,
    })
