#!/usr/bin/env python3
"""Collect explicit publisher-page seeds, never request social platforms or media.

All output is a review queue. An article or an anchor is never a video caption.
Standard library only. Redirects, proxies, logins and browser sessions are unused.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import socket
import ssl
import time
from urllib.parse import parse_qsl, urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

VERSION = "1.0.0"
USER_AGENT = "RaceLinkCreatorLinks/1.0"
FORBIDDEN_HOSTS = ("tiktok.com", "instagram.com", "tiktokcdn.com", "cdninstagram.com", "tiktokv.com", "tiktokcdn-us.com", "musical.ly", "ibytedtos.com", "ibyteimg.com", "byteoversea.com")
SECRET_QUERY_KEYS = {"access_token", "token", "api_key", "apikey", "authorization", "password", "secret"}


class CollectionError(ValueError):
    pass


def validate_target(url, allowed_hosts):
    """Validate a publisher URL without contacting it or resolving its hostname."""
    if any(ord(c) < 32 for c in url):
        raise CollectionError("Control character in URL")
    u = urlsplit(url)
    host = (u.hostname or "").lower().rstrip(".")
    if u.scheme != "https" or not host or u.username or u.password or u.port not in (None, 443):
        raise CollectionError("Only credential-free HTTPS on port 443 is supported")
    if any(host == x or host.endswith("." + x) for x in FORBIDDEN_HOSTS):
        raise CollectionError("Native social platform requests are forbidden")
    if host not in {h.lower().rstrip(".") for h in allowed_hosts}:
        raise CollectionError("Publisher host is not explicitly allowlisted")
    if any(k.lower() in SECRET_QUERY_KEYS for k, _ in parse_qsl(u.query)):
        raise CollectionError("Credential-bearing query parameters are forbidden")
    return urlunsplit(("https", host, u.path or "/", u.query, ""))


def public_addresses(host, resolver=None):
    """Reject private, loopback, reserved and mixed public/private DNS answers."""
    resolver = resolver or socket.getaddrinfo
    answers = resolver(host, 443, type=socket.SOCK_STREAM)
    addresses = []
    for family, _, _, _, sockaddr in answers:
        value = sockaddr[0]
        addr = ipaddress.ip_address(value)
        if not addr.is_global or addr.is_multicast:
            raise CollectionError("Publisher resolves to a non-public network address")
        pair = (family, str(addr))
        if pair not in addresses:
            addresses.append(pair)
    if not addresses:
        raise CollectionError("No public publisher address")
    return addresses


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to prevalidated numeric IPs; preserve TLS hostname verification."""
    def __init__(self, host, addresses, timeout):
        super().__init__(host, timeout=timeout, context=ssl.create_default_context())
        self.addresses = addresses

    def connect(self):
        last = None
        for family, address in self.addresses:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            try:
                sock.connect((address, 443))
                self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
                return
            except OSError as exc:
                last = exc
                sock.close()
        raise CollectionError("Public publisher connection failed") from last


def fetch_public(url, allowed_hosts, max_bytes=2_000_000, timeout=15):
    url = validate_target(url, allowed_hosts)
    u = urlsplit(url)
    connection = PinnedHTTPSConnection(u.hostname, public_addresses(u.hostname), timeout)
    try:
        path = u.path + ("?" + u.query if u.query else "")
        connection.request("GET", path, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,text/plain;q=0.8", "Accept-Encoding": "identity"})
        r = connection.getresponse()
        headers = {k.lower(): v for k, v in r.getheaders()}
        # Do not consume denied/redirect/media bodies, and never follow Location.
        mime = headers.get("content-type", "").split(";", 1)[0].lower()
        permitted = ("text/plain", "application/octet-stream", "") if u.path == "/robots.txt" else ("text/html", "application/xhtml+xml")
        body = b"" if r.status in (401, 403, 429) or 300 <= r.status < 400 or mime not in permitted else r.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise CollectionError("Publisher response exceeds byte limit")
        return {"status": r.status, "headers": headers, "body": body}
    finally:
        connection.close()


def canonical_social_url(url, source_url=""):
    """Recognize direct post identities only, without resolving any URL."""
    try:
        u = urlsplit(urljoin(source_url, url))
        if u.scheme not in ("https", "http") or u.username or u.password:
            return None
        host = (u.hostname or "").lower()
        if host in ("tiktok.com", "www.tiktok.com", "m.tiktok.com"):
            m = re.fullmatch(r"/@([A-Za-z0-9._-]+)/video/(\d{15,22})/?", u.path)
            if m:
                return {"id": "tiktok:" + m[2], "platform": "tiktok", "url": f"https://www.tiktok.com/@{m[1]}/video/{m[2]}", "content_type_hint": "video"}
        if host in ("instagram.com", "www.instagram.com", "m.instagram.com"):
            m = re.fullmatch(r"/(reel|reels|p|tv)/([A-Za-z0-9_-]{5,32})/?", u.path)
            if m:
                kind = "reel" if m[1] == "reels" else m[1]
                return {"id": "instagram:" + m[2], "platform": "instagram", "url": f"https://www.instagram.com/{kind}/{m[2]}/", "content_type_hint": "video" if kind in ("reel", "tv") else "unknown_post_type"}
    except ValueError:
        pass
    return None


class Node:
    def __init__(self, tag="", attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or []), parent, []

    def text(self):
        if self.tag in ("script", "style", "noscript", "template"):
            return ""
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)


class PageParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node()
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag == "a" and "href" in node.attrs:
            self.anchors.append(node)
        if tag not in self.VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current
        while node.parent is not None:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def extract_links(raw, source_url):
    """Extract paired anchors/context; never claim either is the native caption."""
    sha = hashlib.sha256(raw).hexdigest()
    parser = PageParser()
    parser.feed(raw.decode("utf-8", "replace"))
    results = []
    for anchor in parser.anchors:
        social = canonical_social_url(anchor.attrs["href"], source_url)
        if not social:
            continue
        ancestor = anchor.parent
        while ancestor and ancestor.tag not in ("p", "li", "blockquote", "article", "div", "section", "body"):
            ancestor = ancestor.parent
        # The HTML hash preserves provenance. Query/fragment values from outgoing
        # links must not leak into the public review queue, even in visible text.
        raw_label = anchor.text().replace(anchor.attrs["href"], social["url"])
        label = " ".join(raw_label.split())
        context = " ".join(ancestor.text().split()) if ancestor else label
        context = context.replace(anchor.attrs["href"], social["url"])
        outgoing = urlsplit(urljoin(source_url, anchor.attrs["href"]))
        results.append({**social, "title": label, "description": "", "language": "und", "review_status": "requires_editorial_review", "verification_scope": "publisher_website_link", "audio_language_verified": False, "native_access_verified": False, "license": "unknown", "source": {"url": source_url, "sha256": sha, "anchor_href": social["url"], "anchor_href_query_or_fragment_removed": bool(outgoing.query or outgoing.fragment), "anchor_text": label, "anchor_text_raw": raw_label, "context_text": context[:600], "context_truncated": len(context) > 600, "context_is_video_caption": False}})
    return results


