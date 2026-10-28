#!/usr/bin/env python3
"""Focus Académie: local, dependency-free metadata catalog and search API."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import ipaddress
import json
import mimetypes
import re
import sqlite3
import sys
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, unquote, urlsplit, urlunsplit

BASE = Path(__file__).resolve().parent
DEFAULT_DB = BASE / "data" / "catalog.sqlite3"
PUBLIC = BASE / "public"
CATEGORY_LABELS = {
    "driving": "Pilotage", "engineering": "Ingénierie", "mechanics": "Mécanique",
    "simracing": "Sim Racing", "media": "Média", "business": "Business",
    "career": "Carrière", "fitness": "Physique", "other": "Autres",
}
LEVEL_LABELS = {
    "beginner": "Débutant", "intermediate": "Intermédiaire",
    "advanced": "Avancé", "all": "Tous niveaux", "unknown": "À qualifier",
}
PLATFORMS = {"youtube", "vimeo", "dailymotion", "tiktok", "instagram", "facebook", "twitch", "other"}
LICENSES = {"unknown", "standard", "creative-commons", "public-domain", "permission"}
TRANSCRIPT_BASES = {"creative-commons", "public-domain", "creator-permission", "user-owned"}
MAX_JSON = 150 * 1024 * 1024
MAX_TRANSCRIPT = 5 * 1024 * 1024
VEHICLE_FIELDS = ("make", "model", "generation", "engine", "body_type", "fuel_type")
VEHICLE_FILTERS = VEHICLE_FIELDS + ("year",)
UNKNOWN_VALUES = {"", "unknown", "inconnu", "inconnue", "n/a", "non precise", "unspecified"}
CONTENT_FORMATS = {
    "tutorial": "tutorial", "tutorial_candidate": "tutorial",
    "demonstration": "demonstration", "telemetry_demonstration": "demonstration",
    "course": "course", "course_candidate": "course", "lecture": "course",
    "stream": "stream", "training_stream_candidate": "stream", "unspecified": "unspecified",
}
QUESTION_STOPWORDS = set("""
comment pourquoi quand quelle quelles quels quel est sont je tu on nous vous il elle ils elles
le la les un une des de du d l a au aux en et ou pour par avec sans dans sur que qui ce cet cette
how why when what which can could do does did i you we they the a an to of for with without
in on and is are my your
como por que cuando cual cuales puedo podemos el la los las un una de del al en con sin para
""".split())
GENERIC_CONTEXT = {"roue", "roues", "wheel", "wheels", "voiture", "voitures", "car", "cars",
                   "coche", "coches", "rueda", "ruedas"}
TOPIC_TERMS = {
    "braking": ({"frein", "freins", "freiner", "freinage", "brake", "brakes", "braking",
                 "frenar", "frenado", "frenada"}, ['"frein"*', '"brak"*', '"fren"*']),
    "locking": ({"bloquer", "blocage", "bloque", "bloquage", "lock", "locking", "lockup",
                 "bloquear", "bloqueo"}, ['"bloqu"*', '"blocage"', '"lock"*']),
    "telemetry": ({"telemetrie", "telemetry", "telemetria"}, ['"telemetr"*']),
    "setup": ({"reglage", "reglages", "regler", "setup", "setups", "tuning", "ajuste",
               "ajustes", "configurar"}, ['"regl"*', '"setup"*', '"tuning"', '"ajust"*']),
    "tyres": ({"pneu", "pneus", "pneumatiques", "tyre", "tyres", "tire", "tires",
               "neumatico", "neumaticos"}, ['"pneu"*', '"tyre"*', '"tire"*', '"neumatic"*']),
    "sponsorship": ({"sponsor", "sponsors", "sponsoring", "sponsorship", "sponsorships",
                     "patrocinio"}, ['"sponsor"*', '"patrocini"*']),
    "oversteer": ({"survirage", "oversteer", "oversteering", "sobreviraje"},
                 ['"survir"*', '"oversteer"*', '"sobrevir"*']),
    "understeer": ({"sousvirage", "understeer", "understeering", "subviraje"},
                  ['"sous virage"', '"sousvir"*', '"understeer"*', '"subvir"*']),
    "trajectory": ({"trajectoire", "trajectoires", "trazada", "trazadas"},
                  ['"trajectoir"*', '"racing line"', '"trazad"*']),
}


class ValidationError(ValueError):
    pass


class ClosingConnection(sqlite3.Connection):
    """Commit/rollback and close: stdlib's context manager alone never closes."""
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def folded(value):
    return "".join(c for c in unicodedata.normalize("NFKD", str(value)).lower()
                   if not unicodedata.combining(c)).strip()


def connect(db_path=DEFAULT_DB):
    conn = sqlite3.connect(str(db_path), timeout=20, factory=ClosingConnection)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=20000")
    return conn


def initialize(db_path=DEFAULT_DB):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(videos)")}
        if columns and "domain_scope" not in columns:
            conn.execute("ALTER TABLE videos ADD COLUMN domain_scope TEXT NOT NULL DEFAULT 'motorsport'")
        if columns and "pedagogical_format" not in columns:
            conn.execute("ALTER TABLE videos ADD COLUMN pedagogical_format TEXT NOT NULL DEFAULT 'unspecified'")
            for raw, normalized in CONTENT_FORMATS.items():
                conn.execute("UPDATE videos SET pedagogical_format=? WHERE COALESCE("
                             "json_extract(metadata_json,'$.content_format'),"
                             "json_extract(metadata_json,'$.contentFormat'))=?", (normalized, raw))
        if columns and "source_questions_text" not in columns:
            conn.execute("ALTER TABLE videos ADD COLUMN source_questions_text TEXT NOT NULL DEFAULT ''")
        fts_columns = {row["name"] for row in conn.execute("PRAGMA table_info(videos_fts)")}
        rebuild = bool(fts_columns and "source_questions_text" not in fts_columns)
        for trigger in ("videos_ai", "videos_ad", "videos_au"):
            conn.execute(f"DROP TRIGGER IF EXISTS {trigger}")
        if rebuild:
            conn.execute("DROP TABLE videos_fts")
        conn.executescript((BASE / "schema.sql").read_text(encoding="utf-8"))
        if rebuild:
            conn.execute("INSERT INTO videos_fts(videos_fts) VALUES('rebuild')")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_domain ON videos(domain_scope)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_format ON videos(pedagogical_format)")
    return db_path


def web_url(value, *, required=False):
    if not value:
        if required:
            raise ValidationError("URL manquante")
        return None
    value = str(value).strip()
    if len(value) > 4096:
        raise ValidationError("URL trop longue")
    try:
        p = urlsplit(value)
        host = (p.hostname or "").lower()
        port = p.port
    except ValueError as exc:
        raise ValidationError("URL invalide") from exc
    if (p.scheme.lower() not in {"https", "http"} or not host
            or p.username or p.password or any(ord(c) < 32 for c in value)):
        raise ValidationError("Seules les URL publiques HTTP(S) sont admises")
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".localhost")):
        raise ValidationError("URL locale interdite")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if "." not in host:
            raise ValidationError("Nom de domaine public requis")
    else:
        if not address.is_global:
            raise ValidationError("Adresse réseau privée interdite")
    if port and port not in (80, 443):
        raise ValidationError("Port non standard interdit")
    return value


def canonical_url(value):
    value = web_url(value, required=True)
    p = urlsplit(value)
    host = p.hostname.lower().removeprefix("www.").removeprefix("m.")
    path = p.path.rstrip("/")
    query = parse_qs(p.query)
    if host in {"youtube.com", "youtu.be", "youtube-nocookie.com"}:
        video_id = query.get("v", [""])[0] if path == "/watch" else path.split("/")[-1]
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValidationError("URL YouTube directe avec identifiant vidéo requis")
        return f"https://www.youtube.com/watch?v={video_id}", "youtube"
    if host in {"dailymotion.com", "dai.ly"}:
        if host == "dailymotion.com" and not re.fullmatch(r"/(?:embed/)?video/[^/]+", path):
            raise ValidationError("URL Dailymotion directe requise")
        video_id = path.rsplit("/", 1)[-1].split("_", 1)[0]
        if not re.fullmatch(r"[A-Za-z0-9]+", video_id):
            raise ValidationError("Identifiant Dailymotion invalide")
        return f"https://www.dailymotion.com/video/{video_id}", "dailymotion"
    if host in {"vimeo.com", "player.vimeo.com"}:
        parts = [part for part in path.split("/") if part]
        ids = [part for part in parts if part.isdigit()]
        if not ids:
            raise ValidationError("URL Vimeo directe requise")
        # Preserve a private/unlisted hash: it can be needed to access the video.
        private_hash = query.get("h", [""])[0]
        if parts[-1] != ids[-1] and parts[-1].isalnum():
            private_hash = parts[-1]
        suffix = "?" + urlencode({"h": private_hash}) if private_hash else ""
        return f"https://vimeo.com/{ids[-1]}{suffix}", "vimeo"
    canonical_hosts = {
        "instagram.com": "instagram", "tiktok.com": "tiktok", "facebook.com": "facebook",
        "fb.watch": "facebook", "twitch.tv": "twitch", "clips.twitch.tv": "twitch",
    }
    platform = canonical_hosts.get(host, "other")
    if platform == "instagram":
        post = re.fullmatch(r"/(?:[A-Za-z0-9_.]+/)?(p|reel|reels|tv)/([A-Za-z0-9_-]+)", path)
        if not post:
            raise ValidationError("URL de publication Instagram directe requise")
        path = f"/{post[1]}/{post[2]}"
    if platform == "tiktok" and not re.fullmatch(r"/@[^/]+/video/\d+", path):
        raise ValidationError("URL de vidéo TikTok directe requise")
    if platform == "twitch" and not (
            (host == "clips.twitch.tv" and re.fullmatch(r"/[A-Za-z0-9_-]+", path))
            or re.fullmatch(r"/videos/\d+", path)
            or re.fullmatch(r"/[^/]+/clip/[A-Za-z0-9_-]+", path)):
        raise ValidationError("URL de vidéo ou clip Twitch directe requise")
    if platform == "facebook" and host != "fb.watch" and not (
            "/videos/" in path or re.fullmatch(r"/reel/\d+", path)
            or (path in {"/watch", "/video.php"} and query.get("v"))):
        raise ValidationError("URL de vidéo Facebook directe requise")
    clean_query = {k: v for k, v in query.items()
                   if not k.lower().startswith("utm_")
                   and k.lower() not in {"fbclid", "gclid", "igsh", "igshid", "si", "feature"}}
    canonical = urlunsplit(("https", host, path or "/", urlencode(clean_query, doseq=True), ""))
    return canonical, platform


def field(item, name, alias=None, default=None):
    return item.get(name, item.get(alias, default)) if alias else item.get(name, default)


def text_value(value, maximum=10000):
    if value is None:
        return ""
    value = str(value).strip()
    if len(value) > maximum:
        raise ValidationError(f"Texte supérieur à {maximum} caractères")
    return value


def media_identity(url):
    canonical, platform = canonical_url(url)
    parsed = urlsplit(canonical)
    if platform == "instagram":
        return platform, parsed.path.rstrip("/").split("/")[-1]
    if platform == "facebook" and parsed.hostname == "facebook.com":
        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if not video_id:
            match = re.search(r"/(?:videos/(?:[^/]+/)?|reel/)(\d+)/?$", parsed.path)
            video_id = match[1] if match else ""
        if video_id and video_id.isdigit():
            return platform, video_id
    return platform, canonical


def normalized_category(value):
    value = folded(value).replace("_", "-")
    aliases = {folded(v): k for k, v in CATEGORY_LABELS.items()}
    aliases.update({"sim-racing": "simracing", "sim racing": "simracing", "technique": "engineering"})
    return aliases.get(value, value) if value in CATEGORY_LABELS or value in aliases else "other"


def normalized_level(value):
    value = folded(value)
    aliases = {folded(v): k for k, v in LEVEL_LABELS.items()}
    aliases.update({"pro": "advanced", "expert": "advanced", "tous": "all"})
    return aliases.get(value, value) if value in LEVEL_LABELS or value in aliases else "unknown"


def spec_key(value):
    return re.sub(r"[^a-z0-9]", "", folded(value))


