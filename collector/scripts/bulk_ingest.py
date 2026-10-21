#!/usr/bin/env python3
"""Bounded metadata ingestion. Preparation and application are dry-run by default.

Only fetch-apify performs network I/O: GET an existing dataset; never run an Actor.
No captions/transcripts/media are downloaded or granted reuse rights by this tool.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from server import (DEFAULT_DB, ValidationError, canonical_url, folded, import_items,
                    language_confidence, normalize_item, utcnow, web_url)
from automotive import extract_automotive
from scripts.social_metadata import normalize_social_metadata

VERSION = "1.1.2"
MAX_INPUT_BYTES = 150 * 1024 * 1024
MAX_LINE_BYTES = 2 * 1024 * 1024
MAX_ITEMS = 100000
PROVIDERS = ("auto", "apify-tiktok", "apify-instagram", "yt-dlp", "yt-dlp-tiktok", "yt-dlp-instagram")
EDUCATION = re.compile(r"\b(?:how to|how (?:do|can|should) (?:i|you)|tutorial\w*|tuto\w*|"
    r"comment (?:faire|fonctionne\w*|lire|comprendre|choisir|reconnaitre|savoir|tester|utiliser|ajuster|personnaliser|remplir|redemarrer)|guide\w*|explai\w*|"
    r"expli\w*|learn\w*|apprendre|apprenez|comprendre|fonctionnement|conseils?|tips?|pas a pas|step by step|etape par etape|"
    r"is measured by|stands for|signifie|signification|"
    r"como|aprend\w*|explica\w*|anleitung|wechseln|reparieren|sostituire|trocar|"
    r"remplacer|changer|vidange|replace|replacement|repair|diagnos\w*|"
    r"reparer|regler|configurer|configure|calibrat\w*|installation|"
    r"controler|verifier|nettoyer|entretenir|purger|demonter|remonter|"
    r"nettoyage|entretien|reglage|remplacement|changement|reparation|purge|"
    r"demontage|remontage|verification|controle|astuces?|etapes? pour|que signifie\w*|"
    r"quel ordre|dans quel ordre|brancher|debrancher|installer|connecter|"
    r"maintenance|bleed|adjust|inspect|remove|install|connect|pair|pairing)\b")
CONTEXTUAL_LEARNING = re.compile(r"\b(?:ou trouver|ou se situ\w*|where to find|where is|"
    r"comment (?:passer|engager) (?:la )?marche arriere|"
    r"regarde[rz]? (?:cet |l['’]|le )?indicateur d['’]usure)\b")
SPECIFIC_VEHICLE_CONTEXT = re.compile(r"\b(?:obd(?:2|ii)?|pneumati\w*|frein\w*|brakes?|"
    r"boite manuelle|boite de vitesses|manual gearbox|reverse gear)\b")
PROMOTION = re.compile(r"\b(?:code promo|promo code|discount code|buy now|shop now|"
    r"achetez|soldes|giveaway|concours|unboxing|deballage|product launch|"
    r"lancement|sponsored|sponsorise|paid partnership|black friday|"
    r"limited offer|offre limitee|lien en bio|link in bio|code reduction|"
    r"partenariat remunere|partenariat commercial|publicite|affiliation|affiliate|ad|pub|"
    r"commande[rz] maintenant|shop my|tiktok shop|a vendre|for sale|"
    r"prix promo|offre speciale|compra ahora|codigo de descuento|enlace en bio|"
    r"book now|book your|dm for|devis gratuit|offres du moment|offres exclusives|"
    r"collaboration commerciale|reservez|portes ouvertes|"
    r"venez decouvrir|venez visiter|prenez rendez.vous|"
    r"comment (?:ev|link|info|guide|yes|start)\b|commentez (?:lien|info|oui|guide))\b")
REVIEW = re.compile(r"\b(?:review|comparatif|comparison|top \d+|setup tour|room tour|"
    r"visite de|my new|mon nouveau|reaction|highlights|best moments)\b")
RISK_REVIEW = re.compile(r"\b(?:street racing|course de rue|dpf delete|egr delete|"
    r"adblue off|supprimer (?:le )?(?:fap|airbag)|airbag bypass|"
    r"disable (?:the )?(?:airbag|abs)|haute tension|high voltage)\b")
MECHANICAL_COMPONENTS = (
    r"amortisseur\w*|shock absorbers?|struts?|rotules?|ball joints?|control arms?|"
    r"triangle de suspension|wheel bearings?|roulements? (?:de )?(?:roue|moyeu)|"
    r"courroie\w*|timing belt|timing chain|chaine de distribution|"
    r"filtre\w* (?:a |d'|de )?(?:air|habitacle|huile|carburant|essence|gazole)|"
    r"air filter|cabin filter|fuel filter|oil filter|"
    r"liquide (?:de )?(?:frein|refroidissement)|coolant|radiateur\w*|radiator|"
    r"pompe a eau|water pump|power steering|direction assistee|"
    r"cremaillere de direction|injecteur\w*|injector\w*|demarreur|starter motor|ignition coils?|bobines? d'allumage|"
    r"plaquette\w*|brake pads?|disque\w* de frein|etrier\w*|brake calipers?|"
    r"joint de culasse|head gasket|echappement|exhaust|fap|dpf|egr|"
    r"boite de vitesses|gearbox|transmission fluid|liquide de transmission|"
    r"essuie.glace\w*|lave.glace\w*|windscreen washer|windshield washer|"
    r"feu\w* arriere|feux arriere|phares?|headlights?|tail lights?|"
    r"parallelisme|wheel alignment|train avant|turbo|turbocharger|evap|purge valve|"
    r"station essence|station.service|faire le plein|tableau de bord|"
    r"voyants? (?:sur|du) (?:ton |votre |le )?tableau|dashboard lights?|"
    r"carplay|android auto|autoradio|pulseur|pusleur|fusibles?|climatisation|faisceau electrique|"
    r"redemarrer (?:votre |la |sa |une )?voiture"
)
CATEGORY_RULES = (
    ("simracing", r"\b(?:sim ?racing|iracing|assetto corsa|acc setup|force feedback|simucube|fanatec|thrustmaster)\b"),
    ("media", r"\b(?:photography|photographie|photographier|filming|filmer|video editing|montage video|photo shoot)\b"),
    ("career", r"\b(?:career|carriere|devenir mecanicien|become a mechanic|become a racing driver|devenir pilote|metier)\b"),
    ("business", r"\b(?:business|car dealership|car shop|ouvrir un garage|sponsorship|sponsoring|patrocinio)\b"),
    ("engineering", r"\b(?:telemetr\w*|aerodynam\w*|thermodynam\w*|vehicle dynamics)\b"),
    ("driving", r"\b(?:trail braking|racing line|apex|understeer|oversteer|pilotage|"
     r"trajectoire|karting|racecraft|rally|trackday|motorsport|"
     r"(?:passer|engager) (?:la )?marche arriere|reverse gear)\b"),
    ("mechanics", r"\b(?:motor|moteur|engine|"
     r"vidange|oil change|essuie|wiper\w*|brake\w*|frein\w*|clio\d?|golf|peugeot|renault|"
     r"toyota|bmw|audi|diesel|obd(?:2|ii)?|batter\w*|embrayage|clutch|suspension|alternateur|"
     r"neumatic\w*|pneu\w*|tyre\w*|spark plug\w*|bougie\w*|carbur\w*|wheel\w*|" + MECHANICAL_COMPONENTS + r")\b"),
)
AUTO_CONTEXT = re.compile(r"\b(?:cars?|auto|automobiles?|vehicles?|vehicules?|voitures?|coche|garage|"
    r"mecanicien|mechanic|racing|motorsport|pilotage|pilote|karting|rally|circuit)\b")
AUTO_CONTEXT_TAGS = {"auto","automobile","voiture","mecaniqueauto","mecaniqueautomobile","garageautomobile"}
MECHANICAL_CONTEXT = re.compile(r"\b(?:moteur|engine|vidange|oil change|oil filter|essuie|wiper\w*|"
    r"brake\w*|frein\w*|clio\d?|golf|peugeot|renault|toyota|bmw|audi|diesel|obd(?:2|ii)?|"
    r"embrayage|clutch|alternateur|neumatic\w*|pneu\w*|tyre\w*|spark plug\w*|carbur\w*|" + MECHANICAL_COMPONENTS + r")\b")
NON_AUTO_CONTEXT = re.compile(r"\b(?:iphone|smartphone|laptop|ordinateur|smartwatch|washing machine|"
    r"machine a laver|vacuum cleaner|aspirateur|velo|bicycle|cycling|vtt|"
    r"mountain bike|road bike|e.bike|trottinette|scooter electrique|chauffage central|"
    r"syndrome de l.essuie.glace|syndrome (?:de la bandelette|ilio.tibial)|sbit|"
    r"radiateur de maison|home radiator|genou|knee|kitchen|cuisine|hotte|"
    r"extractor hood|cooker hood|range hood|avion|aircraft|airplane|aeroplane|"
    r"plane (?:tire|tyre|wheel)|boeing|airbus|helicopter|helicoptere|boat|bateau|yacht|"
    r"candles?|home decor|bougies? (?:parfumee\w*|decorative\w*)|machine (?:a )?cafe|"
    r"espresso machine|poussette|stroller|landau|martial arts|arts martiaux|karate|judo|"
    r"ballon (?:d'eau|sanitaire)|chauffe.eau|water heater|water tank)\b")
AMBIGUOUS_MECHANICAL_MATCH = re.compile(r"(?:amortisseur\w*|shock absorbers?|struts?|rotules?|"
    r"courroie\w*|filtre\w* (?:a |d'|de )?air|air filter|radiateur\w*|radiator|"
    r"pompe a eau|water pump|suspension|wheel\w*|turbo|fusibles?|climatisation|faisceau electrique)\Z")
FRENCH_GRAMMAR = set("le la les un une des du votre vos vous pour sur dans avec sans son sa ses et est pas il comment pourquoi quand".split())
FRENCH_CONTENT = set("comment pourquoi changer remplacer reparer regler controler verifier nettoyer entretenir purger demonter remonter apprendre apprenez conseils astuce astuces tuto tutoriel tutoriels voiture voitures moteur frein freins freinage vidange huile filtre habitacle essuie glaces pare brise amortisseur amortisseurs courroie distribution roue roues pneu pneus batterie bougie bougies embrayage liquide refroidissement direction demarreur alternateur suspension echappement boite vitesses panne diagnostic mecanique mecanicien pilotage trajectoire trajectoires volant pedale pedales embrayer debrayer accelerateur accelerer retrograder apprendre debutant debutants comprendre fonctionnement fusible fusibles ampoule ampoules reparation entretien nettoyage reglage votre vous".split())
FRENCH_GRAMMAR.update("que quel quelle quels quelles ton ta tes ces cet cette voici toutes tout tous aux au ou on de".split())
FRENCH_CONTENT.update("etape etapes voici brancher debrancher ordre signifie signifient voyant voyants tableau bord essence plein carburant station remplacement changement remontage demontage verification controle reparation reglage installer connecter autoradio ecran telephone aujourd".split())
DISTINCTIVE_FRENCH = set("vidange moteur essuie amortisseur amortisseurs courroie embrayage demarreur refroidissement echappement bougie bougies freinage voiture tutoriel tutoriels remplacement brancher debrancher signifie voyants phares reglage nettoyage reparer remplacer changer".split())
ENGLISH_GRAMMAR = set("the your how with from without why which this these".split())
SPANISH_CONTENT = set("como cambiar reemplazar aceite coche limpiaparabrisas freno frenos bateria bujia ruedas reparar".split())
# Actor-specific fields are mapped explicitly. Unlisted profile data, comments,
# cookies, credentials, subtitle text and CDN media URLs are never propagated.
SOURCE_PATHS = (
    "id", "aweme_id", "shortCode", "shortcode", "code", "url", "webVideoUrl", "webpage_url",
    "original_url", "title", "text", "desc", "caption", "description", "type", "productType",
    "isVideo", "is_video", "isPrivate", "is_private", "private", "availability", "isAd", "isSponsored",
    "isPaidPartnership", "paidPartnership", "hasTikTokShopProduct", "isSlideshow", "isPhoto", "isStory",
    "authorMeta.privateAccount", "authorMeta.name", "authorMeta.nickName", "author.uniqueId", "author.nickname",
    "author.unique_id", "ownerUsername", "ownerFullName", "owner.username", "owner.full_name",
    "channel", "uploader", "uploader_id", "videoMeta.duration", "videoDuration", "duration",
    "language", "textLanguage", "descLanguage", "captionLanguage", "defaultAudioLanguage",
    "defaultLanguage", "videoMeta.language", "language_status",
    "createTimeISO", "createTime", "timestamp", "upload_date", "published_at", "extractor_key", "ie_key", "_type",
    "displayUrl", "videoMeta.coverUrl", "videoMeta.originalCoverUrl", "thumbnail",
)
THUMBNAIL_FIELDS = {"displayUrl", "videoMeta.coverUrl", "videoMeta.originalCoverUrl", "thumbnail"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def file_digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def at(row, path):
    value = row
    for key in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def pick(row, *paths):
    for path in paths:
        value = at(row, path)
        if isinstance(value, (str, int, float)) and not isinstance(value, bool) and str(value).strip():
            return str(value).strip(), path
    return "", ""


def short(value, limit):
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value or "")).strip()[:limit]


def source_prose(value):
    """Hashtags, handles and URLs do not establish a lesson or vehicle application."""
    text = re.sub(r"https?://\S+", " ", str(value or ""), flags=re.I)
    return re.sub(r"(?<!\w)[#@]\w+", " ", text)


def indexed_title(value, platform):
    instagram_wrapper = re.search(r"\|\s*Instagram\s*$", str(value or ""), flags=re.I)
    text = re.sub(r"\s*\|\s*(?:TikTok|Instagram)\s*$", "", str(value or ""), flags=re.I)
    # Instagram indexed titles often wrap the caption as "Creator | Caption | Instagram".
    # Keep the original index title in provenance; never manufacture a native caption.
    if platform == "instagram" and instagram_wrapper and "|" in text:
        left,right = text.split("|",1)
        if len(left.strip()) <= 100 and right.strip():
            text = right.strip()
    return text.strip()


def french_source_estimate(title, description, scope):
    fields = {"title": source_prose(title), "source_description": source_prose(description)}
    combined = folded(" ".join(fields.values()))
    words = set(re.findall(r"[a-z]+", combined))
    # Mixed language text remains unknown rather than promising French audio.
    if len(words & ENGLISH_GRAMMAR) >= 2 or (
            len(words & SPANISH_CONTENT) >= 2 and words & {"el", "los", "las", "para", "del"}):
        return None
    for name, value in fields.items():
        tokens = set(re.findall(r"[a-z]+", folded(value)))
        grammar, content = tokens & FRENCH_GRAMMAR, tokens & FRENCH_CONTENT
        if (len(tokens & DISTINCTIVE_FRENCH) >= 2 or
            (len(grammar | content) >= 4 and ((len(grammar) >= 2 and len(content) >= 2) or
                                              (len(grammar) >= 1 and len(content) >= 3) or
                                              (len(grammar) >= 3 and len(content) >= 1)))):
            return {"language": "fr",
                "status": "inferred_from_indexed_source_text" if scope == "indexed_search_metadata"
                          else "inferred_from_source_text",
                "evidence": {"basis": "conservative_french_source_text_rules", "field": name,
                    "excerpt": short(value, 300), "matched_terms": sorted(grammar | content),
                    "rules_version": VERSION, "scope": scope,
                    "audio_language_verified": False, "search_query_used": False}}
    return None


def image_metadata_url(value):
    """Validate a public image URL without fetching it or discarding CDN signatures."""
    try:
        url = web_url(value)
        if not url:
            return None
        # Authentication credentials are not thumbnails. CDN expiry/signature
        # parameters remain intact because removing them can break public images.
        if any(key.lower() in {"access_token", "api_key", "apikey", "authorization", "password"}
               for key in parse_qs(urlsplit(url).query)):
            return None
        return url
    except (ValidationError, ValueError, TypeError):
        return None


def publication_metadata(row):
    for field_name in ("createTimeISO", "published_at", "timestamp", "upload_date", "createTime"):
        value = at(row, field_name)
        if value is None or isinstance(value, bool):
            continue
        try:
            text = str(value).strip()
            if field_name == "upload_date" and re.fullmatch(r"\d{8}", text):
                return dt.datetime.strptime(text, "%Y%m%d").date().isoformat(), field_name
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
                return dt.date.fromisoformat(text).isoformat(), field_name
            if field_name in {"timestamp", "createTime"} and re.fullmatch(r"\d{9,10}(?:\.\d+)?", text):
                return dt.datetime.fromtimestamp(float(text), dt.timezone.utc).isoformat(timespec="seconds"), field_name
            parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
            # A timezone absent from the source is not silently manufactured.
            return parsed.isoformat(timespec="seconds"), field_name
        except (ValueError, OverflowError, OSError):
            continue
    return None, ""


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def project_source(row, depth=0):
    """Keep only fields used by mappings, including no raw video/audio URL."""
    if not isinstance(row, dict):
        return row
    if depth > 5:
        raise ValidationError("Nested source exceeds five levels")
    out = {}
    for path in SOURCE_PATHS:
        value = at(row, path)
        if value is None:
            continue
        if isinstance(value, str):
            value = short(value, 20000)
            if path in {"url", "webVideoUrl", "webpage_url", "original_url"}:
                parsed = urlsplit(value)
                # No input URL token/signature/query is persisted, except a YouTube ID.
                query = parse_qs(parsed.query)
                clean_query = urlencode({"v": query["v"][0]}) if query.get("v") else ""
                value = urlunsplit((parsed.scheme, parsed.hostname or "", parsed.path, clean_query, ""))
            elif path in THUMBNAIL_FIELDS:
                value = image_metadata_url(value)
                if not value:
                    continue
        elif not isinstance(value, (int, float, bool)):
            # Arbitrary nested language_evidence is not a trusted platform signal.
            continue
        dest = out
        parts = path.split(".")
        for part in parts[:-1]:
            dest = dest.setdefault(part, {})
        dest[parts[-1]] = value
    if row.get("videoUrl") or row.get("video_url"):
        out["isVideo"] = True
    if row.get("imagePost") or row.get("slideshowImageLinks"):
        out["isSlideshow"] = True
    if not out.get("thumbnail") and isinstance(row.get("thumbnails"), list):
        for entry in reversed(row["thumbnails"][-100:]):
            value = image_metadata_url(entry.get("url")) if isinstance(entry, dict) else None
            if value:
                out["thumbnail"] = value
                break
    for key in ("latestPosts", "latestIgtvVideos"):
        if isinstance(row.get(key), list):
            out[key] = [project_source(child, depth + 1) for child in row[key]]
    return out


def source_rows(path):
    path = Path(path)
    def expand(value, depth=0):
        if depth > 5:
            raise ValidationError("Nested export exceeds five levels")
        if isinstance(value, list):
            for child in value:
                yield from expand(child, depth + 1)
        elif isinstance(value, dict) and any(isinstance(value.get(k), list) for k in ("latestPosts", "latestIgtvVideos")):
            for key in ("latestPosts", "latestIgtvVideos"):
                for child in value.get(key, []) or []:
                    if isinstance(child, dict) and value.get("private") is True:
                        child = {**child, "isPrivate": True}
                    yield from expand(child, depth + 1)
        elif isinstance(value, dict) and any(isinstance(value.get(k), list) for k in ("entries", "items", "videos")):
            for key in ("entries", "items", "videos"):
                if isinstance(value.get(key), list):
                    yield from expand(value[key], depth + 1)
                    break
        else:
            yield value
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        with path.open("r", encoding="utf-8-sig") as stream:
            for number, line in enumerate(iter(lambda: stream.readline(MAX_LINE_BYTES + 1), ""), 1):
                if len(line.encode("utf-8")) > MAX_LINE_BYTES:
                    raise ValidationError(f"JSONL line {number} exceeds 2 MiB")
                if line.strip():
                    try:
                        yield from expand(json.loads(line))
                    except json.JSONDecodeError as exc:
                        raise ValidationError(f"Invalid JSON on line {number}") from exc
    else:
        if path.stat().st_size > MAX_INPUT_BYTES:
            raise ValidationError("JSON exceeds 150 MiB; use JSONL or bounded pages")
        yield from expand(json.loads(path.read_text(encoding="utf-8-sig")))


def identity(url):
    canonical, platform = canonical_url(url)
    parsed = urlsplit(canonical)
    if platform == "youtube":
        key = parse_qs(parsed.query)["v"][0]
    elif platform in {"instagram", "tiktok"}:
        key = parsed.path.rstrip("/").split("/")[-1]
    else:
        raise ValidationError("Only YouTube, TikTok and Instagram are supported")
    # TikTok ID is stable if the author changes their username; Instagram p/reel
    # aliases share the shortcode. Remove every tracking parameter.
    if platform != "youtube":
        canonical = urlunsplit(("https", parsed.netloc, parsed.path, "", ""))
    return f"{platform}:{key}", canonical, platform


def language_metadata(row, provider):
    paths = ("defaultAudioLanguage", "videoMeta.language", "language", "defaultLanguage",
             "textLanguage", "descLanguage", "captionLanguage")
    value, path = pick(row, *paths)
    tag = value.lower().replace("_", "-")
    if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", tag) or tag in {"und", "mul"}:
        return "und", "unknown", {"basis": "no_usable_language_field"}
    # yt-dlp's video language and explicit audio-language metadata are declarations.
    # Actor generic/text language fields are evidence about text, never verified audio.
    if path == "defaultAudioLanguage" or (provider.startswith("yt-dlp") and path == "language"):
        status, basis = "platform_metadata", "exported_video_language_field"
    else:
        status, basis = "inferred_from_exported_caption_language", "exported_text_language_field"
    if row.get("language_status") == "inferred_from_discovery_query":
        return "und", "unknown", {"basis": "query_language_ignored"}
    supplied_status = str(row.get("language_status") or "")
    if supplied_status.startswith("unknown"):
        return "und", "unknown", {"basis": "source_explicitly_has_no_language_evidence"}
    if supplied_status.startswith(("estimated", "inferred")):
        status, basis = "inferred_from_exported_caption_language", "exported_language_estimate_not_audio_declaration"
    return tag, status, {"basis": basis, "field": path, "value": value,
                         "audio_language_verified": False}


def educational_decision(title, description, row):
    text = folded(source_prose(title) + " " + source_prose(description))
    # Promotional hashtags remain exclusion signals, even though hashtags alone
    # cannot positively establish the lesson's topic or a vehicle application.
    promotion = PROMOTION.search(folded(title + " " + description))
    title_text = folded(source_prose(title))
    risk = RISK_REVIEW.search(text)
    edu = EDUCATION.search(text)
    if not edu and (AUTO_CONTEXT.search(text) or SPECIFIC_VEHICLE_CONTEXT.search(text) or
                    extract_automotive(source_prose(title))["vehicles"]):
        edu = CONTEXTUAL_LEARNING.search(text)
    phone_connection = bool(edu and re.search(r"\b(?:carplay|android auto|autoradio|infotainment)\b",text)
        and not re.search(r"(?:replace|repair|remplacer|reparer).{0,30}(?:iphone|smartphone)|(?:iphone|smartphone).{0,20}(?:battery|batterie)",text))
    out_of_scope = next((match for match in NON_AUTO_CONTEXT.finditer(text)
                         if not (phone_connection and match[0] in {"smartphone","iphone"})),None)
    category = next(((name, re.search(pattern, text)) for name, pattern in CATEGORY_RULES
                     if re.search(pattern, text)), None)
    context_tags = set(re.findall(r"#(\w+)",folded(title+" "+description))) & AUTO_CONTEXT_TAGS
    if category and category[0] in {"media", "business", "career"} and not AUTO_CONTEXT.search(text):
        category = None
    technical_pilotage = (category and category[0] == "driving" and category[1][0] == "pilotage" and
        (re.search(r"\bpilotage (?:pneumatique|du turbo|de la geometrie|des ailettes)\b",text) or
         (re.search(r"\b(?:turbo\w*|geometrie variable)\b",title_text) and
          not re.search(r"\b(?:racing line|racecraft|trajectoire|karting|rally|trackday|understeer|oversteer)\b",text))))
    if technical_pilotage:
        mechanical = re.search(r"\b(?:"+MECHANICAL_COMPONENTS+r")\b",text)
        if mechanical:
            category=("mechanics",mechanical)
    if category and category[0] == "mechanics" and (out_of_scope or not (
            AUTO_CONTEXT.search(text) or context_tags or MECHANICAL_CONTEXT.search(text) or extract_automotive(source_prose(title))["vehicles"])):
        category = None
    if category and category[0] == "mechanics" and AMBIGUOUS_MECHANICAL_MATCH.fullmatch(category[1][0]) and not (
            AUTO_CONTEXT.search(text) or context_tags or extract_automotive(source_prose(title))["vehicles"]):
        category = None
    procedural_question = bool(category and edu and re.search(r"\b(?:how to|how (?:do|can|should) (?:i|you)|comment)\b",title_text))
    review = next((match for match in REVIEW.finditer(title_text)
                   if not (match[0] in {"my new","mon nouveau"} and procedural_question)),None)
    reasons = []
    if out_of_scope:
        reasons.append("out_of_scope_source_context")
    if promotion or any(row.get(key) is True for key in ("isAd", "isSponsored", "isPaidPartnership", "paidPartnership", "hasTikTokShopProduct")):
        reasons.append("promotional_or_sponsored_metadata")
    if review:
        reasons.append("review_or_entertainment_requires_editorial_check")
    if risk:
        reasons.append("safety_sensitive_method_requires_editorial_check")
    if not edu:
        reasons.append("no_explicit_learning_signal")
    if not category:
        reasons.append("no_supported_automotive_or_motorsport_topic")
    evidence = {"learning_signal": edu[0] if edu else None,
                "topic_signal": category[1][0] if category else None,
                "promotion_signal": promotion[0] if promotion else None,
                "review_signal": review[0] if review else None,
                "safety_signal": risk[0] if risk else None,
                "broad_automotive_context_tags":sorted(context_tags),
                "out_of_scope_signal": out_of_scope[0] if out_of_scope else None}
    return {"status": "quarantine" if reasons else "candidate", "reasons": reasons,
            "rules_version": VERSION, "basis": "title_and_caption_rules_not_video_review", "evidence": evidence}, \
        (category[0] if category else "other")


def separate_social_display(record, source_fields, caption_field, detected_provider):
    """Project social display fields after qualification, retaining exact evidence.

    This deliberately does not reclassify the resource or infer its language.
    Exa bodies remain audit evidence only. Direct exported captions are identified
    as unverified exports unless the collector recorded direct public metadata.
    """
    if record["platform"] not in {"instagram", "tiktok", "facebook"}:
        return
    collection = record.get("collection_provenance", {})
    indexed = collection.get("provider") == "exa-public-mcp"
    scope = record["verification_scope"]
    editorial = (source_fields.get("description_basis") in {"public_title_or_caption_only", "editorial_summary"}
        or source_fields.get("descriptionType") == "editorial_summary"
        or source_fields.get("description_type") == "editorial_summary")
    excluded_body = {}
    if indexed:
        # The external collector archive already preserves these mixed bodies.
        # Do not import comments/recommendations from other posts into the DB,
        # even as nested audit metadata. Keep a fingerprint instead.
        excluded_body = {key:value for key,value in source_fields.items()
            if key in {"caption", "text", "desc", "sourceDescription", "source_caption"}
            or (key == "description" and not editorial)}
        source_fields = {key:value for key,value in source_fields.items() if key not in excluded_body}
    caption = source_fields.get(caption_field, "") if caption_field else ""
    if editorial and caption_field == "description":
        caption = ""
    direct_caption = bool(caption and not indexed and (scope == "public_video_metadata" or
        (not collection and detected_provider in {"apify-instagram", "apify-tiktok", "yt-dlp-instagram", "yt-dlp-tiktok"})))
    display_input = {**source_fields, "title":record["title"],
        "description":source_fields.get("description", "") if editorial else caption,
        "verification_scope":scope, "provenance":record["provenance"],
        "collection_provenance":collection}
    if caption and not indexed:
        display_input["source_caption"] = caption
    if editorial:
        display_input["description_basis"] = "editorial_summary"
    separated = normalize_social_metadata(display_input)
    if excluded_body:
        separated["normalization"]["excluded_index_body_sha256"] = digest(excluded_body)
        separated["normalization"]["excluded_index_body_fields"] = list(excluded_body)
    separated["source_metadata"]["import_source_fields"] = source_fields
    separated["original_title"] = source_fields.get("title") or source_fields.get(caption_field or "", "")
    separated["original_caption"] = caption if direct_caption else ""
    separated["original_caption_status"] = ("public_video_metadata" if scope == "public_video_metadata" else
        "exported_direct_caption_not_independently_verified") if direct_caption else "unavailable"
    separated["title_basis"] = "editorial_rewrite" if separated["normalization"]["title_override"] else "source_cleanup"
    # Keep a reviewable nonempty source title, even when it lacks a sentence end.
    title = separated["title"] or record["title"]
    if len(title) > 480:
        prefix = title[:480]
        title = prefix.rsplit(" ",1)[0] if " " in prefix else prefix
        separated["needs_title_review"] = True
        separated["normalization"]["display_title_limited"] = True
    record["title"] = title
    record["description"] = short(separated["description"],1200)
    if editorial:
        record["description_basis"] = source_fields.get("description_basis") or "editorial_summary"
    record["descriptionType"] = separated["field_provenance"]["description"]["basis"]
    original_tags = source_fields.get("tags", [])
    original_tags = original_tags if isinstance(original_tags,list) else []
    tags, added, omitted, seen = [], [], [], set()
    for value in original_tags:
        if not isinstance(value,str):
            raise ValidationError("Search tags must be strings")
        key = unicodedata.normalize("NFC",value).casefold()
        if key not in seen:
            seen.add(key)
            tags.append(value)
    for value in separated["hashtags"]:
        key = unicodedata.normalize("NFC",value).casefold()
        if key in seen:
            continue
        if len(tags) >= 100 or len(value) > 100:
            omitted.append(value)
            continue
        seen.add(key)
        tags.append(value)
        added.append(value)
    separated["original_search_tags"] = original_tags
    separated["added_search_hashtags"] = added
    separated["unindexed_hashtags"] = omitted
    record["tags"] = tags
    record["social_content"] = separated


def adapt(row, provider="auto", *, source_label="export", index=0):
    if not isinstance(row, dict):
        raise ValidationError("Source record is not an object")
    raw_hash = digest(row)
    # Capture only text/list fields; never copy comments, media URLs, credentials
    # or arbitrary metadata blobs into source evidence.
    source_fields = {key:value for key,value in row.items()
        if key in {"title", "description", "caption", "text", "desc", "sourceDescription", "source_caption",
                   "description_basis", "descriptionType", "description_type"} and isinstance(value,str)}
    for key in ("tags", "hashtags", "mentions", "links"):
        if isinstance(row.get(key),list):
            source_fields[key] = [value for value in row[key] if isinstance(value,str)]
    collection = row.get("_collection")
    if isinstance(collection, dict) and collection.get("provider") in {"yt-dlp", "exa-public-mcp"}:
        search_filters = collection.get("search_filters")
        collection = {key: short(value, 1500) if isinstance(value, str) else value
            for key, value in collection.items() if key in {"collector", "collector_version", "provider",
                "job_kind", "source", "collected_at", "extractor_version", "evidence_scope",
                "extractor_title", "title_basis",
                "authenticated", "media_downloaded", "audio_language_verified"}
            and (value is None or isinstance(value, (str, bool)))}
        if collection["provider"] == "exa-public-mcp" and isinstance(search_filters, dict):
            safe_filters = {}
            for key in ("include_domains", "include_text"):
                values = search_filters.get(key)
                if isinstance(values, list) and len(values) <= 5 and all(isinstance(v,str) and len(v) <= 100 for v in values):
                    safe_filters[key] = [short(v,100) for v in values]
            location = search_filters.get("user_location")
            if isinstance(location,str) and re.fullmatch(r"[A-Z]{2}|",location):
                safe_filters["user_location"] = location
            collection["search_filters"] = safe_filters
    else:
        collection = None
    if collection and collection["provider"] == "exa-public-mcp":
        # A search result is never promoted to direct-page metadata by its wrapper.
        collection["evidence_scope"] = "indexed_search_metadata"
    row = project_source(row)
    url, url_field = pick(row, "webVideoUrl", "webpage_url", "original_url", "url")
    detected_provider = provider
    if provider == "auto":
        hint = (url + " " + str(row.get("extractor_key", "")) + " " + str(row.get("ie_key", ""))).lower()
        detected_provider = "apify-tiktok" if "tiktok" in hint or "authorMeta" in row else \
            "apify-instagram" if "instagram" in hint or "shortCode" in row or "ownerUsername" in row else "yt-dlp"
        if collection and collection["provider"] == "yt-dlp" and detected_provider.startswith("apify-"):
            detected_provider = detected_provider.replace("apify-", "yt-dlp-")
    if not url or not url.startswith(("https://", "http://")):
        source_id, _ = pick(row, *(('shortCode', 'shortcode', 'code') if detected_provider.endswith('-instagram') else ('id', 'aweme_id')))
        if detected_provider == "yt-dlp" and re.fullmatch(r"[A-Za-z0-9_-]{11}", source_id):
            url, url_field = f"https://www.youtube.com/watch?v={source_id}", "id"
        elif detected_provider == "apify-tiktok":
            author, _ = pick(row, "authorMeta.name", "author.uniqueId", "author.unique_id")
            if re.fullmatch(r"\d{5,30}", source_id) and re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", author):
                url, url_field = f"https://www.tiktok.com/@{author}/video/{source_id}", "id+author"
        elif detected_provider == "apify-instagram" and re.fullmatch(r"[A-Za-z0-9_-]{5,100}", source_id):
            url, url_field = f"https://www.instagram.com/p/{source_id}/", "shortCode"
    identifier, url, platform = identity(url)
    expected = {"apify-tiktok": "tiktok", "apify-instagram": "instagram", "yt-dlp": "youtube",
                "yt-dlp-tiktok": "tiktok", "yt-dlp-instagram": "instagram"}[detected_provider]
    if platform != expected:
        raise ValidationError("Provider does not match canonical source platform")
    if any(row.get(k) is True for k in ("isPrivate", "is_private", "private")) or at(row, "authorMeta.privateAccount") is True or row.get("availability") in {"private", "premium_only", "subscriber_only", "needs_auth"}:
        raise ValidationError("Private or access-restricted record")
    media_type = str(row.get("type") or row.get("productType") or "").lower()
    video_signal = platform in {"youtube", "tiktok"} or \
        "/reel/" in url or "/reels/" in url or "/tv/" in url or \
        media_type in {"video", "reel", "reels", "clips", "igtv"} or row.get("isVideo") is True or row.get("is_video") is True
    if not video_signal or media_type in {"image", "photo", "sidecar", "carousel"} or any(row.get(k) is True for k in ("isSlideshow", "isPhoto", "isStory")):
        raise ValidationError("Not an evidenced video; images and mixed carousels are not imported")
    caption, caption_field = pick(row, "caption", "text", "desc", "description")
    title, title_field = pick(row, "title")
    if not title:
        title, title_field = caption, caption_field
    if not title:
        raise ValidationError("Missing source title or caption")
    original_title = title
    original_caption_length = len(caption)
    is_indexed = bool(collection and collection.get("evidence_scope") == "indexed_search_metadata")
    restored_title = False
    if is_indexed:
        title = indexed_title(title, platform)
        # Public index bodies observed in real probes contain mixed recommendations
        # and comments, sometimes before the target caption. Keep the original body
        # only in the collector's separate research evidence, never in the catalog.
        caption = ""
    elif (collection and collection.get("provider") == "yt-dlp" and
          collection.get("evidence_scope") == "public_video_metadata" and caption):
        # Some direct extractors cut titles near 75 characters. Restore only an
        # exact, substantial prefix with an explicit ellipsis from the same
        # source's first physical caption line; never from a search-index body.
        prefix = re.sub(r"(?:\.{3}|\u2026)$", "", title.strip()).rstrip()
        first_line = caption.split("\n",1)[0].rstrip("\r")
        if prefix != title.strip() and len(prefix) >= 30 and first_line.startswith(prefix) and len(first_line) > len(prefix):
            title, title_field, restored_title = first_line, caption_field, True
    title = short(title.splitlines()[0] if title.splitlines() else "", 480)
    if not title:
        raise ValidationError("Missing usable source title")
    description = short(caption, 1200)
    creator, creator_field = pick(row, "authorMeta.nickName", "authorMeta.name", "author.nickname", "author.uniqueId",
                                  "ownerFullName", "ownerUsername", "owner.full_name", "owner.username", "channel", "uploader")
    duration_value, _ = pick(row, "videoMeta.duration", "videoDuration", "duration")
    try:
        numeric = float(duration_value)
        duration = int(numeric) if math.isfinite(numeric) and 0 <= numeric <= 172800 else None
    except (ValueError, OverflowError):
        duration = None
    language, language_status, language_evidence = language_metadata(row, detected_provider)
    scope = collection.get("evidence_scope") if collection else "exported_metadata_not_independently_verified"
    if collection and collection["provider"] == "exa-public-mcp":
        language, language_status, language_evidence = "und", "unknown_audio_language", {
            "basis": "search_index_does_not_verify_audio_language"}
    if language == "und":
        estimate = french_source_estimate(title, "" if is_indexed else description, scope)
        if estimate:
            language, language_status, language_evidence = estimate["language"], estimate["status"], estimate["evidence"]
    thumbnail, thumbnail_field = pick(row, "displayUrl", "videoMeta.coverUrl", "videoMeta.originalCoverUrl", "thumbnail")
    published_at, date_field = publication_metadata(row)
    # Search excerpts can contain recommendations and comments from other videos.
    # They cannot establish a lesson or language absent from the indexed title.
    decision, category = educational_decision(title, "" if is_indexed else description, row)
    record = {"id": identifier, "url": url, "platform": platform, "title": title,
        "creator": short(creator, 300), "description": description, "sourceDescription": description,
        "description_basis": "indexed_title_only_no_verified_caption" if is_indexed else "source_caption_excerpt",
        "language": language, "language_status": language_status,
        "language_evidence": language_evidence, "audio_language_verified": False,
        "category_slug": category, "category_status": "inferred_from_title_and_caption_rules",
        "domain_scope": "automotive_adjacent" if category == "mechanics" else "motorsport",
        "level_slug": "unknown", "level_status": "unknown", "duration_seconds": duration,
        "thumbnail_url": thumbnail or None, "published_at": published_at,
        "publication_date_status": ("indexed_metadata_unverified" if is_indexed else "source_metadata") if published_at else "unknown",
        "thumbnail_status": ("indexed_metadata_unverified" if is_indexed else "source_metadata") if thumbnail else "unknown",
        "content_format": "tutorial_candidate" if decision["status"] == "candidate" else "unspecified",
        "content_format_status": "inferred_from_title_and_caption_rules", "license": "unknown",
        "transcript_status": "not_checked", "transcriptImported": False,
        "review_status": "candidate", "verification_scope": "exported_metadata_not_independently_verified",
        "source_url": url, "verified_at": None, "collected_at": utcnow(),
        "automotive": extract_automotive(source_prose(title)), "bulk_qualification": decision,
        "provenance": {"adapter": collection["provider"] if collection else detected_provider,
            "schema_adapter": detected_provider, "adapter_version": VERSION, "source": source_label,
            "record_index": index, "source_record_sha256": raw_hash,
            "mapped_fields": {"url": url_field, "title": title_field, "description": caption_field, "creator": creator_field,
                              "thumbnail": thumbnail_field, "published_at": date_field},
        "caption_truncated": len(caption) > 1200, "title_truncated": len(original_title) > len(title),
        **({"source_extractor_title":short(original_title,480),
            "title_basis":"exact_truncated_prefix_of_direct_caption_first_line",
            "title_restored_from_caption":True} if restored_title else {}),
        **({"source_index_title":short(original_title,480),"qualification_text":"indexed_title_only",
            "index_excerpt_omitted":original_caption_length > 0,
            "original_excerpt_characters":original_caption_length} if is_indexed else {})}}
    if collection:
        record["collection_provenance"] = collection
        scope = collection.get("evidence_scope")
        if scope in {"public_video_metadata", "public_listing_metadata", "indexed_search_metadata"}:
            record["verification_scope"] = scope
    separate_social_display(record, source_fields, caption_field, detected_provider)
    normalize_item(record)
    return record, decision


def existing_identities(db):
    if db is None:
        return {}
    path = Path(db).resolve()
    if not path.is_file():
        raise ValidationError("Comparison database does not exist; preparation will not create it")
    conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        result = {}
        for identifier, url in conn.execute("SELECT id,url FROM videos WHERE platform IN ('youtube','instagram','tiktok')"):
            key, _, _ = identity(url)
            if key in result:
                raise ValidationError("Database has duplicate media identities; reconcile separately")
            result[key] = {"id": identifier, "url": url}
        return result
    finally:
        conn.close()


def rejected_media_identity(row, provider):
    """Recover only a stable public identity so an explicit negative cannot hide."""
    if not isinstance(row,dict):
        return None
    url,_=pick(row,"webVideoUrl","webpage_url","original_url","url")
    if url:
        try:
            return identity(url)[0]
        except (ValidationError,ValueError,TypeError):
            return None
    shortcode,_=pick(row,"shortCode","shortcode","code")
    if re.fullmatch(r"[A-Za-z0-9_-]{5,100}",shortcode) and (
            provider.endswith("-instagram") or any(k in row for k in ("ownerUsername","shortCode","shortcode"))):
        return "instagram:"+shortcode
    source_id,_=pick(row,"id","aweme_id")
    if re.fullmatch(r"\d{5,30}",source_id) and (provider.endswith("-tiktok") or "authorMeta" in row):
        return "tiktok:"+source_id
    if re.fullmatch(r"[A-Za-z0-9_-]{11}",source_id) and provider in {"auto","yt-dlp"}:
        return "youtube:"+source_id
    return None


def prepare(paths, output, *, provider="auto", db=DEFAULT_DB, max_items=10000):
    if not 1 <= max_items <= MAX_ITEMS:
        raise ValidationError("max-items must be between 1 and 100000")
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValidationError("Use a new or empty preparation directory")
    files = []
    for path in map(Path, paths):
        if path.is_dir() and (path / "checkpoint.json").exists():
            state = json.loads((path / "checkpoint.json").read_text(encoding="utf-8"))
            if not state.get("bounded_complete") or not state.get("checked_at"):
                raise ValidationError("Fetched snapshot has not completed its bounded read and stability check")
            for page in state.get("pages", []):
                if not re.fullmatch(r"page-\d{9}\.json", page.get("file", "")) or \
                    file_digest(path / page["file"]) != page.get("sha256"):
                    raise ValidationError("Fetched page hash differs from checkpoint")
            if {p.name for p in path.glob("page-*.json")} != {p["file"] for p in state.get("pages", [])}:
                raise ValidationError("Fetched directory contains untracked pages")
        files.extend(sorted(path.glob("page-*.json")) if path.is_dir() else [path])
    if not files:
        raise ValidationError("No source files found")
    existing = existing_identities(db)
    grouped, quarantine, explicit_negatives, consumed, truncated = {}, [], {}, 0, False
    for path in files:
        for row in source_rows(path):
            if consumed == max_items:
                truncated = True
                break
            consumed += 1
            try:
                record, decision = adapt(row, provider, source_label=path.name, index=consumed)
                grouped.setdefault(record["id"], []).append((record, decision))
            except (ValidationError, ValueError, TypeError) as exc:
                rejected={"source": path.name, "record_index": consumed, "source_record_sha256": digest(row),
                    "reasons": [short(str(exc), 250)], "record": None}
                if str(exc) in {"Private or access-restricted record", "Not an evidenced video; images and mixed carousels are not imported"}:
                    identifier=rejected_media_identity(row,provider)
                    if identifier:
                        rejected["id"]=identifier
                        explicit_negatives.setdefault(identifier,[]).append(rejected)
                quarantine.append(rejected)
        if truncated:
            break
    accepted, duplicates = [], 0
    # Fold explicit negative variants into the same media identity instead of
    # reporting a private/non-video duplicate as a separate unrelated error.
    quarantine=[entry for entry in quarantine if entry.get("id") not in explicit_negatives]
    for identifier,rejections in explicit_negatives.items():
        if identifier not in grouped:
            duplicates += len(rejections)-1
            quarantine.append({"id":identifier,"record":None,
                "reasons":list(dict.fromkeys(reason for rejected in rejections for reason in rejected["reasons"])),
                "source_variants":rejections})
    for identifier, variants in grouped.items():
        duplicates += len(variants) - 1 + len(explicit_negatives.get(identifier,[]))
        languages = {r["language"].split("-")[0] for r, _ in variants if r["language_status"] == "platform_metadata"}
        direct_candidate = any(r["verification_scope"] == "public_video_metadata" and not decision["reasons"]
                               for r,decision in variants)
        indexed_candidate = any(r["verification_scope"] == "indexed_search_metadata" and not decision["reasons"]
                                for r,decision in variants)
        reasons, waived = [], []
        missing_evidence={"no_explicit_learning_signal","no_supported_automotive_or_motorsport_topic"}
        for variant,decision in variants:
            for reason in decision["reasons"]:
                if (direct_candidate or indexed_candidate) and variant["verification_scope"] == "indexed_search_metadata" and reason in missing_evidence:
                    waived.append({"reason":reason,"scope":"indexed_search_metadata",
                                   "source_record_sha256":variant["provenance"]["source_record_sha256"]})
                else:
                    reasons.append(reason)
        reasons.extend(reason for rejected in explicit_negatives.get(identifier,[]) for reason in rejected["reasons"])
        reasons=list(dict.fromkeys(reasons))
        if len(languages) > 1:
            reasons.append("conflicting_video_language_metadata")
        # Prefer usable declared language, then direct metadata over search-index
        # excerpts, then more complete source text; ties retain
        # source order. Any disqualifying variant quarantines the whole media identity.
        record = max((r for r, _ in variants), key=lambda r: (
            language_confidence(r["language"], r["language_status"]) == "platform_declared",
            {"public_video_metadata": 3, "public_listing_metadata": 2, "indexed_search_metadata": 1}.get(r["verification_scope"], 0),
            r["bulk_qualification"]["status"] == "candidate",
            len(r["description"])))
        record["bulk_sources"] = [{**r["provenance"], **({"collection": r["collection_provenance"]}
                                  if r.get("collection_provenance") else {})} for r, _ in variants]
        if identifier in explicit_negatives:
            record["bulk_rejected_variants"]=explicit_negatives[identifier]
        if waived:
            record["bulk_reconciliation"]={"basis":"qualified_direct_metadata_over_index_missing_evidence" if direct_candidate else "qualified_index_title_over_index_missing_evidence",
                "ignored_missing_evidence":waived,"explicit_negative_flags_preserved":True,
                "selected_scope":record["verification_scope"],"rules_version":VERSION}
        if reasons:
            quarantine.append({"id": identifier, "reasons": reasons, "record": record})
        else:
            accepted.append(record)
    output.mkdir(parents=True, exist_ok=True)
    atomic_json(output / "accepted.json", accepted)
    with (output / "quarantine.jsonl").open("w", encoding="utf-8") as stream:
        for entry in quarantine:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    prepared_hash = file_digest(output / "accepted.json")
    report = {"adapter_version": VERSION, "mode": "dry_run", "database_modified": False,
        "database_compared": db is not None,
        "created_at": utcnow(), "source_records": consumed, "accepted_candidates": len(accepted),
        "quarantined": len(quarantine), "duplicates_in_batch": duplicates, "truncated_at_bound": truncated,
        "existing_media_to_update": sum(r["id"] in existing for r in accepted) if db is not None else None,
        "new_media_candidates": sum(r["id"] not in existing for r in accepted) if db is not None else None,
        "accepted_sha256": prepared_hash, "quarantine_sha256": file_digest(output / "quarantine.jsonl"),
        "candidate_counts": {
            "platform": dict(Counter(r["platform"] for r in accepted)),
            "category": dict(Counter(r["category_slug"] for r in accepted)),
            "verification_scope": dict(Counter(r["verification_scope"] for r in accepted)),
            "language_status": dict(Counter(r["language_status"] for r in accepted)),
            "language": dict(Counter(r["language"].split("-")[0] for r in accepted))},
        "source_files": [{"name": p.name, "sha256": file_digest(p)} for p in files],
        "rules": {"version": VERSION, "languages": "Exported language fields or conservative French source-text estimate; never search-query language",
            "rights": "Unknown; no media or transcripts imported", "review": "Candidate metadata only; not editorial selection"}}
    atomic_json(output / "report.json", report)
    atomic_json(output / "approval.template.json", {"accepted_sha256": prepared_hash,
        "approved_ids": [], "reviewer": "", "reason": "", "note": "Fill only after editorial review and authorization."})
    return report


def apply_prepared(prepared, *, db, approval=None, execute=False):
    prepared = Path(prepared)
    records = json.loads((prepared / "accepted.json").read_text(encoding="utf-8"))
    report = json.loads((prepared / "report.json").read_text(encoding="utf-8"))
    checksum = file_digest(prepared / "accepted.json")
    if checksum != report.get("accepted_sha256"):
        raise ValidationError("Prepared data changed after preparation")
    if not isinstance(records, list) or len(records) > MAX_ITEMS:
        raise ValidationError("Invalid prepared records")
    ids = [r.get("id") for r in records]
    if len(set(ids)) != len(ids):
        raise ValidationError("Prepared records contain duplicate IDs")
    selected = records
    if approval:
        approved = json.loads(Path(approval).read_text(encoding="utf-8"))
        requested = approved.get("approved_ids")
        if approved.get("accepted_sha256") != checksum or not isinstance(requested, list) or \
            not all(isinstance(i, str) for i in requested) or len(set(requested)) != len(requested) or \
            not set(requested).issubset(ids) or not requested or not str(approved.get("reviewer") or "").strip() or \
            not str(approved.get("reason") or "").strip():
            raise ValidationError("Approval requires matching hash, explicit valid IDs, reviewer and reason")
        selected = [r for r in records if r["id"] in set(requested)]
    elif execute:
        raise ValidationError("Execution requires an explicit approval manifest")
    existing = existing_identities(db)
    mapped = []
    for record in selected:
        record = dict(record)
        stable_id, _, _ = identity(record["url"])
        if stable_id != record["id"] or record.get("bulk_qualification", {}).get("status") != "candidate":
            raise ValidationError("Prepared identity or candidate classification changed")
        normalize_item(record)
        if stable_id in existing:
            # import_items merges by existing URL and preserves stronger evidence.
            # Stable TikTok IDs also deduplicate a renamed author permalink here.
            record.update(existing[stable_id])
        mapped.append(record)
    result = {"mode": "execute" if execute else "dry_run", "selected": len(mapped), "database_modified": False,
              "new": sum(r["id"] not in existing for r in selected), "existing": sum(r["id"] in existing for r in selected)}
    if execute:
        if not mapped:
            raise ValidationError("No approved record")
        # All records are one strict transaction; do not initialize/migrate production.
        result["import"] = import_items(db, mapped, source=f"bulk:{checksum}", strict=True)
        result["database_modified"] = True
        atomic_json(prepared / f"applied-{time.time_ns()}.json", {**result, "applied_at": utcnow(),
            "approval_sha256": file_digest(approval), "accepted_sha256": checksum})
    return result


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ApifyReader:
    """GET-only transport with no token in URL, redirect, log or persisted state."""
    def __init__(self, token, interval=1.0, retries=3, opener=None, sleep=time.sleep):
        if not token or "\n" in token or "\r" in token:
            raise ValidationError("APIFY_TOKEN is absent or invalid")
        if not .2 <= interval <= 30 or not 0 <= retries <= 5:
            raise ValidationError("interval must be 0.2–30 seconds; retries 0–5")
        self.token, self.interval, self.retries = token, interval, retries
        self.opener, self.sleep = opener or build_opener(NoRedirect()), sleep

    def get(self, dataset, items=False, **params):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}(?:~[A-Za-z0-9_-]{1,100})?", dataset):
            raise ValidationError("Dataset ID or username~dataset-name required")
        url = f"https://api.apify.com/v2/datasets/{quote(dataset, safe='~')}" + ("/items" if items else "")
        if params:
            url += "?" + urlencode(params)
        request = Request(url, headers={"Authorization": f"Bearer {self.token}",
            "Accept": "application/json", "User-Agent": f"FocusAcademyMetadata/{VERSION}"}, method="GET")
        for attempt in range(self.retries + 1):
            self.sleep(self.interval)
            try:
                with self.opener.open(request, timeout=30) as response:
                    body = response.read(20 * 1024 * 1024 + 1)
                    if len(body) > 20 * 1024 * 1024:
                        raise ValidationError("Dataset page exceeds 20 MiB; lower page-size")
                    return json.loads(body.decode("utf-8"))
            except HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt == self.retries:
                    raise ValidationError(f"Apify HTTP {exc.code}; checkpoint retained") from None
                delay = 2 ** attempt
                retry_after = exc.headers.get("Retry-After", "") if exc.headers else ""
                if retry_after:
                    try:
                        delay = max(delay, float(retry_after))
                    except ValueError:
                        raise ValidationError("Server requests a dated retry; resume later") from None
                if not math.isfinite(delay) or delay > 30:
                    raise ValidationError("Server requests a long retry; resume later")
                self.sleep(delay)
            except (URLError, TimeoutError):
                if attempt == self.retries:
                    raise ValidationError("Apify network failure; checkpoint retained") from None
                self.sleep(2 ** attempt)
        raise AssertionError("unreachable")


def fetch_apify(dataset, output, *, reader, page_size=250, max_items=10000, max_pages=40, resume=False):
    if not 1 <= page_size <= 1000 or not 1 <= max_items <= MAX_ITEMS or not 1 <= max_pages <= 1000:
        raise ValidationError("Bound page-size to 1–1000, max-items to 1–100000, max-pages to 1–1000")
    output = Path(output)
    checkpoint = output / "checkpoint.json"
    if output.exists() and any(output.iterdir()) and not resume:
        raise ValidationError("Output exists; use --resume or a new directory")
    metadata = reader.get(dataset).get("data", {})
    if not isinstance(metadata.get("itemCount"), int) or not metadata.get("id") or not metadata.get("modifiedAt"):
        raise ValidationError("Dataset snapshot metadata is incomplete")
    snapshot = {k: metadata[k] for k in ("id", "itemCount", "modifiedAt")}
    output.mkdir(parents=True, exist_ok=True)
    if resume:
        state = json.loads(checkpoint.read_text(encoding="utf-8"))
        if state.get("dataset") != dataset or state.get("snapshot") != snapshot:
            raise ValidationError("Dataset changed since checkpoint; start a fresh snapshot")
        if state.get("max_items") != max_items:
            raise ValidationError("Resume must keep original max-items bound")
        next_offset = 0
        for page in state["pages"]:
            filename = page["file"]
            if not re.fullmatch(r"page-\d{9}\.json", filename) or file_digest(output / filename) != page["sha256"]:
                raise ValidationError("A checkpoint page is missing or changed")
            if page["offset"] != next_offset or not isinstance(page["count"], int) or not 1 <= page["count"] <= 1000:
                raise ValidationError("Checkpoint pagination is not contiguous")
            next_offset += page["count"]
        if state["next_offset"] != next_offset or next_offset > min(snapshot["itemCount"], max_items):
            raise ValidationError("Checkpoint offset is inconsistent")
        state.update(complete=False, bounded_complete=False)
    else:
        state = {"version": VERSION, "dataset": dataset, "snapshot": snapshot, "next_offset": 0,
                 "max_items": max_items, "pages": [], "complete": False, "actor_started": False}
        atomic_json(checkpoint, state)
    end = min(snapshot["itemCount"], max_items)
    for _ in range(max_pages):
        offset = state["next_offset"]
        if offset >= end:
            break
        limit = min(page_size, end - offset)
        # clean/skipEmpty must stay false: offset advances by source rows, including
        # empty rows, so filtered exports cannot silently skip or repeat a page.
        rows = reader.get(dataset, items=True, format="json", offset=offset, limit=limit,
                          clean="false", skipEmpty="false", skipHidden="true", desc="false")
        if not isinstance(rows, list) or len(rows) != limit:
            raise ValidationError("Unexpected page length; dataset may be changing. Checkpoint retained")
        filename = f"page-{offset:09d}.json"
        atomic_json(output / filename, [project_source(row) for row in rows])
        state["pages"].append({"file": filename, "offset": offset, "count": len(rows), "sha256": file_digest(output / filename)})
        state["next_offset"] += len(rows)
        atomic_json(checkpoint, state)
    latest = reader.get(dataset).get("data", {})
    if {k: latest.get(k) for k in snapshot} != snapshot:
        raise ValidationError("Dataset changed during read; do not prepare these pages as a frozen snapshot")
    state.update(complete=state["next_offset"] == snapshot["itemCount"],
                 bounded_complete=state["next_offset"] == end, checked_at=utcnow())
    atomic_json(checkpoint, state)
    return {k: state[k] for k in ("dataset", "next_offset", "complete", "bounded_complete", "actor_started")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="Review-only normalization; no network and no DB writes")
    prep.add_argument("paths", nargs="+", type=Path)
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--provider", choices=PROVIDERS, default="auto")
    prep.add_argument("--db", type=Path, default=DEFAULT_DB, help="Existing comparison DB, opened read-only")
    prep.add_argument("--without-db", action="store_true")
    prep.add_argument("--max-items", type=int, default=10000)
    apply = sub.add_parser("apply", help="Dry-run unless --execute AND an approval manifest are supplied")
    apply.add_argument("prepared", type=Path)
    apply.add_argument("--db", type=Path, required=True)
    apply.add_argument("--approval", type=Path)
    apply.add_argument("--execute", action="store_true")
    fetch = sub.add_parser("fetch-apify", help="GET an existing dataset only; uses APIFY_TOKEN environment variable")
    fetch.add_argument("dataset")
    fetch.add_argument("--output", type=Path, required=True)
    fetch.add_argument("--page-size", type=int, default=250)
    fetch.add_argument("--max-items", type=int, default=10000)
    fetch.add_argument("--max-pages", type=int, default=40)
    fetch.add_argument("--interval", type=float, default=1)
    fetch.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(args.paths, args.output, provider=args.provider,
                             db=None if args.without_db else args.db, max_items=args.max_items)
        elif args.command == "apply":
            result = apply_prepared(args.prepared, db=args.db, approval=args.approval, execute=args.execute)
        else:
            result = fetch_apify(args.dataset, args.output, reader=ApifyReader(os.environ.get("APIFY_TOKEN"), args.interval),
                page_size=args.page_size, max_items=args.max_items, max_pages=args.max_pages, resume=args.resume)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (ValidationError, OSError, json.JSONDecodeError, sqlite3.Error) as exc:
        # Transport messages are deliberately sanitized; never print response bodies or headers.
        print(json.dumps({"error": short(str(exc), 300)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
