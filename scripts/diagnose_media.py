"""
diagnose_media.py
-----------------
Shows exactly what the TalkBank media server returns, so the downloader can be
pointed at the right thing instead of guessed at.

The downloader reported "no files found" without an access error, which means
the request SUCCEEDED but the returned page contained no direct links to audio
files. There are only a few possible reasons, and they need different fixes:

  * a login page was returned instead of a listing   -> needs session cookie
  * the listing is drawn by JavaScript               -> browser required
  * the folder path is different from the one assumed -> fix the URL
  * files are not .mp3 at that level                  -> fix the pattern

This prints the status, the final URL after any redirects, the content type,
and the first part of the body, plus every link it can see. That identifies the
cause immediately.

USAGE
    python scripts\\diagnose_media.py --user YOURNAME --password YOURPASS
    python scripts\\diagnose_media.py --cookie "paste=cookie"

Paste the whole output back and the downloader can be corrected precisely.
"""
from __future__ import annotations

import argparse
import base64
import re
import urllib.error
import urllib.request

CANDIDATES = [
    "https://media.talkbank.org/dementia/English/Pitt/",
    "https://media.talkbank.org/dementia/English/Pitt/Control/cookie/",
    "https://media.talkbank.org/dementia/English/Pitt/Control/",
    "https://media.talkbank.org/dementia/",
]

LINK_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)


def build_opener(user, password, cookie):
    handlers = []
    if user and password:
        mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        mgr.add_password(None, "https://media.talkbank.org", user, password)
        handlers.append(urllib.request.HTTPBasicAuthHandler(mgr))
        handlers.append(urllib.request.HTTPDigestAuthHandler(mgr))
    op = urllib.request.build_opener(*handlers)
    hdrs = [("User-Agent", "Mozilla/5.0")]
    if cookie:
        hdrs.append(("Cookie", cookie))
    if user and password:
        tok = base64.b64encode(f"{user}:{password}".encode()).decode()
        hdrs.append(("Authorization", f"Basic {tok}"))
    op.addheaders = hdrs
    return op


def probe(opener, url: str) -> None:
    print("=" * 70)
    print(f"URL: {url}")
    print("=" * 70)
    try:
        with opener.open(url, timeout=45) as r:
            body = r.read(6000).decode("utf-8", errors="replace")
            print(f"  status       : {r.status}")
            print(f"  final url    : {r.geturl()}")
            print(f"  content-type : {r.headers.get('Content-Type')}")
            print(f"  length       : {r.headers.get('Content-Length')}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP ERROR   : {e.code} {e.reason}")
        try:
            body = e.read(3000).decode("utf-8", errors="replace")
        except Exception:
            body = ""
        auth = e.headers.get("WWW-Authenticate") if e.headers else None
        if auth:
            print(f"  auth scheme  : {auth}")
    except Exception as e:
        print(f"  FAILED       : {type(e).__name__}: {e}")
        return

    links = LINK_RE.findall(body)
    print(f"\n  links found  : {len(links)}")
    for l in links[:25]:
        print(f"      {l}")
    exts = {}
    for l in links:
        if "." in l.split("/")[-1]:
            e = l.split(".")[-1].lower()[:5]
            exts[e] = exts.get(e, 0) + 1
    if exts:
        print(f"  extensions   : {exts}")

    looks_login = any(w in body.lower() for w in
                      ("password", "sign in", "log in", "login"))
    print(f"  looks like a login page: {looks_login}")
    print(f"  mentions javascript    : {'<script' in body.lower()}")

    print("\n  --- first 900 characters of the body ---")
    print("  " + body[:900].replace("\n", "\n  "))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user")
    ap.add_argument("--password")
    ap.add_argument("--cookie")
    args = ap.parse_args()

    op = build_opener(args.user, args.password, args.cookie)
    for url in CANDIDATES:
        probe(op, url)

    print("Paste this whole output back so the downloader can be fixed.")


if __name__ == "__main__":
    main()