def normalize_automotive(value):
    if not isinstance(value, dict):
        raise ValidationError("automotive doit être un objet")
    result = {"vehicles": [], "tasks": [], "systems": [], "specifications": [],
              "status": "metadata_extraction"}
    vehicles = value.get("vehicles", [])
    if not isinstance(vehicles, list) or len(vehicles) > 200:
        raise ValidationError("Liste d'applications véhicule invalide")
    seen = set()
    for vehicle in vehicles:
        if not isinstance(vehicle, dict):
            raise ValidationError("Application véhicule invalide")
        item = {key: text_value(vehicle.get(key), 150) for key in VEHICLE_FIELDS}
        for key in VEHICLE_FIELDS:
            if folded(item[key]) in UNKNOWN_VALUES:
                item[key] = ""
        for key in ("year_from", "year_to"):
            year = vehicle.get(key)
            if year in {None, ""}:
                item[key] = None
            elif isinstance(year, bool) or not str(year).isdigit() or not 1886 <= int(year) <= 2100:
                raise ValidationError("Année véhicule invalide")
            else:
                item[key] = int(year)
        if item["year_from"] and item["year_to"] and item["year_from"] > item["year_to"]:
            raise ValidationError("Plage d'années inversée")
        item["evidence"] = text_value(vehicle.get("evidence"), 3000)
        item["status"] = vehicle.get("status", "title_mention")
        if (not isinstance(vehicle.get("evidence"), str) or not item["evidence"]
                or item["status"] not in {"title_mention", "caption_mention", "inferred_from_unambiguous_model"}):
            raise ValidationError("Mention véhicule exige une preuve textuelle explicite de titre ou de légende")
        if item["status"] == "inferred_from_unambiguous_model" and (
                item["make"] != "Renault" or item["model"] != "Clio" or not re.search(
                    r"(?<!\w)clio\s*(?:iii|iv|ii|v|i|[1-5])(?!\w|[.,]\d)", folded(item["evidence"]))):
            raise ValidationError("L'inférence de marque est limitée au modèle Clio avec génération explicite")
        identity = tuple(item[key] for key in VEHICLE_FIELDS + ("year_from", "year_to"))
        if identity not in seen and any(item[key] for key in VEHICLE_FIELDS):
            seen.add(identity)
            result["vehicles"].append(item)
    for field_name in ("tasks", "systems"):
        values = value.get(field_name, [])
        if not isinstance(values, list) or len(values) > 100:
            raise ValidationError(f"Liste {field_name} invalide")
        for entry in values:
            if not isinstance(entry, str) or not re.fullmatch(r"[a-z][a-z0-9_:-]{0,79}", entry):
                raise ValidationError(f"Identifiant {field_name} invalide")
        result[field_name] = list(dict.fromkeys(values))
    specifications = value.get("specifications", [])
    if not isinstance(specifications, list) or len(specifications) > 100:
        raise ValidationError("Liste de références techniques invalide")
    for specification in specifications:
        if not isinstance(specification, dict):
            raise ValidationError("Référence technique invalide")
        item = {key: text_value(specification.get(key), 3000 if key == "evidence" else 150)
                for key in ("kind", "value", "evidence")}
        item["status"] = specification.get("status", "title_mention")
        if not all(item.values()) or not spec_key(item["value"]) or item["status"] != "title_mention":
            raise ValidationError("Référence technique exige une valeur et une preuve de titre")
        result["specifications"].append(item)
    return result


def replace_automotive_index(conn, video_id, automotive):
    for table in ("video_vehicles", "video_tasks", "video_systems", "video_specifications"):
        conn.execute(f"DELETE FROM {table} WHERE video_id=?", (video_id,))
    for position, vehicle in enumerate(automotive["vehicles"]):
        columns = ["video_id", "position"]
        values = [video_id, position]
        for key in VEHICLE_FIELDS:
            columns.extend([key, key + "_key"])
            values.extend([vehicle[key], folded(vehicle[key])])
        columns.extend(["year_from", "year_to", "evidence", "status"])
        values.extend(vehicle[key] for key in ("year_from", "year_to", "evidence", "status"))
        conn.execute(f"INSERT INTO video_vehicles({','.join(columns)}) "
                     f"VALUES({','.join('?' for _ in columns)})", values)
    for field_name, table, column in (("tasks", "video_tasks", "task"), ("systems", "video_systems", "system")):
        conn.executemany(f"INSERT INTO {table}(video_id,{column}) VALUES(?,?)",
                         [(video_id, value) for value in automotive[field_name]])
    conn.executemany("INSERT INTO video_specifications(video_id,kind,value,value_key,evidence,status)"
                     " VALUES(?,?,?,?,?,?)",
                     [(video_id, item["kind"], item["value"], spec_key(item["value"]),
                       item["evidence"], item["status"]) for item in automotive["specifications"]])


def import_automotive_enrichment(db_path, entries):
    if isinstance(entries, dict) and isinstance(entries.get("videos"), dict):
        entries = entries["videos"]
    if not isinstance(entries, dict):
        raise ValidationError("Enrichissement attendu sous forme {video_id: automotive}")
    result = {"updated": 0, "missing": [], "rejected": []}
    with connect(db_path) as conn:
        for video_id, raw in entries.items():
            current = conn.execute("SELECT metadata_json FROM videos WHERE id=?", (video_id,)).fetchone()
            if current is None:
                result["missing"].append(video_id)
                continue
            try:
                automotive = normalize_automotive(raw)
            except (ValidationError, TypeError) as exc:
                result["rejected"].append({"id": video_id, "error": str(exc)})
                continue
            metadata = json.loads(current["metadata_json"])
            metadata["automotive"] = automotive
            conn.execute("UPDATE videos SET metadata_json=?,updated_at=? WHERE id=?",
                         (json.dumps(metadata, ensure_ascii=False), utcnow(), video_id))
            replace_automotive_index(conn, video_id, automotive)
            result["updated"] += 1
    return result


def normalize_source_questions(item):
    comments = item.get("comments") or {}
    raw = item.get("source_questions", comments.get("questions", []) if isinstance(comments, dict) else [])
    if not isinstance(raw, list) or len(raw) > 50:
        raise ValidationError("Questions sources invalides")
    questions = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValidationError("Chaque question source doit avoir une provenance")
        question = text_value(entry.get("question_fr") or entry.get("question"), 1000)
        if not question:
            continue
        questions.append({"question": question,
            "language": "fr" if entry.get("question_fr") else text_value(entry.get("language") or "und", 35),
            "excerpt": text_value(entry.get("excerpt"), 1000),
            "source_url": web_url(entry.get("source_url"), required=True),
            "retrieved_at": text_value(entry.get("retrieved_at"), 60),
            "status": "public_comment_sample", "answer_status": "not_verified"})
    return questions


def language_confidence(language, status):
    if language in {"und", "mul"} or status.startswith("unknown"):
        return "unknown"
    if status in {"platform_metadata", "platform_declared", "original_audio_metadata"}:
        return "platform_declared"
    if status in {"caption_track", "original_caption_track", "original_automatic_caption_track", "source_caption_metadata"}:
        return "source_caption_track"
    if status.startswith(("inferred", "estimated")):
        return "estimated"
    return "unknown"


def language_strength(language, status):
    confidence = language_confidence(language, status)
    return {"unknown": 0, "estimated": 1, "platform_declared": 2, "source_caption_track": 2}[confidence]


def normalize_item(item):
    if not isinstance(item, dict):
        raise ValidationError("Chaque entrée doit être un objet JSON")
    url, detected_platform = canonical_url(item.get("url"))
    title = text_value(item.get("title"), 500)
    if not title:
        raise ValidationError("Titre manquant")
    identifier = "v_" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    supplied_id = item.get("id")
    if supplied_id and re.fullmatch(r"[A-Za-z0-9_:-]{1,100}", str(supplied_id)):
        identifier = str(supplied_id)
    platform = detected_platform
    supplied_platform = folded(item.get("platform", ""))
    if detected_platform == "other" and supplied_platform in PLATFORMS:
        platform = supplied_platform
    language = str(item.get("language") or "und").lower().replace("_", "-")
    language_aliases = {
        "francais": "fr", "français": "fr", "french": "fr", "english": "en", "anglais": "en",
        "español": "es", "espagnol": "es", "spanish": "es", "deutsch": "de", "allemand": "de",
        "italiano": "it", "italien": "it", "português": "pt", "portugais": "pt",
        "japonais": "ja", "日本語": "ja", "arabe": "ar", "العربية": "ar",
        "n/a": "und", "unknown": "und", "multilingue": "mul",
    }
    language = language_aliases.get(language, language)
    if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", language):
        language = "und"
    language_tag = language
    language = language.split("-")[0]
    language_status = text_value(field(item, "language_status", "languageStatus", "unknown"), 60)
    discovery_language_hint = None
    if language_status == "inferred_from_discovery_query":
        discovery_language_hint = language
        language, language_status = "und", "unknown_query_only"
    duration = field(item, "duration_seconds", "durationSeconds")
    if duration is not None:
        if isinstance(duration, bool) or not str(duration).isdigit() or int(duration) > 172800:
            raise ValidationError("Durée invalide")
        duration = int(duration)
    license_value = str(item.get("license") or "unknown").lower()
    license_aliases = {"cc": "creative-commons", "cc-by": "creative-commons",
                       "public": "unknown", "free": "unknown", "libre": "unknown"}
    license_value = license_aliases.get(license_value, license_value)
    if license_value not in LICENSES:
        license_value = "unknown"
    license_url = web_url(field(item, "license_url", "licenseUrl"))
    if license_value in {"creative-commons", "public-domain", "permission"} and not license_url:
        raise ValidationError("Une licence libre ou autorisation exige une URL de preuve")
    tags = item.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 100:
        raise ValidationError("Les tags doivent être une liste de 100 éléments maximum")
    tags = [text_value(t, 100) for t in tags]
    domain_scope = field(item, "domain_scope", "domainScope", "motorsport")
    if domain_scope not in {"motorsport", "automotive_adjacent"}:
        raise ValidationError("domain_scope doit être motorsport ou automotive_adjacent")
    transcript = item.get("transcript")
    transcript_data = {
        "transcript_text": "", "transcript_language": None, "transcript_source_url": None,
        "transcript_permission_basis": None, "transcript_permission_reference": None,
    }
    transcript_metadata = None
    if transcript:
        if not isinstance(transcript, dict):
            raise ValidationError("La transcription doit inclure provenance et droits")
        transcript_text = text_value(transcript.get("text"), MAX_TRANSCRIPT)
        if not transcript_text:
            raise ValidationError("Transcription vide")
        basis = transcript.get("permission_basis")
        if basis not in TRANSCRIPT_BASES:
            raise ValidationError("Autorisation de réutiliser la transcription manquante")
        reference = text_value(transcript.get("permission_reference"), 4096)
        if not reference:
            raise ValidationError("Preuve ou référence de l'autorisation requise")
        transcript_data = {
            "transcript_text": transcript_text,
            "transcript_language": text_value(transcript.get("language") or language, 35),
            "transcript_source_url": web_url(transcript.get("source_url"), required=True),
            "transcript_permission_basis": basis,
            "transcript_permission_reference": reference,
        }
        segments = transcript.get("segments", transcript.get("cues", []))
        if not isinstance(segments, list) or len(segments) > 50000:
            raise ValidationError("Segments de transcription invalides")
        validated_segments = []
        for segment in segments:
            if not isinstance(segment, dict):
                raise ValidationError("Chaque segment doit contenir un horodatage et du texte")
            start = segment.get("start")
            if isinstance(start, bool) or not isinstance(start, (int, float)) or not 0 <= start <= 172800:
                raise ValidationError("Horodatage de transcription invalide")
            validated = {"start": start, "text": text_value(segment.get("text"), 10000)}
            if segment.get("end") is not None:
                end = segment["end"]
                if isinstance(end, bool) or not isinstance(end, (int, float)) or not start <= end <= 172800:
                    raise ValidationError("Fin de segment invalide")
                validated["end"] = end
            validated_segments.append(validated)
        transcript_metadata = {
            "segments": validated_segments,
            "kind": text_value(transcript.get("kind") or "source_unspecified", 100),
            "attribution": text_value(transcript.get("attribution"), 2000),
            "license_url": web_url(transcript.get("license_url")),
            "changes": text_value(transcript.get("changes"), 3000),
            "quality_status": text_value(transcript.get("quality_status"), 200),
            "source_vtt": text_value(transcript.get("source_vtt"), 500),
            "source_sha256": text_value(transcript.get("source_sha256"), 64),
        }
    metadata = {k: v for k, v in item.items() if k not in {"transcript", "_transcript_metadata"}}
    metadata.update(language=language, language_status=language_status)
    if language_tag != language and not discovery_language_hint:
        metadata["language_tag"] = language_tag
    if discovery_language_hint:
        metadata["discovery_language_hint"] = discovery_language_hint
        metadata["language_audit_note"] = "La langue de la requête ne prouve pas celle de la vidéo."
    source_questions = normalize_source_questions(item)
    metadata["source_questions"] = source_questions
    if "automotive" in item:
        metadata["automotive"] = normalize_automotive(item["automotive"])
    if transcript_metadata is not None:
        metadata["_transcript_metadata"] = transcript_metadata
    now = utcnow()
    normalized = {
        "id": identifier, "url": url, "title": title, "platform": platform,
        "creator": text_value(item.get("creator"), 300),
        "language": language,
        "category": normalized_category(field(item, "category_slug", "category", "other")),
        "domain_scope": domain_scope,
        "pedagogical_format": CONTENT_FORMATS.get(field(item, "content_format", "contentFormat"), "unspecified"),
        "level": normalized_level(field(item, "level_slug", "level", "all")),
        "description": text_value(item.get("description"), 20000),
        "duration_seconds": duration,
        "published_at": text_value(field(item, "published_at", "publishedAt"), 60) or None,
        "thumbnail_url": web_url(field(item, "thumbnail_url", "thumbnailUrl")),
        "tags": json.dumps(tags, ensure_ascii=False),
        "license": license_value, "license_url": license_url,
        "source_url": web_url(field(item, "source_url", "sourceUrl") or url, required=True),
        "verified_at": text_value(field(item, "verified_at", "verifiedAt"), 60) or None,
        "review_status": text_value(field(item, "review_status", "reviewStatus", "candidate"), 60),
        "verification_scope": text_value(field(item, "verification_scope", "verificationScope",
                                               "public_search_metadata"), 100),
        "language_status": language_status,
        "level_status": text_value(field(item, "level_status", "levelStatus", "estimated"), 60),
        "source_questions_text": "\n".join(q["question"] + " " + q["excerpt"] for q in source_questions),
        "metadata_json": json.dumps(metadata, ensure_ascii=False),
        "created_at": now, "updated_at": now,
        **transcript_data,
    }
    return normalized