def collect(seeds, allowed_hosts, *, max_pages=10, delay=1.0, max_bytes=2_000_000, timeout=15, known_ids=(), fetcher=fetch_public, sleeper=time.sleep):
    if not 1 <= max_pages <= 100 or not 0.5 <= delay <= 60 or not 1000 <= max_bytes <= 5_000_000 or not 1 <= timeout <= 60:
        raise CollectionError("Limits: pages 1–100, delay 0.5–60s, bytes 1000–5000000, timeout 1–60s")
    normalized = list(dict.fromkeys(validate_target(u, allowed_hosts) for u in seeds))
    if len(normalized) > max_pages:
        raise CollectionError("Explicit seed count exceeds max-pages; no partial silent crawl")
    robots, blocked, seen, errors, pages, events = {}, set(), {}, [], [], []
    known = set(known_ids)

    def get(url, cap):
        if events:
            sleeper(delay)
        events.append({"url": url})
        result = fetcher(url, allowed_hosts, max_bytes=cap, timeout=timeout)
        events[-1]["status"] = result["status"]
        return result

    for url in normalized:
        host = urlsplit(url).hostname
        if host in blocked:
            errors.append({"url": url, "reason": "host_stopped_after_prior_refusal_or_error"})
            continue
        try:
            if host not in robots:
                robots_url = "https://" + host + "/robots.txt"
                result = get(robots_url, min(max_bytes, 128_000))
                status = result["status"]
                if status == 404:
                    rules = RobotFileParser()
                    rules.parse([])
                elif status == 200:
                    content_type = result["headers"].get("content-type", "").split(";", 1)[0].lower()
                    if content_type and content_type not in ("text/plain", "application/octet-stream"):
                        raise CollectionError("Unexpected robots content type; no publisher request")
                    rules = RobotFileParser()
                    rules.parse(result["body"].decode("utf-8", "replace").splitlines())
                else:
                    raise CollectionError(f"robots HTTP {status}; no retry or redirect")
                robots[host] = rules
            rules = robots[host]
            if not rules.can_fetch(USER_AGENT, url):
                raise CollectionError("robots_disallow; host stopped")
            crawl_delay = rules.crawl_delay(USER_AGENT)
            request_rate = rules.request_rate(USER_AGENT)
            required_delay = max(delay, crawl_delay or 0, request_rate.seconds / request_rate.requests if request_rate else 0)
            if required_delay > 60:
                raise CollectionError("robots delay exceeds the bounded 60-second wait; host stopped")
            if required_delay > delay:
                sleeper(required_delay - delay)
            result = get(url, max_bytes)
            status = result["status"]
            if status != 200:
                raise CollectionError(f"publisher HTTP {status}; no retry or redirect")
            content_type = result["headers"].get("content-type", "").split(";", 1)[0].lower()
            if content_type not in ("text/html", "application/xhtml+xml"):
                raise CollectionError("Non-HTML response refused; no media processing")
            raw = result["body"]
            if len(raw) > max_bytes:
                raise CollectionError("Publisher response exceeds byte limit")
            links = extract_links(raw, url)
            pages.append({"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "link_occurrences": len(links)})
            for entry in links:
                if entry["id"] not in seen:
                    entry["occurrences"] = [entry.pop("source")]
                    entry["already_known"] = entry["id"] in known
                    seen[entry["id"]] = entry
                else:
                    seen[entry["id"]]["occurrences"].append(entry["source"])
        except (CollectionError, OSError, http.client.HTTPException, ValueError) as exc:
            blocked.add(host)
            errors.append({"url": url, "reason": str(exc), "host_stopped": True})
    return {"collector": "creator_site_collect", "version": VERSION, "created_at": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "review_queue_not_an_import", "limits": {"max_pages": max_pages, "delay": delay, "max_bytes": max_bytes, "timeout": timeout}, "seed_count": len(normalized), "requests": events, "pages": pages, "errors": errors, "known_ids_skipped": sorted(x["id"] for x in seen.values() if x["already_known"]), "candidates": [x for x in seen.values() if not x["already_known"]], "native_social_requests": 0, "media_downloads": 0, "database_modified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    live = commands.add_parser("collect", help="Fetch only explicit publisher seeds, respecting robots")
    live.add_argument("--seed", action="append", required=True)
    live.add_argument("--allow-host", action="append", required=True)
    live.add_argument("--max-pages", type=int, default=10)
    live.add_argument("--delay", type=float, default=1.0)
    live.add_argument("--max-bytes", type=int, default=2_000_000)
    live.add_argument("--timeout", type=int, default=15)
    live.add_argument("--known-ids", type=Path)
    live.add_argument("--output", type=Path, required=True)
    offline = commands.add_parser("extract", help="Extract from an already saved HTML page; no network")
    offline.add_argument("--html", type=Path, required=True)
    offline.add_argument("--source-url", required=True)
    offline.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; use a new snapshot path")
    try:
        if args.command == "extract":
            url = validate_target(args.source_url, [urlsplit(args.source_url).hostname or ""])
            if args.html.stat().st_size > 5_000_000:
                raise CollectionError("Offline HTML exceeds 5 MB")
            result = {"collector": "creator_site_collect", "version": VERSION, "status": "review_queue_not_an_import", "network_requests": 0, "candidates": extract_links(args.html.read_bytes(), url)}
        else:
            known = json.loads(args.known_ids.read_text(encoding="utf-8")) if args.known_ids else []
            if not isinstance(known, list) or not all(isinstance(x, str) for x in known):
                raise CollectionError("known-ids must be a JSON array of canonical string IDs")
            result = collect(args.seed, args.allow_host, max_pages=args.max_pages, delay=args.delay, max_bytes=args.max_bytes, timeout=args.timeout, known_ids=known)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output), "candidates": len(result["candidates"]), "errors": len(result.get("errors", [])), "imported": 0}))
    except (CollectionError, OSError, ValueError) as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
