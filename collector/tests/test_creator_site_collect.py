import importlib.util
from pathlib import Path
import socket
import unittest
import json
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "creator_site_collect.py"
spec = importlib.util.spec_from_file_location("creator_site_collect", SOURCE)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CreatorCollectorTests(unittest.TestCase):
    def test_canonical_tiktok_query_removed(self):
        self.assertEqual(c.canonical_social_url("https://www.tiktok.com/@creator/video/7531530713762385174?tracking=x")["url"], "https://www.tiktok.com/@creator/video/7531530713762385174")

    def test_instagram_alias_identity_and_post_uncertainty(self):
        self.assertEqual(c.canonical_social_url("https://instagram.com/reels/ABC123_def-/")["url"], "https://www.instagram.com/reel/ABC123_def-/")
        self.assertEqual(c.canonical_social_url("https://instagram.com/p/ABC123_def-/")["content_type_hint"], "unknown_post_type")

    def test_profiles_shortlinks_and_fake_domains_not_posts(self):
        for value in ["https://tiktok.com/@creator", "https://vm.tiktok.com/abc", "https://instagram.com/creator/", "https://instagram.com.evil.test/reel/ABCD12345/", "https://user:pass@instagram.com/reel/ABCD12345/"]:
            self.assertIsNone(c.canonical_social_url(value), value)

    def test_anchors_context_and_hash_do_not_become_captions(self):
        raw = b'<p>Creator explains brakes <a href="https://instagram.com/reel/ABCD12345/">Brake &amp; pads</a></p><script>bad</script>'
        r = c.extract_links(raw, "https://publisher.test/page")[0]
        self.assertEqual(r["title"], "Brake & pads")
        self.assertEqual(r["description"], "")
        self.assertFalse(r["source"]["context_is_video_caption"])
        self.assertEqual(len(r["source"]["sha256"]), 64)
        self.assertEqual(r["source"]["context_text"], "Creator explains brakes Brake & pads")

    def test_secret_outgoing_query_is_not_exported_in_proof_or_visible_url(self):
        href = "https://www.instagram.com/reel/ABCDEF/?access_token=TEST_SECRET#private_fragment"
        raw = f'<p><a href="{href}">{href}</a></p>'.encode()
        result = c.extract_links(raw, "https://publisher.test/page")
        serialized = json.dumps(result)
        self.assertNotIn("TEST_SECRET", serialized)
        self.assertNotIn("private_fragment", serialized)
        self.assertTrue(result[0]["source"]["anchor_href_query_or_fragment_removed"])
        self.assertEqual(result[0]["source"]["anchor_href"], "https://www.instagram.com/reel/ABCDEF/")

    def test_forbidden_native_and_credential_urls(self):
        for u in ["https://www.tiktok.com/x", "https://www.instagram.com/x", "https://x:t@publisher.test/x", "http://publisher.test/x", "https://publisher.test:444/x", "https://publisher.test/?access_token=secret"]:
            with self.assertRaises(c.CollectionError):
                c.validate_target(u, ["publisher.test", "www.tiktok.com", "www.instagram.com"])

    def test_exact_host_allowlist(self):
        with self.assertRaises(c.CollectionError):
            c.validate_target("https://publisher.test.evil.test/x", ["publisher.test"])

    def test_private_and_mixed_dns_answers_denied(self):
        def answer(ips):
            return lambda *a, **kw: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443)) for ip in ips]
        for ips in [["127.0.0.1"], ["10.1.1.1"], ["169.254.169.254"], ["192.168.1.1"], ["8.8.8.8", "10.1.1.1"]]:
            with self.assertRaises(c.CollectionError):
                c.public_addresses("publisher.test", answer(ips))
        self.assertEqual(c.public_addresses("publisher.test", answer(["8.8.8.8"])), [(socket.AF_INET, "8.8.8.8")])

    def test_ipv6_loopback_denied(self):
        with self.assertRaises(c.CollectionError):
            c.public_addresses("publisher.test", lambda *a, **kw: [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 443, 0, 0))])

    @staticmethod
    def fake(responses):
        calls = []
        def fetch(url, *a, **kw):
            calls.append(url)
            return responses[url]
        return fetch, calls

    @staticmethod
    def response(status=200, body=b"", content_type="text/html"):
        return {"status": status, "body": body, "headers": {"content-type": content_type}}

    def test_robots_deny_stops_host(self):
        f, calls = self.fake({"https://publisher.test/robots.txt": self.response(body=b"User-agent: *\nDisallow: /", content_type="text/plain")})
        r = c.collect(["https://publisher.test/a", "https://publisher.test/b"], ["publisher.test"], fetcher=f, sleeper=lambda _: None)
        self.assertEqual(calls, ["https://publisher.test/robots.txt"])
        self.assertEqual(len(r["errors"]), 2)

    def test_robots_429_stops_before_content(self):
        f, calls = self.fake({"https://publisher.test/robots.txt": self.response(429)})
        r = c.collect(["https://publisher.test/a"], ["publisher.test"], fetcher=f, sleeper=lambda _: None)
        self.assertEqual(calls, ["https://publisher.test/robots.txt"])
        self.assertEqual(len(r["errors"]), 1)

    def test_large_robots_delay_does_not_block_for_minutes(self):
        f, calls = self.fake({"https://publisher.test/robots.txt": self.response(body=b"User-agent: *\nCrawl-delay: 600", content_type="text/plain")})
        sleeps = []
        r = c.collect(["https://publisher.test/a"], ["publisher.test"], fetcher=f, sleeper=sleeps.append)
        self.assertEqual(calls, ["https://publisher.test/robots.txt"])
        self.assertEqual(sleeps, [])
        self.assertEqual(len(r["errors"]), 1)

    def test_real_fetcher_does_not_read_media_response_body(self):
        response = mock.Mock(status=200)
        response.getheaders.return_value = [("Content-Type", "video/mp4")]
        connection = mock.Mock()
        connection.getresponse.return_value = response
        with mock.patch.object(c, "public_addresses", return_value=[(socket.AF_INET, "8.8.8.8")]), mock.patch.object(c, "PinnedHTTPSConnection", return_value=connection):
            result = c.fetch_public("https://publisher.test/video", ["publisher.test"])
        response.read.assert_not_called()
        self.assertEqual(result["body"], b"")
        connection.close.assert_called_once()

    def test_403_429_stop_without_following_or_retry(self):
        for status in [403, 429]:
            f, calls = self.fake({"https://publisher.test/robots.txt": self.response(404), "https://publisher.test/a": self.response(status)})
            r = c.collect(["https://publisher.test/a", "https://publisher.test/b"], ["publisher.test"], fetcher=f, sleeper=lambda _: None)
            self.assertEqual(calls, ["https://publisher.test/robots.txt", "https://publisher.test/a"])
            self.assertEqual(len(r["errors"]), 2)

    def test_redirect_not_followed(self):
        f, calls = self.fake({"https://publisher.test/robots.txt": self.response(404), "https://publisher.test/a": {"status": 302, "body": b"", "headers": {"location": "https://instagram.com/reel/ABCD12345/"}}})
        r = c.collect(["https://publisher.test/a"], ["publisher.test"], fetcher=f, sleeper=lambda _: None)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(r["candidates"]), 0)

    def test_never_follows_social_or_internal_links(self):
        html = b'<a href="https://instagram.com/reel/ABCD12345/">Tutorial</a><a href="https://publisher.test/b">Next</a>'
        f, calls = self.fake({"https://publisher.test/robots.txt": self.response(404), "https://publisher.test/a": self.response(body=html)})
        r = c.collect(["https://publisher.test/a"], ["publisher.test"], fetcher=f, sleeper=lambda _: None)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(r["candidates"]), 1)
        self.assertEqual(r["native_social_requests"], 0)

    def test_duplicates_and_known_ids(self):
        html = b'<a href="https://instagram.com/reel/ABCD12345/">Tuto</a><a href="https://www.instagram.com/reel/ABCD12345/?x=1">Same</a>'
        f, _ = self.fake({"https://publisher.test/robots.txt": self.response(404), "https://publisher.test/a": self.response(body=html)})
        r = c.collect(["https://publisher.test/a"], ["publisher.test"], known_ids=["instagram:ABCD12345"], fetcher=f, sleeper=lambda _: None)
        self.assertEqual(r["candidates"], [])
        self.assertEqual(r["known_ids_skipped"], ["instagram:ABCD12345"])

    def test_media_and_oversized_content_rejected(self):
        for response in [self.response(body=b"image", content_type="image/jpeg"), self.response(body=b"x" * 1001)]:
            f, _ = self.fake({"https://publisher.test/robots.txt": self.response(404), "https://publisher.test/a": response})
            r = c.collect(["https://publisher.test/a"], ["publisher.test"], max_bytes=1000, fetcher=f, sleeper=lambda _: None)
            self.assertEqual(len(r["errors"]), 1)

    def test_limits_checked_before_any_request(self):
        def forbidden(*a, **kw):
            self.fail("Network attempted")
        with self.assertRaises(c.CollectionError):
            c.collect(["https://publisher.test/a", "https://publisher.test/b"], ["publisher.test"], max_pages=1, fetcher=forbidden)
        with self.assertRaises(c.CollectionError):
            c.collect(["https://publisher.test/a"], ["publisher.test"], delay=0, fetcher=forbidden)


if __name__ == "__main__":
    unittest.main()