def import_items(db_path, items, source="json", *, strict=False):
    if not isinstance(items, list):
        raise ValidationError("Le catalogue doit être une liste JSON ou un objet avec videos/items")
    started = utcnow()
    result = {"inserted": 0, "updated": 0, "rejected": 0, "errors": []}
    with connect(db_path) as conn:
        social_identities = {media_identity(existing["url"]): existing for existing in conn.execute(
            "SELECT * FROM videos WHERE platform IN ('facebook','instagram')")}
        for index, item in enumerate(items):
            try:
                row = normalize_item(item)
                existing = conn.execute("SELECT * FROM videos WHERE url=?", (row["url"],)).fetchone()
                identity = media_identity(row["url"]) if row["platform"] in {"facebook", "instagram"} else None
                if existing is None and identity in social_identities:
                    existing = social_identities[identity]
                    # Different permalink shapes can address the same public media.
                    row["url"] = existing["url"]
                if existing:
                    row["id"] = existing["id"]
                    old_metadata = json.loads(existing["metadata_json"])
                    new_metadata = json.loads(row["metadata_json"])
                    incoming_language = (row["language"], row["language_status"])
                    incoming_language_metadata = {key: new_metadata[key] for key in (
                        "language_evidence", "languageEvidence", "language_tag", "audio_language_verified",
                        "discovery_language_hint", "language_audit_note") if key in new_metadata}
                    review_ranks = {"candidate": 0, "editorial_selection": 1, "curated": 2,
                                    "approved": 3, "verified": 3}
                    scope_ranks = {"public_search_metadata": 0, "public_video_metadata": 1,
                                   "video_metadata_license_and_source_captions": 2,
                                   "editorial_review": 3, "video_review": 3, "content_review": 3}
                    old_rank = (review_ranks.get(existing["review_status"], 0),
                                scope_ranks.get(existing["verification_scope"], 0))
                    new_rank = (review_ranks.get(row["review_status"], 0),
                                scope_ranks.get(row["verification_scope"], 0))
                    if new_rank < old_rank:
                        incoming_transcript_metadata = new_metadata.get("_transcript_metadata")
                        incoming_automotive = new_metadata.get("automotive")
                        incoming_questions = new_metadata.get("source_questions", [])
                        new_metadata = dict(old_metadata)
                        new_metadata["_latest_discovery"] = {
                            "source_url": row["source_url"], "verified_at": row["verified_at"],
                            "verification_scope": row["verification_scope"],
                        }
                        if incoming_transcript_metadata is not None:
                            new_metadata["_transcript_metadata"] = incoming_transcript_metadata
                        if incoming_automotive is not None:
                            new_metadata["automotive"] = incoming_automotive
                        for key in row:
                            if key not in {"id", "url", "created_at", "updated_at", "metadata_json"} \
                                    and not key.startswith("transcript_"):
                                row[key] = existing[key]
                        if incoming_questions:
                            new_metadata["source_questions"] = incoming_questions
                            row["source_questions_text"] = "\n".join(
                                q["question"] + " " + q["excerpt"] for q in incoming_questions)
                    # Missing evidence in a later batch must not erase an established right.
                    if row["license"] == "unknown" and existing["license"] != "unknown":
                        row["license"] = existing["license"]
                        row["license_url"] = existing["license_url"]
                        new_metadata["license"] = existing["license"]
                        new_metadata["license_url"] = existing["license_url"]
                    for key in ("creator", "description", "duration_seconds", "published_at", "thumbnail_url"):
                        if row[key] in {None, ""} and existing[key] not in {None, ""}:
                            row[key] = existing[key]
                    # Metadata refresh never deletes an authorized transcript already imported.
                    if not item.get("transcript"):
                        for key in list(row):
                            if key.startswith("transcript_"):
                                row.pop(key)
                        if "_transcript_metadata" in old_metadata:
                            new_metadata["_transcript_metadata"] = old_metadata["_transcript_metadata"]
                    if "automotive" not in item and "automotive" in old_metadata:
                        new_metadata["automotive"] = old_metadata["automotive"]
                    if not item.get("content_format") and not item.get("contentFormat"):
                        for format_key in ("content_format", "contentFormat", "format_status"):
                            if format_key in old_metadata:
                                new_metadata[format_key] = old_metadata[format_key]
                        row["pedagogical_format"] = existing["pedagogical_format"]
                    if not row["source_questions_text"] and existing["source_questions_text"]:
                        row["source_questions_text"] = existing["source_questions_text"]
                        new_metadata["source_questions"] = old_metadata.get("source_questions", [])
                    old_language = (existing["language"], existing["language_status"])
                    if language_strength(*incoming_language) > language_strength(*old_language):
                        row["language"], row["language_status"] = incoming_language
                        for key in ("language_evidence", "languageEvidence", "language_tag", "audio_language_verified"):
                            new_metadata.pop(key, None)
                        new_metadata.update(incoming_language_metadata)
                    elif language_strength(*old_language) > language_strength(*incoming_language):
                        row["language"], row["language_status"] = old_language
                        for key in ("language_evidence", "languageEvidence", "language_tag", "audio_language_verified"):
                            new_metadata.pop(key, None)
                            if key in old_metadata:
                                new_metadata[key] = old_metadata[key]
                    new_metadata.update(language=row["language"], language_status=row["language_status"])
                    row["metadata_json"] = json.dumps(new_metadata, ensure_ascii=False)
                    updates = [k for k in row if k not in {"id", "created_at"}]
                    conn.execute(f"UPDATE videos SET {','.join(k + '=?' for k in updates)} WHERE id=?",
                                 [row[k] for k in updates] + [row["id"]])
                    result["updated"] += 1
                else:
                    columns = list(row)
                    conn.execute(f"INSERT INTO videos ({','.join(columns)}) VALUES "
                                 f"({','.join('?' for _ in columns)})", [row[k] for k in columns])
                    result["inserted"] += 1
                metadata = json.loads(row["metadata_json"])
                if "automotive" in metadata:
                    replace_automotive_index(conn, row["id"], metadata["automotive"])
                if identity is not None:
                    social_identities[identity] = conn.execute("SELECT * FROM videos WHERE id=?", (row["id"],)).fetchone()
            except (ValidationError, sqlite3.IntegrityError, TypeError, OverflowError) as exc:
                if strict:
                    raise ValidationError(f"Entrée {index}: {exc}") from exc
                result["rejected"] += 1
                result["errors"].append({"index": index, "error": str(exc)})
        conn.execute(
            "INSERT INTO import_runs(source,started_at,finished_at,inserted,updated,rejected,errors_json)"
            " VALUES(?,?,?,?,?,?,?)",
            (str(source), started, utcnow(), result["inserted"], result["updated"], result["rejected"],
             json.dumps(result["errors"], ensure_ascii=False)))
    return result


def import_json(db_path, path, *, strict=False):
    path = Path(path)
    if path.stat().st_size > MAX_JSON:
        raise ValidationError("Fichier JSON supérieur à 150 Mo")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        data = data.get("videos", data.get("items"))
    return import_items(db_path, data, str(path), strict=strict)


def parse_vtt_segments(content):
    """Preserve actual WebVTT timestamps; never invent positions."""
    content = content.lstrip("\ufeff").replace("\r\n", "\n")
    if not content.startswith("WEBVTT"):
        raise ValidationError("Fichier WEBVTT requis")
    blocks = re.split(r"\n\s*\n", content)
    segments = []
    for block in blocks[1:]:
        lines = block.splitlines()
        if not lines or lines[0].startswith(("NOTE", "STYLE", "REGION")):
            continue
        timing = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing is None:
            continue
        bounds = lines[timing].split("-->", 1)
        times = []
        for bound in bounds:
            stamp = bound.strip().split(" ", 1)[0]
            match = re.fullmatch(r"(?:(\d+):)?(\d{2}):(\d{2})[.,](\d{3})", stamp)
            if not match:
                raise ValidationError("Horodatage WebVTT invalide")
            hours, minutes, seconds, millis = [int(x or 0) for x in match.groups()]
            if minutes >= 60 or seconds >= 60:
                raise ValidationError("Horodatage WebVTT invalide")
            times.append(hours * 3600 + minutes * 60 + seconds + millis / 1000)
        value = re.sub(r"<[^>]*>", "", " ".join(lines[timing + 1:]))
        value = re.sub(r"\s+", " ", html.unescape(value)).strip()
        if value and (not segments or segments[-1]["text"] != value):
            segments.append({"start": times[0], "end": times[1], "text": value})
    if not segments:
        raise ValidationError("Aucun texte transcrit trouvé dans le VTT")
    return segments


def parse_vtt(content):
    return "\n".join(segment["text"] for segment in parse_vtt_segments(content))


def import_transcript(db_path, video_id, path, language, source_url, permission_basis, permission_reference):
    path = Path(path)
    if path.stat().st_size > MAX_TRANSCRIPT:
        raise ValidationError("Transcription supérieure à 5 Mo")
    with connect(db_path) as conn:
        video = conn.execute("SELECT * FROM videos WHERE id=?", (video_id,)).fetchone()
    if not video:
        raise ValidationError("Vidéo inconnue")
    item = json.loads(video["metadata_json"])
    item["id"] = video["id"]
    segments = parse_vtt_segments(path.read_text(encoding="utf-8-sig"))
    item["transcript"] = {
        "text": "\n".join(segment["text"] for segment in segments), "segments": segments,
        "language": language, "kind": "source_webvtt",
        "source_url": source_url, "permission_basis": permission_basis,
        "permission_reference": permission_reference,
    }
    return import_items(db_path, [item], f"vtt:{path}", strict=True)


