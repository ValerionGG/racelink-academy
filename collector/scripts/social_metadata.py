"""Lossless-source social metadata separation, using only Python's stdlib.

normalize_social_metadata(record, title_override=None) returns a new dictionary:
title, description, hashtags, mentions, links, needs_title_review,
source_metadata, field_provenance and normalization. Hashtags/mentions include
their #/@ prefix and retain the first observed spelling. No language detection,
network, database access, compatibility inference or generated wording occurs.

Pass an editorial override as {"title": "...", "basis": "..."}. A caption's
short title must be an exact complete sentence or Markdown heading; otherwise
the source's first line remains a provisional title with needs_title_review=true.
Textless inputs remain empty instead of receiving an invented title. Native titles are never cut to
fit a length limit (long native titles are merely flagged for review).
"""
from __future__ import annotations

import copy
import html
import json
import re
import unicodedata
from collections.abc import Mapping

VERSION = "1.0.4"
MAX_EXTRACTED_TITLE = 180
TEXT_FIELDS = ("title", "description", "caption", "text", "desc", "sourceDescription",
               "source_title", "original_title", "indexed_title", "source_caption")
CONTEXT_FIELDS = ("id", "platform", "creator", "verification_scope", "verificationScope",
    "description_basis", "descriptionType", "description_type", "title_basis", "provenance",
    "collection_provenance", "_collection", "url", "source_url", "hashtags", "mentions", "links")
LINK_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"\u201c\u201d]+", re.I)
ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "prof", "st", "no", "fig", "vs", "etc", "e.g", "i.e"}


def _word(char):
    return bool(char) and (unicodedata.category(char)[0] in "LMN" or char == "_")


def _key(value):
    return unicodedata.normalize("NFC", value).casefold()