def serialize_video(row, detail=False):
    value = dict(row)
    metadata = json.loads(value.pop("metadata_json", "{}"))
    value.pop("source_questions_text", None)
    value["source_questions"] = metadata.get("source_questions", [])
    value["language_confidence"] = language_confidence(value["language"], value["language_status"])
    value["language_tag"] = metadata.get("language_tag", value["language"])
    value["tags"] = json.loads(value.get("tags", "[]"))
    transcript_text = value.pop("transcript_text", "")
    transcript_source = value.pop("transcript_source_url", None)
    transcript_basis = value.pop("transcript_permission_basis", None)
    transcript_reference = value.pop("transcript_permission_reference", None)
    value["has_transcript"] = bool(transcript_text)
    value["transcript_status"] = "available" if transcript_text else "unavailable"
    value["category_label"] = CATEGORY_LABELS.get(value["category"], value["category"])
    value["level_label"] = LEVEL_LABELS.get(value["level"], value["level"])
    value["source_description"] = metadata.get("sourceDescription", "")
    if metadata.get("provider") == "peertube":
        value["source_provider"] = "peertube"
    social = metadata.get("social_content", {})
    if isinstance(social, dict) and social.get("normalization"):
        value["hashtags"] = social.get("hashtags", [])
        value["source_title"] = social.get("original_title", "")
        value["source_caption"] = social.get("original_caption", "")
        value["title_basis"] = social.get("title_basis", "source_cleanup")
    value["source_transcript_status"] = metadata.get("transcriptStatus", "unknown")
    value["source_captions_available"] = value["source_transcript_status"] == "source_captions_available"
    value["description_type"] = metadata.get("descriptionType", "source_metadata")
    if isinstance(social, dict) and social.get("normalization"):
        value["description_type"] = social.get("field_provenance", {}).get("description", {}).get("basis", value["description_type"])
    value["embed_status"] = metadata.get("embedStatus", "unknown")
    value["content_format"] = metadata.get("content_format", metadata.get("contentFormat", "unspecified"))
    value["contentFormat"] = value["content_format"]
    value["resource_type"] = "video"
    value["pedagogical_format"] = CONTENT_FORMATS.get(value["content_format"], "unspecified")
    value["format_status"] = metadata.get("format_status", "metadata_candidate"
        if value["pedagogical_format"] != "unspecified" else "not_classified")
    value["automotive"] = metadata.get("automotive", {
        "vehicles": [], "tasks": [], "systems": [], "specifications": [], "status": "not_extracted"})
    value["synopsis"] = metadata.get("synopsis", "")
    value["learning_outcomes"] = metadata.get("learning_outcomes", metadata.get("learningPoints", []))
    value["summary_basis"] = metadata.get("summary_basis", metadata.get("summaryBasis"))
    value["summary_language"] = metadata.get("summary_language", metadata.get("summaryLanguage"))
    value["summary_quality_note"] = metadata.get("summary_quality_note", metadata.get("summaryQualityNote"))
    value["learningPoints"] = value["learning_outcomes"]
    value["summaryBasis"] = value["summary_basis"]
    value["summaryLanguage"] = value["summary_language"]
    value["summaryQualityNote"] = value["summary_quality_note"]
    value["content_verified"] = (
        value.get("review_status") in {"verified", "curated", "approved"}
        and value.get("verification_scope") in {"editorial_review", "video_review", "content_review"})
    # Legacy camelCase aliases keep the static front end easy to integrate.
    value["durationSeconds"] = value.get("duration_seconds")
    value["thumbnailUrl"] = value.get("thumbnail_url")
    value["verifiedAt"] = value.get("verified_at")
    value["reviewStatus"] = value.get("review_status")
    value["languageStatus"] = value.get("language_status")
    value["levelStatus"] = value.get("level_status")
    value["transcriptStatus"] = value["transcript_status"]
    if detail:
        transcript_metadata = metadata.get("_transcript_metadata", {})
        value["transcript"] = ({
            "text": transcript_text, "language": value.get("transcript_language"),
            "source_url": transcript_source, "permission_basis": transcript_basis,
            "permission_reference": transcript_reference,
            "permission": f"{transcript_basis} · {transcript_reference}",
            "segments": transcript_metadata.get("segments", []),
            "kind": transcript_metadata.get("kind", "source_unspecified"),
            "attribution": transcript_metadata.get("attribution", ""),
            "license_url": transcript_metadata.get("license_url"),
            "changes": transcript_metadata.get("changes", ""),
            "quality_status": transcript_metadata.get("quality_status", ""),
            "source_vtt": transcript_metadata.get("source_vtt", ""),
            "source_sha256": transcript_metadata.get("source_sha256", ""),
        } if transcript_text else None)
    return value


def query_value(params, key, default=""):
    value = params.get(key, default)
    return str(value[0] if isinstance(value, list) and value else value)


def integer_param(params, key, default, minimum, maximum):
    value = query_value(params, key, str(default))
    if not re.fullmatch(r"\d{1,8}", value):
        raise ValidationError(f"Paramètre {key} invalide")
    number = int(value)
    if not minimum <= number <= maximum:
        raise ValidationError(f"{key} doit être compris entre {minimum} et {maximum}")
    return number


def educational_query_candidates(q, words):
    """Small transparent glossary, never an AI translation or a semantic guarantee."""
    tokens = [folded(word) for word in words]
    significant = [token for token in tokens if token not in QUESTION_STOPWORDS]
    groups, concepts, unknown = [], [], []
    for token in significant:
        if token in GENERIC_CONTEXT:
            continue
        match = next(((name, terms) for name, (aliases, terms) in TOPIC_TERMS.items()
                      if token in aliases), None)
        if match:
            name, terms = match
            if name not in concepts:
                concepts.append(name)
                groups.append("(" + " OR ".join(terms) + ")")
        else:
            unknown.append(token)
            groups.append('"' + token.replace('"', '""') + '"*')
    candidates = []
    if concepts and groups:
        candidates.append((" AND ".join(groups), "glossary", concepts))
    is_question = "?" in q or (tokens and tokens[0] in {
        "comment", "pourquoi", "how", "why", "como", "can", "could"})
    # An empty precise braking/locking answer can offer nearby braking tutorials.
    # Never discard a name, a car model, or another unknown specific term.
    if is_question and not unknown and set(concepts) == {"braking", "locking"}:
        broad = "(" + " OR ".join(TOPIC_TERMS["braking"][1]) + ")"
        candidates.append((broad, "related_topics", ["braking"]))
    return candidates


TASK_PHRASES = {
    "oil_change": ["vidange", "oil change", "change oil", "cambio de aceite", "cambiar aceite"],
    "oil_filter": ["filtre a huile", "oil filter", "filtro de aceite"],
    "cabin_filter": ["filtre habitacle", "filtre d habitacle", "filtre de cabine", "cabin filter", "pollen filter", "filtro habitaculo"],
    "air_filter": ["filtre a air", "air filter", "filtro de aire"],
    "fuel_filter": ["filtre a carburant", "filtre a gasoil", "fuel filter", "filtro de combustible"],
    "wipers": ["essuie glaces", "essuie glace", "wipers", "wiper", "limpiaparabrisas"],
    "wheel_change": ["changer une roue", "changer la roue", "changement de roue", "wheel change",
                     "change wheel", "cambiar rueda"],
    "key_battery": ["pile de cle", "pile cle", "pile de la cle", "pile de ma cle", "pile de carte",
                    "pile de la carte", "pile telecommande", "pile de telecommande",
                    "key battery", "key fob battery", "pila llave"],
    "battery": ["batterie", "battery", "bateria"],
    "brake_pads": ["plaquettes de frein", "plaquettes frein", "brake pads", "pastillas de freno"],
    "brake_discs": ["disques de frein", "disques frein", "brake discs", "brake rotors", "discos de freno"],
    "wheel_bearing": ["roulement de roue", "roulement roue", "wheel bearing", "rodamiento de rueda"],
    "spark_plugs": ["bougies d allumage", "bougies allumage", "spark plugs", "bujias"],
    "glow_plugs": ["bougies de prechauffage", "glow plugs"],
    "fuses": ["fusibles", "fusible", "fuses", "fuse"],
    "lighting": ["ampoule", "ampoules", "phare", "phares", "headlight", "bulb", "bombilla"],
    "diagnostics": ["diagnostic", "diagnostics", "obd", "code defaut"],
    "service_reset": ["service reset", "reset service", "remise a zero entretien", "reset entretien"],
    "oil_spec": ["quelle huile", "which oil", "oil viscosity", "viscosite huile", "que aceite"],
    "fuel_choice": ["quel carburant", "which fuel", "que combustible", "choix carburant"],
}
AUTOMOTIVE_STOPWORDS = QUESTION_STOPWORDS | set(
    "faire faireune changer change changing remplacer replace replacing mettre ajouter remplir trouver "
    "savoir comment tutorial tuto tutoriel guide video ma mon mes sa son ses voiture vehicule auto "
    "car vehicle coche mi su como hacer comment bien".split())
ROMAN_GENERATIONS = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
                     "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10"}


def phrase_pattern(value):
    words = re.findall(r"[^\W_]+", folded(value), re.UNICODE)
    return r"(?<!\w)" + r"[\W_]*".join(re.escape(word) for word in words) + r"(?!\w)"


def vehicle_filter_values(params):
    result = {}
    for key in VEHICLE_FILTERS:
        value = query_value(params, key).strip()
        if not value or value in {"all", "any", "*"}:
            continue
        if len(value) > 150:
            raise ValidationError(f"Filtre {key} trop long")
        if key == "year":
            if not re.fullmatch(r"\d{4}", value) or not 1886 <= int(value) <= 2100:
                raise ValidationError("Année véhicule invalide")
            result[key] = int(value)
        else:
            result[key] = value
    return result


def vehicle_conditions(filters, alias="vv"):
    conditions, values = [], []
    for key, value in filters.items():
        if key == "year":
            conditions.append(
                f"COALESCE({alias}.year_from,{alias}.year_to) <= ? AND "
                f"COALESCE({alias}.year_to,{alias}.year_from) >= ?")
            values.extend([value, value])
        else:
            conditions.append(f"{alias}.{key}_key=?")
            values.append(folded(value))
    return conditions, values


def vehicle_options(db_path, params):
    selected = vehicle_filter_values(params)
    options = {}
    with connect(db_path) as conn:
        full_conditions, full_args = vehicle_conditions(selected)
        full_where = " WHERE " + " AND ".join(full_conditions) if full_conditions else ""
        totals = conn.execute(
            "SELECT COUNT(*) matching_applications,COUNT(DISTINCT video_id) total_videos "
            "FROM video_vehicles vv" + full_where, full_args).fetchone()
        for key in VEHICLE_FILTERS:
            if key == "make":
                filters = {}
            elif key == "model":
                filters = {name: value for name, value in selected.items() if name == "make"}
            elif key == "generation":
                filters = {name: value for name, value in selected.items() if name in {"make", "model"}}
            else:
                filters = {name: value for name, value in selected.items() if name != key}
            conditions, args = vehicle_conditions(filters)
            if key != "year":
                conditions.append(f"vv.{key}_key<>''")
                where = " WHERE " + " AND ".join(conditions)
                rows = conn.execute(f"SELECT MIN(vv.{key}) AS value,COUNT(DISTINCT video_id) AS count "
                                    "FROM video_vehicles vv" + where +
                                    f" GROUP BY vv.{key}_key ORDER BY value COLLATE NOCASE", args).fetchall()
                options[key] = [dict(row) for row in rows]
            else:
                where = " WHERE " + " AND ".join(conditions) if conditions else ""
                counts = {}
                for row in conn.execute("SELECT video_id,year_from,year_to FROM video_vehicles vv" + where, args):
                    low, high = row["year_from"] or row["year_to"], row["year_to"] or row["year_from"]
                    if low is not None:
                        for year in range(low, high + 1):
                            counts.setdefault(year, set()).add(row["video_id"])
                options[key] = [{"value": str(year), "count": len(counts[year])} for year in sorted(counts)]
    return {"options": options, "facets": options, **dict(totals), "selected": selected,
            "evidence_scope": "title_or_caption_mention", "compatibility_verified": False}


def infer_automotive_request(db_path, q, params):
    """Interpret only explicit words and indexed title mentions; preserve precise constraints."""
    result = {"vehicle": {}, "task": None, "spec": None, "residual": q, "conflicts": []}
    if not q:
        return result
    remaining = folded(q)
    def consume(pattern):
        nonlocal remaining
        found = bool(re.search(pattern, remaining, re.UNICODE))
        if found:
            remaining = re.sub(pattern, " ", remaining, flags=re.UNICODE)
        return found
    with connect(db_path) as conn:
        applications = [dict(row) for row in conn.execute(
            "SELECT DISTINCT make,model,generation,engine FROM video_vehicles "
            "WHERE make<>'' OR model<>''")]
        specs = [row[0] for row in conn.execute("SELECT DISTINCT value FROM video_specifications")]
    make_mentions = []
    make_aliases = {"Volkswagen": ["vw"], "Mercedes-Benz": ["mercedes", "mercedes benz"]}
    for make in sorted({item["make"] for item in applications if item["make"]}, key=len, reverse=True):
        if any(re.search(phrase_pattern(alias), remaining) for alias in [make] + make_aliases.get(make, [])):
            make_mentions.append(make)
    if len(make_mentions) == 1:
        result["vehicle"]["make"] = make_mentions[0]
        for alias in [make_mentions[0]] + make_aliases.get(make_mentions[0], []):
            consume(phrase_pattern(alias))
    scope = [item for item in applications if not result["vehicle"].get("make")
             or item["make"] == result["vehicle"]["make"]]
    model_mentions = []
    compact_remaining = re.sub(r"[\W_]", "", remaining, flags=re.UNICODE)
    # Case variants in imported evidence name one model, not competing mentions.
    models = {folded(model): model for model in sorted(
        {item["model"] for item in scope if item["model"]}, reverse=True)}
    for model in sorted(models.values(), key=len, reverse=True):
        if re.sub(r"[\W_]", "", folded(model), flags=re.UNICODE) not in compact_remaining:
            continue
        if model.isdigit() and not (result["vehicle"].get("make") or query_value(params, "make")):
            continue
        model_rows = [item for item in scope if folded(item["model"]) == folded(model)]
        combined = []
        indexed_generations = {item["generation"] for item in model_rows if item["generation"]}
        for generation in indexed_generations:
            aliases = [generation]
            if folded(generation) in ROMAN_GENERATIONS:
                aliases.append(ROMAN_GENERATIONS[folded(generation)])
            for alias in aliases:
                pattern = phrase_pattern(model + " " + alias) + r"(?![.,]\d)"
                if re.search(pattern, remaining):
                    roman = next((roman for roman, number in ROMAN_GENERATIONS.items() if number == generation), None)
                    canonical = next((value for value in sorted(indexed_generations) if folded(value) == roman), None) if roman else None
                    combined.append((canonical or generation, pattern))
        if combined:
            generations = {generation for generation, _ in combined}
            model_mentions.append((model, next(iter(generations)) if len(generations) == 1 else None,
                                   [pattern for _, pattern in combined]))
        elif re.search(phrase_pattern(model), remaining):
            # An explicitly requested but unindexed generation must remain a
            # structured constraint, never become a loose digit in full text.
            explicit_generation = re.search(phrase_pattern(model) +
                r"\s+(?:mk\s*)?(viii|vii|iii|vi|iv|ix|ii|v|x|i|10|[1-9])(?=$|[\s(),/?])", remaining)
            if explicit_generation:
                token = explicit_generation[1]
                generation = next((roman.upper() for roman, number in ROMAN_GENERATIONS.items()
                                   if number == token), token.upper())
                model_mentions.append((model, generation, [re.escape(explicit_generation[0])]))
            else:
                model_mentions.append((model, None, [phrase_pattern(model)]))
    # A longer model label takes precedence over its substring ("Golf Plus" over "Golf").
    if model_mentions:
        longest = max(len(item[0]) for item in model_mentions)
        model_mentions = [item for item in model_mentions if len(item[0]) == longest]
    if len(model_mentions) == 1:
        model, generation, patterns = model_mentions[0]
        result["vehicle"]["model"] = model
        if generation:
            result["vehicle"]["generation"] = generation
        for pattern in patterns:
            consume(pattern)
        scope = [item for item in scope if folded(item["model"]) == folded(model)]
        makes = {item["make"] for item in scope if item["make"]}
        if len(makes) == 1:
            result["vehicle"].setdefault("make", next(iter(makes)))
    elif query_value(params, "model"):
        scope = [item for item in scope if folded(item["model"]) == folded(query_value(params, "model"))]
    if result["vehicle"].get("model") or query_value(params, "model"):
        engine_mentions = [engine for engine in {item["engine"] for item in scope if item["engine"]}
                           if re.search(phrase_pattern(engine), remaining)]
        if len(engine_mentions) == 1:
            result["vehicle"]["engine"] = engine_mentions[0]
            consume(phrase_pattern(engine_mentions[0]))
        elif not engine_mentions:
            engine = re.search(r"(?<!\w)[0-8][.,]\d(?:\s*(?:l|litre|liter))?"
                r"(?:\s*(?:tdi|hdi|cdti|cdi|dci|tdci|tsi|tfsi|gdi|mpi|vtec|ecoboost|jtd|d4d|d-4d|16v|8v|v[468]))?(?!\w)",
                remaining)
            if engine:
                result["vehicle"]["engine"] = re.sub(r"\s+", " ", engine[0].upper().replace(",", "."))
                consume(re.escape(engine[0]))
        years = re.findall(r"(?<!\w)(?:19|20)\d{2}(?!\w)", remaining)
        if len(set(years)) == 1:
            result["vehicle"]["year"] = years[0]
            consume(phrase_pattern(years[0]))
    for task, aliases in TASK_PHRASES.items():
        matched = [alias for alias in aliases if re.search(phrase_pattern(alias), remaining)]
        if matched:
            result["task"] = task
            for alias in matched:
                # OBD is narrower than general diagnostics; retain that precise term.
                if alias != "obd":
                    consume(phrase_pattern(alias))
            break
    matched_specs = [spec for spec in specs if re.search(phrase_pattern(spec), remaining)
                     and not (result["vehicle"].get("make") == "BMW" and spec_key(spec) == "e85"
                              and not re.search(r"\b(?:fuel|carburant|ethanol|essence|combustible)\b", remaining))]
    if len({spec_key(value) for value in matched_specs}) == 1 and matched_specs:
        result["spec"] = matched_specs[0]
        consume(phrase_pattern(matched_specs[0]))
    if not result["spec"]:
        # Preserve an explicitly typed SAE grade even when no indexed video mentions it.
        grade = re.search(r"(?<!\w)(\d{1,2})[\s-]*w[\s-]*(\d{2})(?!\w)", remaining)
        if grade:
            result["spec"] = grade.group(1) + "W-" + grade.group(2)
            consume(phrase_pattern(result["spec"]))
    for key, value in result["vehicle"].items():
        explicit = query_value(params, key)
        if explicit and folded(explicit) != folded(value):
            result["conflicts"].append({"field": key, "selected": explicit, "mentioned": value})
    for key in ("task", "spec"):
        explicit, value = query_value(params, key), result[key]
        equal = spec_key(explicit) == spec_key(value) if key == "spec" else explicit == value
        if explicit and value and not equal:
            result["conflicts"].append({"field": key, "selected": explicit, "mentioned": value})
    if result["vehicle"] or result["task"] or result["spec"]:
        tokens = re.findall(r"[^\W_]+", remaining, re.UNICODE)
        ignored = AUTOMOTIVE_STOPWORDS | (
            {"huile", "oil", "aceite"} if result["task"] == "oil_change" or result["spec"] else set())
        result["residual"] = " ".join(token for token in tokens if token not in ignored)
    return result


def search(db_path, params, *, count_only=False, offset=None, no_assistance=False):
    page = integer_param(params, "page", 1, 1, 1000000)
    per_page = integer_param(params, "per_page", 24, 1, 100)
    q = query_value(params, "q").strip()
    if len(q) > 300:
        raise ValidationError("Recherche limitée à 300 caractères")
    interpretation = infer_automotive_request(db_path, q, params)
    effective_params = dict(params)
    for key, value in interpretation["vehicle"].items():
        if not query_value(params, key):
            effective_params[key] = str(value)
    for key in ("task", "spec"):
        if interpretation[key] and not query_value(params, key):
            effective_params[key] = interpretation[key]
    structured = bool(interpretation["vehicle"] or interpretation["task"] or interpretation["spec"])
    residual = interpretation["residual"]
    where, args, join = [], [], ""
    resource_format = query_value(params, "format", "all") or "all"
    content_format = query_value(params, "content_format")
    if resource_format not in {"all", "video", "guide", "image"}:
        raise ValidationError("Format attendu : all, video, guide ou image")
    if resource_format not in {"all", "video"}:
        where.append("0")
    if content_format and content_format not in {"all", "any", "*"}:
        if content_format not in set(CONTENT_FORMATS.values()):
            raise ValidationError("Format pédagogique invalide")
        where.append("v.pedagogical_format=?")
        args.append(content_format)
    search_mode, expanded_topics = ("structured" if structured else "literal"), []
    words = re.findall(r"[^\W_]+", residual, flags=re.UNICODE)[:20]
    has_search = bool(words)
    if has_search:
        # Every token is quoted. User input cannot become FTS operators or SQL.
        fts_query = " AND ".join('"' + token.replace('"', '""') + '"*' for token in words)
        join = " JOIN videos_fts ON videos_fts.rowid=v.rowid "
        where.append("videos_fts MATCH ?")
        args.insert(0, fts_query)
        # FTS alternatives update args[0]; keep its predicate first as well.
        where.insert(0, where.pop())
    elif residual:
        where.append("0")
    if interpretation["conflicts"]:
        where.append("0")
    vehicle_filters = vehicle_filter_values(effective_params)
    if vehicle_filters:
        clauses, values = vehicle_conditions(vehicle_filters)
        # Materialize matching IDs once. A correlated EXISTS can rescan the same
        # make/model range for each catalog row, multiplied by every facet query.
        where.append("v.id IN (SELECT vv.video_id FROM video_vehicles vv WHERE "
                     + " AND ".join(clauses) + ")")
        args.extend(values)
    for key, table, column in (("task", "video_tasks", "task"), ("system", "video_systems", "system"),
                               ("spec", "video_specifications", "value_key")):
        value = query_value(effective_params, key)
        if value and value not in {"all", "any", "*"}:
            if len(value) > 150:
                raise ValidationError(f"Filtre {key} trop long")
            where.append(f"v.id IN (SELECT aa.video_id FROM {table} aa WHERE aa.{column}=?)")
            args.append(spec_key(value) if key == "spec" else value)
    for field_name in ("category", "level", "language", "platform", "license"):
        value = query_value(params, field_name)
        if value and value not in {"all", "any", "*"}:
            if len(value) > 100:
                raise ValidationError(f"Filtre {field_name} trop long")
            if field_name == "category":
                value = normalized_category(value)
            elif field_name == "level":
                value = normalized_level(value)
            if field_name == "license" and value == "open":
                where.append("v.license IN ('creative-commons','public-domain')")
                continue
            where.append(f"v.{field_name}=?")
            args.append(value.lower())
    ids_value = query_value(params, "ids")
    if ids_value:
        ids = list(dict.fromkeys(ids_value.split(",")))
        if len(ids) > 100 or any(not re.fullmatch(r"[A-Za-z0-9_:-]{1,100}", value) for value in ids):
            raise ValidationError("ids doit contenir au maximum 100 identifiants valides séparés par une virgule")
        where.append("v.id IN (" + ",".join("?" for _ in ids) + ")")
        args.extend(ids)
    domain = query_value(params, "domain")
    if domain and domain not in {"all", "any"}:
        if domain not in {"motorsport", "automotive_adjacent"}:
            raise ValidationError("Contexte invalide")
        where.append("v.domain_scope=?")
        args.append(domain)
    duration = query_value(params, "duration")
    durations = {"short": "v.duration_seconds < 600",
                 "medium": "v.duration_seconds >= 600 AND v.duration_seconds < 1800",
                 "long": "v.duration_seconds >= 1800"}
    if duration and duration not in {"all", "any"}:
        if duration not in durations:
            raise ValidationError("Durée attendue: short, medium ou long")
        where.append("(" + durations[duration] + ")")
    transcript = query_value(params, "transcript")
    if transcript and transcript not in {"all", "any"}:
        if transcript in {"available", "true", "1"}:
            where.append("v.transcript_text <> ''")
        elif transcript in {"missing", "unavailable", "false", "0"}:
            where.append("v.transcript_text = ''")
        else:
            raise ValidationError("Filtre transcription invalide")
    base = " FROM videos v " + join + (" WHERE " + " AND ".join(where) if where else "")
    sort = query_value(params, "sort", "relevance")
    sorts = {
        "relevance": ("bm25(videos_fts,5.0,1.5,1.0,2.0,0.5,0.7),v.title COLLATE NOCASE,v.id"
                      if has_search else "v.review_status IN ('editorial_selection','curated','verified') DESC,"
                      "v.title COLLATE NOCASE,v.id"),
        "newest": "v.published_at IS NULL,v.published_at DESC,v.id",
        "title": "v.title COLLATE NOCASE,v.id",
        "duration": "v.duration_seconds IS NULL,v.duration_seconds,v.id",
    }
    if sort not in sorts:
        raise ValidationError("Tri invalide")
    with connect(db_path) as conn:
        total = conn.execute("SELECT COUNT(*)" + base, args).fetchone()[0]
        if has_search and not total:
            original_fts = args[0]
            for alternative, mode, topics in educational_query_candidates(residual, words):
                args[0] = alternative
                total = conn.execute("SELECT COUNT(*)" + base, args).fetchone()[0]
                if total:
                    search_mode, expanded_topics = mode, topics
                    break
            if not total:
                args[0] = original_fts
        if count_only:
            return {"total": total}
        rows = conn.execute("SELECT v.*" + base + " ORDER BY " + sorts[sort] + " LIMIT ? OFFSET ?",
                            args + [per_page, (page - 1) * per_page if offset is None else offset]).fetchall()
        facets = {}
        for facet in ("category", "level", "language", "platform", "license"):
            rows_facet = conn.execute(
                f"SELECT v.{facet} AS value,COUNT(*) AS count" + base
                + f" GROUP BY v.{facet} ORDER BY count DESC,value", args).fetchall()
            facets[facet] = [dict(r) for r in rows_facet]
        transcript_rows = conn.execute(
            "SELECT CASE WHEN v.transcript_text='' THEN 'missing' ELSE 'available' END AS value,"
            "COUNT(*) AS count" + base + " GROUP BY value ORDER BY value", args).fetchall()
        facets["transcript"] = [dict(r) for r in transcript_rows]
        facets["domain"] = [dict(r) for r in conn.execute(
            "SELECT v.domain_scope AS value,COUNT(*) AS count" + base
            + " GROUP BY v.domain_scope ORDER BY count DESC,value", args).fetchall()]
        facets["content_format"] = [dict(r) for r in conn.execute(
            "SELECT v.pedagogical_format AS value,COUNT(*) AS count" + base
            + " GROUP BY v.pedagogical_format ORDER BY count DESC,value", args)]
        facets["format"] = [{"value": "video", "count": total}]
        for facet_name, table, column in (("task", "video_tasks", "task"),
                                         ("system", "video_systems", "system"),
                                         ("spec", "video_specifications", "value")):
            facets[facet_name] = [dict(row) for row in conn.execute(
                f"SELECT aa.{column} AS value,COUNT(DISTINCT aa.video_id) AS count FROM {table} aa "
                "WHERE aa.video_id IN (SELECT v.id" + base + ")"
                f" GROUP BY aa.{column} ORDER BY count DESC,value", args)]
    return {"items": [serialize_video(r) for r in rows], "total": total, "page": page,
            "per_page": per_page, "pages": (total + per_page - 1) // per_page, "facets": facets,
            "query": q, "sort": sort, "search_mode": search_mode, "expanded_topics": expanded_topics,
            "inferred_vehicle": interpretation["vehicle"], "inferred_task": interpretation["task"],
            "inferred_spec": interpretation["spec"], "interpretation_conflicts": interpretation["conflicts"],
            "interpreted_fields": {key: interpretation[key] for key in ("vehicle", "task", "spec")},
            "query_residual": residual,
            "search_assistance": query_assistance(db_path, {**params, "format": "video" if resource_format == "all" else resource_format})
                if not total and not no_assistance else {"suggestions": [], "policy": "explicit_opt_in_filters_preserved"}}