def _dedupe(values, kind):
    seen, result = set(), []
    for value in values:
        key = value if kind == "links" else _key(value.replace("＃", "#", 1))
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _clean_spacing(value):
    # Preserve paragraph boundaries in descriptions; source bytes stay elsewhere.
    value = re.sub(r"[^\S\n]+", " ", value.replace("\r\n", "\n").replace("\r", "\n"))
    value = "\n".join(line.strip() for line in value.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", value).strip()


def _numeric_hashtag_cluster(value, start, end, protected):
    """A literal numeric tag can belong to a neighboring hashtag-only cluster."""
    if re.match(r"\s*[/–-]\s*\d", value[end:]):
        return False  # A numbered reference such as #126 / 365 remains prose.
    before = re.search(r"[#＃](\w+)\s+$", value[:start])
    after = re.match(r"\s+[#＃](\w+)", value[end:])
    for match, offset in ((before,0),(after,end)):
        if not match:
            continue
        marker_start = offset + match.start() if match is before else offset + match[0].index("＃" if "＃" in match[0] else "#")
        if protected[marker_start]:
            continue
        if any(unicodedata.category(char).startswith("L") for char in match[1]):
            return True
    return False


def _split_tokens(value, numeric_hashtags=frozenset()):
    """Remove evidenced tokens; numeric tags require native hashtag evidence."""
    # Decode display prose only. Query strings/signatures retain their source bytes.
    pieces, cursor = [], 0
    for match in LINK_RE.finditer(value):
        pieces.extend((html.unescape(value[cursor:match.start()]), match[0]))
        cursor = match.end()
    pieces.append(html.unescape(value[cursor:]))
    value = "".join(pieces)
    spans, links, hashtags, mentions = [], [], [], []
    for match in LINK_RE.finditer(value):
        url = match[0].rstrip(".,;!?:\u3002\uFF01\uFF1F")
        while url and url[-1] in ")]}" and url.count(url[-1]) > url.count({")":"(","]":"[","}":"{"}[url[-1]]):
            url = url[:-1]
        if url:
            links.append(url)
            spans.append((match.start(), match.start()+len(url)))
    protected = [False]*len(value)
    for start,end in spans:
        protected[start:end] = [True]*(end-start)
    i = 0
    while i < len(value):
        marker = value[i]
        if protected[i] or marker not in "#＃@":
            i += 1
            continue
        previous = value[i-1] if i else ""
        preceding_token = re.search(r"\S+$",value[:i])
        prefix = preceding_token[0] if preceding_token else ""
        bad_boundary = (marker == "@" and (_word(previous) or previous in "/#＃@.+-%")) or (
            marker in "#＃" and (previous in "/#＃@.+-%" or
            (_word(previous) and ("." in prefix or "/" in prefix or _key(prefix) == "c"))))
        if i and bad_boundary:
            i += 1
            continue
        end = i+1
        while end < len(value) and (_word(value[end]) or (marker == "@" and value[end] == ".")):
            end += 1
        if marker == "@":
            while end > i+1 and value[end-1] == ".":
                end -= 1
        body = value[i+1:end]
        has_letter = any(unicodedata.category(c).startswith("L") for c in body)
        # Numeric vehicle hashtags such as #5008 are valid when a native hashtag
        # field attests them. Untyped references (#126 / 365), addresses and
        # underscore-only strings must not become inferred hashtags.
        valid = bool(body) and (marker == "@" or has_letter or
            (body.isdecimal() and (_key(body) in numeric_hashtags or
                _numeric_hashtag_cluster(value,i,end,protected))))
        if valid:
            (mentions if marker == "@" else hashtags).append(value[i:end])
            spans.append((i,end))
        i = max(i+1,end)
    chars = list(value)
    for start,end in spans:
        chars[start:end] = " "*(end-start)
    return _clean_spacing("".join(chars)), {"hashtags":hashtags,"mentions":mentions,"links":links}


def _short_sentence(text):
    """Find the first terminated sentence without splitting decimals or ellipses."""
    compact = re.sub(r"\s+", " ", text).strip()
    for match in re.finditer(r"[.!?。！？؟]", compact):
        i = match.start()
        char = compact[i]
        if char == ".":
            if (i and compact[i-1] == ".") or (i+1 < len(compact) and compact[i+1] == "."):
                continue
            if i and i+1 < len(compact) and compact[i-1].isdigit() and compact[i+1].isdigit():
                continue
            prefix = compact[:i]
            word = re.search(r"([\w.]+)$",prefix)
            if word and (_key(word[1]) in ABBREVIATIONS or re.fullmatch(r"\d+",prefix)):
                continue
        tail = compact[i+1:]
        closing = re.match(r"[\"'’”\)\]]*",tail)[0]
        end = i+1+len(closing)
        if char not in "。！？؟" and end < len(compact) and not compact[end].isspace():
            continue
        candidate = compact[:end]
        if len(candidate) > MAX_EXTRACTED_TITLE or "…" in candidate or "..." in candidate:
            return ""
        if any(unicodedata.category(c).startswith("L") for c in candidate):
            return candidate
    return ""


def _caption_title(text):
    first_line = text.split("\n",1)[0].strip()
    heading = re.match(r"^#{1,6}\s+(.+?)(?:\s+#+)?$", first_line)
    if not heading:
        # An initial bold heading may be preceded by decorative symbols/emoji.
        heading = re.match(r"^[^\w*#]*\*\*(.+?)\*\*(?:\s|$)",first_line)
    if heading:
        candidate = heading[1].strip()
        if 0 < len(candidate) <= MAX_EXTRACTED_TITLE and not candidate.endswith(("...","…")):
            return candidate,"source_markdown_heading"
    sentence = _short_sentence(text)
    return (sentence,"source_first_complete_sentence") if sentence else ("","needs_title_review")


def _override(value):
    if value is None:
        return None
    if not isinstance(value,Mapping) or set(value)-{"title","basis"} or not isinstance(value.get("title"),str) or not isinstance(value.get("basis"),str):
        raise ValueError("title_override requires only title and basis strings")
    title,basis = value["title"].strip(),value["basis"].strip()
    if not title or not basis or "\n" in title or "\r" in title:
        raise ValueError("An editorial title must be nonempty, single-line and documented")
    return {"title":title,"basis":basis}


def normalize_social_metadata(record, title_override=None):
    """Return deterministic display metadata plus lossless original text evidence.

    Supports a direct metadata mapping or a catalogue row whose metadata_json is
    a serialized mapping. This function does not mutate either representation.
    Reapplying it to its own output is exactly idempotent.
    """
    if not isinstance(record,Mapping):
        raise TypeError("record must be a mapping")
    override = _override(title_override)
    if isinstance(record.get("normalization"),Mapping) and record["normalization"].get("module") == "social_metadata":
        result = copy.deepcopy(dict(record))
        if override:
            result["title"] = override["title"]
            result["needs_title_review"] = False
            result["field_provenance"]["title"] = {"field":"title_override.title","basis":"editorial_override",
                "editorial_basis":override["basis"]}
            result["normalization"]["title_override"] = override
        return result
    metadata = {}
    raw_json = record.get("metadata_json")
    invalid_metadata_json = False
    if isinstance(raw_json,str):
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed,dict): metadata = parsed
            else: invalid_metadata_json = True
        except (ValueError,TypeError):
            invalid_metadata_json = True
    elif isinstance(raw_json,Mapping):
        metadata = dict(raw_json)
    merged = {**metadata, **record}
    fields = {}
    for field in TEXT_FIELDS:
        if isinstance(merged.get(field),str):
            fields[field] = merged[field]
    original = {"record":{k:copy.deepcopy(record[k]) for k in (*TEXT_FIELDS,*CONTEXT_FIELDS) if k in record},
        "metadata":{k:copy.deepcopy(metadata[k]) for k in (*TEXT_FIELDS,*CONTEXT_FIELDS) if k in metadata}}
    if "metadata_json" in record:
        original["metadata_json"] = copy.deepcopy(raw_json)
    collection = merged.get("collection_provenance") or merged.get("_collection") or {}
    collection = collection if isinstance(collection,Mapping) else {}
    provenance = merged.get("provenance") or {}
    provenance = provenance if isinstance(provenance,Mapping) else {}
    scope = str(merged.get("verification_scope") or merged.get("verificationScope") or collection.get("evidence_scope") or "unknown")
    indexed = ("index" in scope or scope == "public_search_metadata" or
        collection.get("provider") == "exa-public-mcp" or provenance.get("adapter") == "exa-public-mcp")
    description_basis = str(merged.get("description_basis") or "")
    # This known legacy field is an authored summary, not a pasted index body.
    editorial_description = (description_basis in {"public_title_or_caption_only", "editorial_summary"}
        or merged.get("descriptionType") == "editorial_summary"
        or merged.get("description_type") == "editorial_summary")
    caption_field = next((key for key in ("source_caption","caption","text","desc","sourceDescription","description") if fields.get(key)),None)
    caption = fields.get(caption_field,"")
    # A separate direct caption remains token/title evidence while an authored
    # description stays the displayed description. Never use an index body here.
    distinct_caption = caption if editorial_description and not indexed and caption_field != "description" else ""
    distinct_caption_field = caption_field if distinct_caption else None
    if indexed and not editorial_description:
        caption,caption_field = "",None
    elif editorial_description:
        caption,caption_field = fields.get("description",""),"description"
    raw_title = fields.get("title","")
    title_field = "title" if raw_title else None
    title_from_caption = bool(not raw_title or
        "caption" in str(provenance.get("title_basis", "")) or
        "caption" in str(collection.get("title_basis", "")) or
        "caption" in str(merged.get("title_basis", "")) or
        (isinstance(provenance.get("mapped_fields"),Mapping) and
         provenance["mapped_fields"].get("title") in {"caption","text","desc","description","source_caption"}))
    if indexed:
        # A distinct indexed title is retained; its unrelated body never supplies tokens.
        title_from_caption = not bool(raw_title)
    elif title_from_caption and (distinct_caption or (caption and not editorial_description)):
        # Prefer the available source caption to its clipped title derivative;
        # otherwise a title cut at '#Volks' could invent a second partial tag.
        raw_title,title_field = (distinct_caption,distinct_caption_field) if distinct_caption else (caption,caption_field)
    if not raw_title and caption and not editorial_description:
        raw_title,title_field = caption,caption_field
    supplied_hashtags = merged.get("hashtags")
    numeric_hashtags = {_key(value.lstrip("#＃")) for value in supplied_hashtags
        if isinstance(value,str) and value.lstrip("#＃").isdecimal()} if isinstance(supplied_hashtags,list) else set()
    title_clean,title_tokens = _split_tokens(raw_title,numeric_hashtags)
    description,description_tokens = _split_tokens(caption,numeric_hashtags)
    _,caption_tokens = _split_tokens(distinct_caption,numeric_hashtags)
    token_fields = list(dict.fromkeys(f for f in (title_field,caption_field,distinct_caption_field) if f))
    if title_from_caption:
        title,title_basis = _caption_title(title_clean)
        needs_review = not bool(title)
        if needs_review and title_clean:
            title = title_clean.split("\n",1)[0]
            title_basis = "source_text_pending_title_review"
    else:
        title,title_basis = title_clean,"source_native_title" if not indexed else "source_index_title"
        needs_review = not bool(title) or len(title)>MAX_EXTRACTED_TITLE or title.endswith(("...","…"))
    result = {"title":title,"description":description,
        **{kind:_dedupe(title_tokens[kind]+description_tokens[kind]+caption_tokens[kind],kind) for kind in ("hashtags","mentions","links")},
        "needs_title_review":needs_review,"source_metadata":original,
        "field_provenance":{
            "title":{"field":title_field,"basis":title_basis},
            "description":{"field":caption_field,"basis":"existing_editorial_description" if editorial_description else
                "indexed_body_excluded" if indexed else "source_caption_without_social_tokens"},
            "hashtags":{"fields":token_fields.copy(),"basis":"literal_source_tokens"},
            "mentions":{"fields":token_fields.copy(),"basis":"literal_source_tokens"},
            "links":{"fields":token_fields.copy(),"basis":"literal_source_urls"}},
        "normalization":{"module":"social_metadata","version":VERSION,"verification_scope":scope,
            "indexed_body_excluded":indexed and not editorial_description,
            "metadata_json_parse_failed":invalid_metadata_json,"title_override":None,
            "language_inferred":False,"media_reviewed":False}}
    # Portable callers may already have separated these tokens. Preserve only
    # well-formed explicit values, independently of display text, with provenance.
    for kind in ("hashtags", "mentions", "links"):
        supplied = merged.get(kind)
        if not isinstance(supplied, list):
            continue
        accepted = []
        for value in supplied:
            if not isinstance(value,str) or not value:
                continue
            if kind == "hashtags" and value.isdecimal():
                value = "#" + value
            if kind == "links":
                valid = bool(LINK_RE.fullmatch(value))
            else:
                marker = "@" if kind == "mentions" else "#＃"
                body = value[1:]
                valid = (value[0] in marker and bool(body)
                    and all(_word(c) or (kind == "mentions" and c == ".") for c in body)
                    and (any(unicodedata.category(c).startswith("L") for c in body)
                        or (kind == "hashtags" and body.isdecimal())))
            if valid:
                accepted.append(value)
        result[kind] = _dedupe(result[kind]+accepted,kind)
        result["field_provenance"][kind]["fields"].append(kind)
    if override:
        result["title"],result["needs_title_review"] = override["title"],False
        result["field_provenance"]["title"] = {"field":"title_override.title","basis":"editorial_override","editorial_basis":override["basis"]}
        result["normalization"]["title_override"] = override
    return result