def normalize_guides(payload):
    if not isinstance(payload, dict):
        return []
    records = ([payload["identification"]] if isinstance(payload.get("identification"), dict) else [])
    records += payload.get("guides", []) if isinstance(payload.get("guides"), list) else []
    result, seen = [], set()
    for guide in records[:200]:
        if not isinstance(guide, dict) or not re.fullmatch(r"[A-Za-z0-9_:-]{1,100}", str(guide.get("id", ""))):
            continue
        if guide["id"] in seen or not guide.get("title"):
            continue
        sources = []
        for source in guide.get("sources", []):
            try:
                if isinstance(source, dict) and web_url(source.get("url"), required=True):
                    sources.append(dict(source))
            except ValidationError:
                continue
        if not sources:
            continue
        seen.add(guide["id"])
        original = {**guide, "sources": sources}
        card_summary = guide.get("cardSummary")
        description = (card_summary.strip() if isinstance(card_summary, str) and card_summary.strip()
                       else guide.get("intro", guide.get("summary", "")))
        result.append({"id": guide["id"], "resource_type": "guide", "title": str(guide["title"]),
            "description": str(description), "creator": "RaceLink",
            "language": guide.get("language", payload.get("language", "fr")), "platform": "racelink",
            "category": "mechanics", "level": "unknown", "domain_scope": "automotive_adjacent",
            "content_format": "written_guide", "pedagogical_format": "guide", "format_status": "authored_guide",
            "license": "unknown", "has_transcript": False, "duration_seconds": None,
            "review_status": "authored_guide", "verification_scope": "editorial_guide_with_cited_sources",
            "scope": "general_method_not_vehicle_compatibility", "compatibility_verified": False,
            "sources": sources, "source_count": len(sources), "guide": original, "task": guide.get("task"),
            "verified_at": guide.get("verifiedAt", payload.get("updatedAt")),
            "automotive": {"vehicles": [], "tasks": [guide["task"]] if guide.get("task") else [],
                           "systems": [], "specifications": [], "status": "not_applicable"}})
    return result


def load_guides(public_path=PUBLIC):
    path = Path(public_path) / "vehicle-guides.json"
    if not path.is_file():
        return []
    if path.stat().st_size > 2 * 1024 * 1024:
        raise ValidationError("Fichier guides trop volumineux")
    return normalize_guides(json.loads(path.read_text(encoding="utf-8-sig")))


def matching_guides(guides, params, interpretation):
    # These explain a method; cited manufacturer examples never imply fitment.
    if (interpretation["conflicts"] or interpretation["vehicle"] or interpretation["spec"]
            or any(query_value(params, key) not in {"", "all", "any", "*"}
                   for key in VEHICLE_FILTERS + ("spec", "system", "duration", "content_format"))):
        return []
    task = query_value(params, "task") or interpretation["task"]
    terms = [word for word in re.findall(r"[^\W_]+", folded(interpretation["residual"]), re.UNICODE)
             if word not in AUTOMOTIVE_STOPWORDS]
    result = []
    for guide in guides:
        if task and task not in {"all", "any", "*"} and guide.get("task") != task:
            continue
        if any(query_value(params, key) not in {"", "all", "any", "*", str(guide.get(column, ""))}
               for key, column in (("language", "language"), ("platform", "platform"), ("category", "category"),
                                   ("level", "level"), ("license", "license"), ("domain", "domain_scope"))):
            continue
        if query_value(params, "transcript") in {"available", "true", "1"}:
            continue
        if query_value(params, "ids") and guide["id"] not in query_value(params, "ids").split(","):
            continue
        original = guide["guide"]
        # Search actual prose and known task aliases; publisher names are not vehicle applications.
        text = " ".join(discovery_text(original.get(key)) for key in
                        ("title", "intro", "summary", "steps", "checklist", "fields", "missingDetailsMessage"))
        text += " " + " ".join(TASK_PHRASES.get(guide.get("task"), []))
        words = re.findall(r"[^\W_]+", folded(text), re.UNICODE)
        if all(any(word.startswith(term) for word in words) for term in terms):
            result.append(guide)
    return sorted(result, key=lambda guide: (guide["title"].lower(), guide["id"]))


def search_resources(db_path, params, *, public_path=PUBLIC, guides=None, count_only=False, no_assistance=False):
    guides = load_guides(public_path) if guides is None else guides
    kind = query_value(params, "format", "all") or "all"
    video_params = {key: value for key, value in params.items() if key != "format"}
    interpretation = infer_automotive_request(db_path, query_value(params, "q").strip(), params)
    found_guides = matching_guides(guides, params, interpretation)
    page = integer_param(params, "page", 1, 1, 1000000)
    size = integer_param(params, "per_page", 24, 1, 100)
    if kind not in {"all", "video", "guide", "image"}:
        raise ValidationError("Format attendu : all, video, guide ou image")
    start = (page - 1) * size
    offset = max(0, start - len(found_guides)) if kind == "all" else start
    videos = search(db_path, video_params, count_only=count_only, offset=offset, no_assistance=True)
    total = (videos["total"] if kind in {"all", "video"} else 0) + (len(found_guides) if kind in {"all", "guide"} else 0)
    if count_only:
        return {"total": total}
    items = found_guides[start:start + size] if kind in {"all", "guide"} else []
    if kind in {"all", "video"}:
        items += videos["items"][:size - len(items)]
    facets = {key: list(values) if kind in {"all", "video"} else [] for key, values in videos["facets"].items()}
    if kind in {"all", "guide"}:
        for name, column in (("category", "category"), ("level", "level"), ("language", "language"),
                             ("platform", "platform"), ("license", "license"), ("domain", "domain_scope"),
                             ("task", "task"), ("transcript", "transcript_status")):
            counts = {item["value"]: item["count"] for item in facets.get(name, [])}
            for guide in found_guides:
                value = "missing" if name == "transcript" else guide.get(column)
                if value:
                    counts[value] = counts.get(value, 0) + 1
            facets[name] = [{"value": value, "count": count} for value, count in
                            sorted(counts.items(), key=lambda item: (-item[1], item[0]))]
    facets["format"] = [{"value": "video", "count": videos["total"]},
                        {"value": "guide", "count": len(found_guides)}, {"value": "image", "count": 0}]
    return {**videos, "items": items, "total": total, "pages": (total + size - 1) // size, "facets": facets,
            "format": kind, "total_videos": videos["total"], "total_guides": len(found_guides), "total_images": 0,
            "ordering": "guides_first_then_videos", "compatibility_verified": False,
            "search_assistance": query_assistance(db_path, params, config={**discovery_config(public_path), "_guides": guides})
                if not total and not no_assistance else {"suggestions": [], "policy": "explicit_opt_in_filters_preserved"}}


DISCOVERY_FILTERS = VEHICLE_FILTERS + ("task", "system", "spec", "category", "level",
    "language", "platform", "license", "duration", "transcript", "domain", "ids", "format", "content_format")
_DISCOVERY_COUNTS = {}


def discovery_context(params):
    return {key: query_value(params, key) for key in DISCOVERY_FILTERS
            if query_value(params, key) not in {"", "all", "any", "*"}}


def discovery_config(public_path=PUBLIC):
    path = Path(public_path) / "discovery-catalog.json"
    if not path.is_file():
        return {"version": 1, "intents": [], "topics": [], "shelves": []}
    if path.stat().st_size > 1024 * 1024:
        raise ValidationError("Configuration découverte trop volumineuse")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValidationError("Configuration découverte invalide")
    value["_guides"] = load_guides(public_path)
    return value


def merge_topic_context(topic, context):
    merged = dict(context)
    for key, value in discovery_context(topic.get("filters", {})).items():
        if key in merged:
            equal = (spec_key(merged[key]) == spec_key(value) if key == "spec"
                     else folded(merged[key]) == folded(value))
            if not equal:
                return None
        merged[key] = value
    return merged


def discovery_count(db_path, params, guides=None):
    path = Path(db_path)
    wal = Path(str(path) + "-wal")
    try:
        wal_stat = wal.stat()
    except FileNotFoundError:
        wal_stat = None
    revision = (str(path.resolve()), path.stat().st_mtime_ns,
                wal_stat.st_mtime_ns if wal_stat and wal_stat.st_size else 0)
    guides = guides or []
    guide_revision = hashlib.sha256(json.dumps(guides, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    key = revision + (json.dumps(params, sort_keys=True, ensure_ascii=False), guide_revision)
    if key not in _DISCOVERY_COUNTS:
        if len(_DISCOVERY_COUNTS) >= 512:
            _DISCOVERY_COUNTS.pop(next(iter(_DISCOVERY_COUNTS)))
        _DISCOVERY_COUNTS[key] = search_resources(db_path, params, guides=guides, count_only=True)["total"]
    return _DISCOVERY_COUNTS[key]


def discovery_topics(db_path, config, context):
    topics = []
    for topic in config.get("topics", [])[:100]:
        if not isinstance(topic, dict) or topic.get("enabled", True) is False:
            continue
        filters = merge_topic_context(topic, context)
        query = str(topic.get("query") or "")
        count = 0 if filters is None else discovery_count(db_path, {**filters, "q": query}, config.get("_guides"))
        topics.append({**topic, "count": count,
                       "filters": filters if filters is not None else dict(context),
                       "context_conflict": filters is None})
    return topics


def active_editorial_dates(item, shelf, now):
    if shelf.get("enabled") is not True or item.get("enabled", True) is False:
        return False
    try:
        reviewed = dt.datetime.fromisoformat(str(item.get("reviewedAt", shelf.get("reviewedAt", ""))).replace("Z", "+00:00"))
        expires = dt.datetime.fromisoformat(str(item.get("expiresAt", shelf.get("expiresAt", ""))).replace("Z", "+00:00"))
        return reviewed.tzinfo is not None and expires.tzinfo is not None and reviewed <= now < expires
    except (TypeError, ValueError):
        return False


def discovery_shelves(db_path, config, context, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    shelves = []
    with connect(db_path) as conn:
        for shelf in config.get("shelves", [])[:20]:
            if not isinstance(shelf, dict):
                continue
            items, seen = [], set()
            for entry in shelf.get("items", [])[:12]:
                if not isinstance(entry, dict) or not active_editorial_dates(entry, shelf, now):
                    continue
                identifier = str(entry.get("videoId", ""))
                if not re.fullmatch(r"[A-Za-z0-9_:-]{1,100}", identifier) or identifier in seen:
                    continue
                if context.get("ids") and identifier not in context["ids"].split(","):
                    continue
                row = conn.execute("SELECT * FROM videos WHERE id=? AND review_status='editorial_selection'",
                                   (identifier,)).fetchone()
                if row is None or not discovery_count(db_path, {**context, "ids": identifier}):
                    continue
                seen.add(identifier)
                items.append({**entry, "video": serialize_video(row)})
            if items:
                shelves.append({**shelf, "items": items})
    return shelves


def discovery(db_path, params, *, config=None, public_path=PUBLIC, now=None):
    config = config if config is not None else discovery_config(public_path)
    context = discovery_context(params)
    return {"version": config.get("version", 1), "intents": config.get("intents", [])[:20],
            "topics": discovery_topics(db_path, config, context),
            "shelves": discovery_shelves(db_path, config, context, now),
            "context": context, "generated_at": utcnow(), "policy": "explicit_filters_preserved"}


def discovery_text(value):
    if isinstance(value, dict):
        return " ".join(discovery_text(part) for part in value.values())
    if isinstance(value, list):
        return " ".join(discovery_text(part) for part in value)
    return str(value or "")


def one_topic_edit(left, right):
    """One insertion, deletion, substitution or adjacent transposition; never identifiers."""
    if left == right or abs(len(left) - len(right)) > 1:
        return False
    if len(left) == len(right):
        different = [i for i, pair in enumerate(zip(left, right)) if pair[0] != pair[1]]
        return len(different) == 1 or (len(different) == 2
            and different[1] == different[0] + 1
            and left[different[0]] == right[different[1]]
            and left[different[1]] == right[different[0]])
    shorter, longer = (left, right) if len(left) < len(right) else (right, left)
    index = next((i for i, pair in enumerate(zip(shorter, longer)) if pair[0] != pair[1]), len(shorter))
    return shorter[index:] == longer[index + 1:]


def topic_prediction(topic, query, context=None):
    """Complete only known topical tokens, keeping every other input character."""
    context = context or {}
    phrases = [(str(alias), 12, True) for alias in topic.get("aliases", []) if isinstance(alias, str)]
    phrases += [(alias, 14, True) for alias in TASK_PHRASES.get(topic.get("filters", {}).get("task"), [])]
    phrases += [(discovery_text(topic.get("query")), 8, False),
                (discovery_text(topic.get("label")), 4, False)]
    terms = {}
    for phrase, weight, editable in phrases:
        for match in re.finditer(r"[^\W_]+", phrase, re.UNICODE):
            word = folded(match[0])
            if len(word) < 3:
                continue
            old = terms.get(word)
            if old is None or weight > old["weight"]:
                terms[word] = {"text": match[0], "weight": weight,
                               "editable": editable and word.isalpha()
                               and not (match[0].isupper() and len(word) <= 5)}
    protected = set()
    for key in VEHICLE_FILTERS + ("spec",):
        protected.update(re.findall(r"[^\W_]+", folded(context.get(key, "")), re.UNICODE))
    matches, score = [], 0
    for token in re.finditer(r"[^\W_]+", query, re.UNICODE):
        word = folded(token[0])
        if word in AUTOMOTIVE_STOPWORDS or word in protected:
            continue
        # Numbers, engine codes, oil grades and short technical acronyms are immutable.
        immutable = not word.isalpha() or (token[0].isupper() and len(word) <= 5)
        target, kind = word, "exact"
        if word not in terms:
            candidates = [] if immutable or len(word) < 3 else [
                term for term, value in terms.items() if value["editable"] and term.startswith(word)]
            if candidates:
                target = min(candidates, key=lambda term: (-terms[term]["weight"], len(term), term))
                kind = "prefix"
            else:
                candidates = [] if immutable or len(word) < 4 else [
                    term for term, value in terms.items()
                    if value["editable"] and len(term) >= 4 and one_topic_edit(word, term)]
                if len(candidates) != 1:
                    continue
                target, kind = candidates[0], "typo"
        value = terms[target]
        score += {"exact": 24, "prefix": 12, "typo": 4}[kind] + value["weight"]
        replacement = token[0] if kind == "exact" else value["text"]
        if token[0][:1].isupper() and kind != "exact":
            replacement = replacement[:1].upper() + replacement[1:]
        matches.append({"start": token.start(), "end": token.end(), "from": token[0],
                        "to": replacement, "kind": kind, "term": target})
    if not matches or sum(item["kind"] == "typo" for item in matches) > 1:
        return None
    for phrase, weight, _ in phrases:
        words = re.findall(r"[^\W_]+", folded(phrase), re.UNICODE)
        if len(words) > 1 and re.search(phrase_pattern(phrase), folded(query)):
            score += 30 + weight
    def variant(replacements):
        completion = query
        for item in reversed(replacements):
            completion = completion[:item["start"]] + item["to"] + completion[item["end"]:]
        corrections = [{key: item[key] for key in ("from", "to", "kind")}
                       for item in replacements if item["from"] != item["to"]]
        return {"completion": completion, "corrections": corrections,
                "match_basis": "topic_typo" if any(item["kind"] == "typo" for item in corrections)
                else "prefix_completion" if corrections else "exact_terms"}
    variants = [variant(matches)]
    # A single topical word can expand into an existing multi-word alias. This is
    # only tried if the literal completed question has no matching catalog entry.
    if len(matches) == 1:
        matched = matches[0]
        for phrase, _, editable in sorted(phrases, key=lambda item: -item[1]):
            words = re.findall(r"[^\W_]+", folded(phrase), re.UNICODE)
            if not editable or not 1 < len(words) <= 4 or matched["term"] not in words:
                continue
            if any(word in protected or any(char.isdigit() for char in word) for word in words):
                continue
            extra = {**matched, "to": phrase,
                     "kind": "typo" if matched["kind"] == "typo" else "prefix"}
            candidate = variant([extra])
            if candidate["completion"] not in {item["completion"] for item in variants}:
                variants.append(candidate)
            if len(variants) >= 4:
                break
    return {"score": score, "variants": variants}


def topic_score(topic, query):
    prediction = topic_prediction(topic, query)
    return prediction["score"] if prediction else 0


def query_assistance(db_path, params, *, config=None, include_topics=True):
    """Count explicit recovery proposals without modifying the query or relaxing a filter."""
    query = query_value(params, "q").strip()
    result = {"suggestions": [], "policy": "explicit_opt_in_filters_preserved"}
    if not 3 <= len(query) <= 300:
        return result
    config = discovery_config() if config is None else config
    interpretation = infer_automotive_request(db_path, query, params)
    if interpretation["conflicts"]:
        return result
    context = discovery_context(params)
    for key, value in interpretation["vehicle"].items():
        context.setdefault(key, str(value))
    for key in ("task", "spec"):
        if interpretation[key]:
            context.setdefault(key, interpretation[key])
    tokens = list(re.finditer(r"[^\W_]+", query, re.UNICODE))
    words = [folded(token[0]) for token in tokens]
    candidates = []
    for rule in config.get("queryAssistance", [])[:30]:
        if not isinstance(rule, dict) or not isinstance(rule.get("aliases"), list) or not isinstance(rule.get("query"), str):
            continue
        aliases = [re.findall(r"[^\W_]+", folded(alias), re.UNICODE)
                   for alias in rule["aliases"][:50] if isinstance(alias, str)]
        aliases.sort(key=len, reverse=True)
        span = None
        for alias in aliases:
            start = next((index for index in range(len(words))
                          if alias and words[index:index + len(alias)] == alias), None)
            if start is not None:
                span = (tokens[start].start(), tokens[start + len(alias) - 1].end())
                break
        if span is None:
            continue
        start, end = span
        completion = query[:start] + rule["query"] + query[end:]
        if folded(completion) == folded(query):
            continue
        candidates.append({"type": "query", "id": "help-" + rule["id"], "label": rule.get("label") or rule["query"],
            "query": completion, "completion": completion, "filters": dict(context),
            "match_basis": "topic_typo" if rule.get("kind") == "typo" else "symptom_vocabulary",
            "corrections": [{"from": query[start:end], "to": rule["query"], "kind": "typo" if rule.get("kind") == "typo" else "symptom"}],
            "reason": rule.get("reason") or {
                "fr": "Explorer ce sujet avec les mêmes filtres. Ce n’est pas un diagnostic.",
                "en": "Explore this topic with the same filters. This is not a diagnosis.",
                "es": "Explorar este tema con los mismos filtros. No es un diagnóstico."}})
    if include_topics:
        ranked = []
        for topic in config.get("topics", [])[:100]:
            if not isinstance(topic, dict) or topic.get("enabled", True) is False:
                continue
            filters = merge_topic_context(topic, context)
            prediction = topic_prediction(topic, query, context) if filters is not None else None
            if prediction:
                ranked.append((prediction["score"], topic, filters, prediction["variants"]))
        ranked.sort(key=lambda entry: -entry[0])
        for _, topic, filters, variants in ranked:
            for variant in variants:
                if not variant["corrections"]:
                    continue
                candidates.append({"type": "query", "id": "help-topic-" + topic["id"], "label": topic.get("label") or topic["id"],
                    "query": variant["completion"], "filters": filters, **variant, "reason": {
                        "fr": "Correction proposée pour les mots du sujet ; vos filtres restent appliqués.",
                        "en": "Suggested topic-word correction; your filters stay applied.",
                        "es": "Corrección propuesta del tema; se mantienen los filtros."}})
    seen = set()
    for candidate in candidates[:8]:
        if len(candidate["query"]) > 300:
            continue
        key = json.dumps([candidate["query"], candidate["filters"]], sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        count = discovery_count(db_path, {**candidate["filters"], "q": candidate["query"]}, config.get("_guides"))
        if count:
            result["suggestions"].append({**candidate, "count": count})
        if len(result["suggestions"]) >= 3:
            break
    return result


def suggestions(db_path, params, *, config=None, public_path=PUBLIC):
    config = config if config is not None else discovery_config(public_path)
    query = query_value(params, "q").strip()
    if len(query) > 300:
        raise ValidationError("Recherche limitée à 300 caractères")
    if query and len(query) < 2:
        return {"query": query, "suggestions": [], "limit": 6}
    context = discovery_context(params)
    interpretation = infer_automotive_request(db_path, query, params)
    if interpretation["conflicts"]:
        return {"query": query, "suggestions": [], "limit": 6, "context": context,
                "interpretation_conflicts": interpretation["conflicts"]}
    for key, value in interpretation["vehicle"].items():
        context.setdefault(key, str(value))
    if interpretation["spec"]:
        context.setdefault("spec", interpretation["spec"])
    ranked = []
    for index, topic in enumerate(config.get("topics", [])[:100]):
        if not isinstance(topic, dict) or topic.get("enabled", True) is False:
            continue
        filters = merge_topic_context(topic, context)
        if filters is None:
            continue
        prediction = topic_prediction(topic, query, context) if query else {
            "score": 0, "variants": [{"completion": str(topic.get("query") or ""),
                                     "corrections": [], "match_basis": "editorial_default"}]}
        if prediction:
            ranked.append((prediction["score"], index, topic, filters, prediction["variants"]))
    defaults = config.get("defaultTopicIds", [])
    ranked.sort(key=lambda value: (
        -value[0], defaults.index(value[2]["id"]) if not query and value[2]["id"] in defaults
        else len(defaults) + value[1], value[1]))
    limit = 3 if query else 5
    items = query_assistance(db_path, params, config=config, include_topics=False)["suggestions"][:2]
    for _, _, topic, filters, variants in ranked:
        for prediction in variants:
            completion = prediction["completion"]
            if len(completion) > 300:
                continue
            count = discovery_count(db_path, {**filters, "q": completion}, config.get("_guides"))
            if not count:
                continue
            typo = prediction["match_basis"] == "topic_typo"
            correction = {"fr": "Petite faute possible dans un terme du sujet ; correction proposée.",
                          "en": "Possible small typo in a topic term; correction suggested.",
                          "es": "Posible errata en un término del tema; corrección sugerida."} if typo else None
            items.append({"type": "topic", "id": topic["id"], "label": topic.get("label", topic["id"]),
                          "query": completion, "filters": filters, "count": count, **prediction,
                          "correction": correction, "reason": correction or {
                              "fr": "Question conservée ; seuls les mots du sujet sont complétés." if query else "Point de départ éditorial.",
                              "en": "Question preserved; only topic words are completed." if query else "Editorial starting point.",
                              "es": "Pregunta conservada; solo se completan los términos del tema." if query else "Punto de partida editorial."}})
            break
        if len(items) >= limit:
            break
    if query and len(items) < 6 and context.get("format", "all") in {"all", "guide"}:
        guide_result = search_resources(db_path, {**context, "format": "guide", "q": query,
            "per_page": str(6 - len(items))}, guides=config.get("_guides", []), no_assistance=True)
        items.extend({"type": "guide", "resource_type": "guide", "id": guide["id"],
            "label": guide["title"], "query": query, "filters": context,
            "reason": {"fr": "Guide RaceLink avec sources citées, correspondant à la recherche.",
                       "en": "RaceLink guide with cited sources matching the search.",
                       "es": "Guía RaceLink con fuentes citadas que coincide con la búsqueda."}}
            for guide in guide_result["items"])
    if query and len(items) < 6:
        result = search(db_path, {**context, "q": query, "per_page": str(6 - len(items)), "sort": "title"}, no_assistance=True)
        items.extend({"type": "video", "id": item["id"], "video_id": item["id"], "label": item["title"],
                      **{key: item[key] for key in (
                          "creator", "platform", "language", "language_status", "language_confidence")},
                      "query": query, "filters": context, "reason": {
                          "fr": "Titre présent dans le catalogue, correspondant à la recherche et aux filtres.",
                          "en": "Existing catalog title matching the search and filters.",
                          "es": "Título existente que coincide con la búsqueda y los filtros."}}
                     for item in result["items"])
    return {"query": query, "suggestions": items[:6], "limit": 6,
            "policy": "existing_topics_and_titles", "context": context}


def recommendations(db_path, params, *, config=None, public_path=PUBLIC, now=None):
    config = config if config is not None else discovery_config(public_path)
    context = discovery_context(params)
    query = query_value(params, "q").strip()
    if len(query) > 300:
        raise ValidationError("Recherche limitée à 300 caractères")
    interpretation = infer_automotive_request(db_path, query, params)
    for key, value in interpretation["vehicle"].items():
        context.setdefault(key, str(value))
    if interpretation["spec"]:
        context.setdefault("spec", interpretation["spec"])
    video_id = query_value(params, "video_id")
    inferred_category = None
    if video_id:
        if not re.fullmatch(r"[A-Za-z0-9_:-]{1,100}", video_id):
            raise ValidationError("Identifiant vidéo invalide")
        with connect(db_path) as conn:
            row = conn.execute("SELECT title,category FROM videos WHERE id=?", (video_id,)).fetchone()
        if row:
            query = query or row["title"]
            if not context.get("category"):
                context["category"] = inferred_category = row["category"]
    topics = [topic for topic in discovery_topics(db_path, config, context)
              if topic["count"] > 0 and not interpretation["conflicts"]
              and not (topic["filters"] == context and folded(topic.get("query") or "") == folded(query))]
    related = [topic for topic in topics if topic_score(topic, query) > 0 or (
        interpretation["task"] and topic["filters"].get("task") == interpretation["task"])]
    if query and (interpretation["task"] or any(topic_score(topic, query) > 0 for topic in config.get("topics", []))):
        topics = related
    defaults = config.get("defaultTopicIds", [])
    positions = {topic["id"]: index for index, topic in enumerate(topics)}
    topics.sort(key=lambda topic: (-topic_score(topic, query),
        defaults.index(topic["id"]) if topic["id"] in defaults else len(defaults) + positions[topic["id"]]))
    ranked, used_intents = [], set()
    for topic in topics:
        intent = topic.get("intentId", topic.get("intent", topic["id"]))
        if topic_score(topic, query) > 0 or intent not in used_intents:
            ranked.append(topic)
            used_intents.add(intent)
    ranked.extend(topic for topic in topics if topic not in ranked)
    selected = []
    for topic in ranked[:4]:
        lexical = topic_score(topic, query) > 0
        selected.append({**topic, "match_basis": "lexical_and_filters" if lexical else "context_filters",
                         "reason": {
                             "fr": "Mots en commun et filtres conservés." if lexical else "Sujet disponible avec ces filtres.",
                             "en": "Shared words and preserved filters." if lexical else "Topic available with these filters.",
                             "es": "Palabras comunes y filtros conservados." if lexical else "Tema disponible con estos filtros."}})
    return {"topics": selected, "shelves": [] if interpretation["conflicts"] else discovery_shelves(db_path, config, context, now),
            "context": {"filters": context, "query": query, "video_id": video_id or None,
                        "inferred_category": inferred_category},
            "reason": {"fr": "Propositions de sujets à ouvrir ; la recherche actuelle reste inchangée.",
                       "en": "Topic suggestions to open; the current search remains unchanged.",
                       "es": "Temas sugeridos para abrir; la búsqueda actual no cambia."},
            "policy": "explicit_filters_preserved", "interpretation_conflicts": interpretation["conflicts"]}


def stats(db_path, public_path=PUBLIC):
    with connect(db_path) as conn:
        result = dict(conn.execute(
            "SELECT COUNT(*) AS total_videos,COUNT(DISTINCT platform) AS platforms,"
            "COUNT(DISTINCT CASE WHEN language NOT IN ('und','mul') THEN language END) AS languages,"
            "COUNT(DISTINCT category) AS categories,"
            "COALESCE(SUM(transcript_text<>''),0) AS with_transcript,"
            "COALESCE(SUM(source_questions_text<>''),0) AS with_source_questions,"
            "COALESCE(SUM(json_array_length(metadata_json,'$.source_questions')),0) AS total_source_questions,"
            "COALESCE(SUM(review_status IN ('verified','curated','approved') AND verification_scope "
            "IN ('editorial_review','video_review','content_review')),0) AS verified_videos,"
            "COALESCE(SUM(review_status='editorial_selection'),0) AS selected_videos,"
            "COALESCE(SUM(license IN ('creative-commons','public-domain','permission')),0) AS reusable_videos,"
            "MAX(updated_at) AS updated_at FROM videos").fetchone())
        result["facets"] = {
            name: [dict(r) for r in conn.execute(
                f"SELECT {name} AS value,COUNT(*) AS count FROM videos GROUP BY {name} "
                "ORDER BY count DESC,value").fetchall()]
            for name in ("category", "language", "platform", "level", "license")}
        result["facets"]["domain"] = [dict(r) for r in conn.execute(
            "SELECT domain_scope AS value,COUNT(*) AS count FROM videos "
            "GROUP BY domain_scope ORDER BY count DESC,value").fetchall()]
        result["language_status_counts"] = [dict(row) for row in conn.execute(
            "SELECT language,language_status AS status,COUNT(*) AS count FROM videos "
            "GROUP BY language,language_status ORDER BY language,language_status")]
        summary = {}
        for group in result["language_status_counts"]:
            entry = summary.setdefault(group["language"], {"language": group["language"], "total": 0,
                "platform_declared": 0, "source_caption_track": 0, "estimated": 0, "unknown": 0})
            entry["total"] += group["count"]
            entry[language_confidence(group["language"], group["status"])] += group["count"]
        result["language_summary"] = sorted(summary.values(), key=lambda entry: (-entry["total"], entry["language"]))
        result["facets"]["content_format"] = [dict(r) for r in conn.execute(
            "SELECT pedagogical_format AS value,COUNT(*) AS count FROM videos "
            "GROUP BY pedagogical_format ORDER BY count DESC,value")]
        result["facets"]["format"] = [{"value": "video", "count": result["total_videos"]}]
        for name, table, column in (("task", "video_tasks", "task"), ("system", "video_systems", "system"),
                                    ("spec", "video_specifications", "value")):
            result["facets"][name] = [dict(row) for row in conn.execute(
                f"SELECT {column} AS value,COUNT(DISTINCT video_id) AS count FROM {table} "
                f"GROUP BY {column} ORDER BY count DESC,value")]
        result["with_vehicle_mentions"] = conn.execute(
            "SELECT COUNT(DISTINCT video_id) FROM video_vehicles").fetchone()[0]
        last_import = conn.execute(
            "SELECT finished_at,inserted,updated,rejected FROM import_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        result["last_import"] = dict(last_import) if last_import else None
        result["catalog_notice"] = (
            "Catalogue de liens et métadonnées publics. L'accès public ne constitue pas une licence "
            "de réutilisation. Les langues et niveaux estimés sont signalés; seules les "
            "transcriptions assorties d'une autorisation documentée sont indexées.")
    result["total_guides"] = len(load_guides(public_path))
    result["total_images"] = 0
    result["total_resources"] = result["total_videos"] + result["total_guides"]
    result["facets"]["format"] += [{"value": "guide", "count": result["total_guides"]}, {"value": "image", "count": 0}]
    return result


def get_video(db_path, video_id):
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM videos WHERE id=?", (video_id,)).fetchone()
        if not row:
            return None
        result = serialize_video(row, detail=True)
        related = conn.execute(
            "SELECT * FROM videos WHERE category=? AND id<>? ORDER BY language=? DESC,title LIMIT 6",
            (row["category"], row["id"], row["language"])).fetchall()
        result["related"] = [serialize_video(r) for r in related]
        return result


class CatalogHandler(BaseHTTPRequestHandler):
    server_version = "FocusAcademy/1.0"

    def log_message(self, fmt, *args):
        # Avoid log-control characters from untrusted URLs.
        message = (fmt % args).encode("unicode_escape").decode("ascii")
        print(f"{self.client_address[0]} {message}", file=sys.stderr)

    def common_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")

    def json_response(self, value, status=200, head=False):
        payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.common_headers()
        self.end_headers()
        if not head:
            self.wfile.write(payload)

    def do_HEAD(self):
        self.handle_get(head=True)

    def do_GET(self):
        self.handle_get()

    def do_POST(self):
        self.json_response({"error": "API en lecture seule; utiliser les outils d'import locaux"}, 405)

    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.do_POST()

    def handle_get(self, head=False):
        try:
            parsed = urlsplit(self.path)
            route = unquote(parsed.path)
            if "\x00" in route or "\\" in route or ".." in route.split("/"):
                return self.json_response({"error": "Chemin invalide"}, 400, head)
            if route.startswith("/aide/api/"):
                route = route.removeprefix("/aide")
            if route in {"/api/videos", "/api/videos/"}:
                params = parse_qs(parsed.query, max_num_fields=30)
                return self.json_response(search(self.server.db_path, params), head=head)
            if route in {"/api/resources", "/api/resources/"}:
                params = parse_qs(parsed.query, max_num_fields=30)
                return self.json_response(search_resources(self.server.db_path, params,
                    public_path=self.server.public_path), head=head)
            if route.startswith("/api/resources/guide/"):
                guide_id = route.removeprefix("/api/resources/guide/")
                resource = next((guide for guide in load_guides(self.server.public_path) if guide["id"] == guide_id), None)
                return self.json_response({"resource": resource} if resource else {"error": "Guide introuvable"},
                                          200 if resource else 404, head)
            if route == "/api/stats":
                return self.json_response(stats(self.server.db_path, self.server.public_path), head=head)
            if route == "/api/vehicle-options":
                params = parse_qs(parsed.query, max_num_fields=30)
                return self.json_response(vehicle_options(self.server.db_path, params), head=head)
            discovery_routes = {"/api/discovery": discovery, "/api/suggestions": suggestions,
                                "/api/recommendations": recommendations}
            if route in discovery_routes:
                params = parse_qs(parsed.query, max_num_fields=30)
                return self.json_response(discovery_routes[route](
                    self.server.db_path, params, public_path=self.server.public_path), head=head)
            if route == "/api/health":
                return self.json_response({"status": "ok", "service": "focus-academy"}, head=head)
            if route.startswith("/api/videos/"):
                video_id = route.removeprefix("/api/videos/")
                if not re.fullmatch(r"[A-Za-z0-9_:-]{1,100}", video_id):
                    return self.json_response({"error": "Vidéo introuvable"}, 404, head)
                value = get_video(self.server.db_path, video_id)
                return self.json_response(value or {"error": "Vidéo introuvable"},
                                          200 if value else 404, head)
            if route.startswith("/api/"):
                return self.json_response({"error": "Route inconnue"}, 404, head)
            if route in {"/", "/aide", "/aide/"}:
                route = "/index.html"
            elif route.startswith("/aide/"):
                route = route.removeprefix("/aide")
            root = Path(self.server.public_path).resolve()
            target = (root / route.lstrip("/")).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                return self.json_response({"error": "Fichier introuvable"}, 404, head)
            if target.suffix.lower() not in {".html", ".css", ".js", ".json", ".png", ".jpg", ".jpeg",
                                           ".webp", ".svg", ".ico", ".woff", ".woff2", ".txt"}:
                return self.json_response({"error": "Type de fichier interdit"}, 403, head)
            data = target.read_bytes()
            self.send_response(200)
            mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            if mime.startswith("text/") or mime in {"application/javascript", "application/json"}:
                mime += "; charset=utf-8"
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.common_headers()
            self.end_headers()
            if not head:
                self.wfile.write(data)
        except (ValidationError, ValueError) as exc:
            self.json_response({"error": str(exc)}, 400, head)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            # The API never returns database paths, SQL, or a traceback.
            import traceback
            traceback.print_exc()
            self.json_response({"error": "Erreur interne du catalogue"}, 500, head)


def make_server(db_path=DEFAULT_DB, port=8765, public_path=PUBLIC):
    server = ThreadingHTTPServer(("127.0.0.1", port), CatalogHandler)
    server.daemon_threads = True
    server.db_path = Path(db_path)
    server.public_path = Path(public_path)
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--seed", type=Path, help="Import JSON idempotent avant démarrage")
    parser.add_argument("--public", type=Path, default=PUBLIC)
    parser.add_argument("--import-only", action="store_true")
    args = parser.parse_args()
    initialize(args.db)
    if args.seed:
        print(json.dumps(import_json(args.db, args.seed), ensure_ascii=False), flush=True)
    if args.import_only:
        return
    server = make_server(args.db, args.port, args.public)
    print(f"Focus Académie : http://127.0.0.1:{server.server_port}/aide", flush=True)
    print(f"Catalogue SQLite : {args.db}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
