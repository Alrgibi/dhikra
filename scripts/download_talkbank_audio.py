"""
download_talkbank_audio.py
--------------------------
Downloads every recording from a TalkBank protected media folder into one
local folder. Free, no browser extension, no clicking Save.

WHY THIS EXISTS
TalkBank ships transcripts as a single zip but explicitly does not do the same
for media, and the browser extensions they suggest are mostly paywalled for
bulk downloads. This does the same job with the Python you already have.

WHAT IT DOES
  * reads the folder listing on media.talkbank.org
  * finds every audio file linked there
  * downloads them all into one folder
  * SKIPS anything already downloaded, so an interrupted run just resumes
  * verifies each file is non-trivial in size, so a truncated download is
    caught rather than silently producing a corrupt recording

USAGE (Windows)
    python scripts\\download_talkbank_audio.py --user YOURNAME --password YOURPASS

USAGE (Mac / Linux)
    python3 scripts/download_talkbank_audio.py --user YOURNAME --password YOURPASS

By default it fetches the Cookie Theft recordings for both groups, which is
the only task in the Pitt corpus that has healthy controls as well as
patients, and therefore the only one a classifier can be trained on.

IF THE PASSWORD IS REJECTED
TalkBank protects these folders with HTTP Basic authentication, which is the
grey username/password box the browser shows. If your credentials are refused
here but work in the browser, the folder may instead be behind a session
cookie; pass --cookie "name=value" using the cookie your browser holds (see
--help for how to find it).
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://media.talkbank.org/dementia/English/Pitt"
DEFAULT_FOLDERS = ["Control/cookie", "Dementia/cookie"]
AUDIO_RE = re.compile(r'href="([^"?]+\.(?:mp3|wav|m4a|ogg))"', re.I)
MIN_BYTES = 2000          # anything smaller is an error page, not a recording


def _opener(user: str | None, password: str | None, cookie: str | None):
    handlers = []
    if user and password:
        mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        mgr.add_password(None, BASE, user, password)
        handlers.append(urllib.request.HTTPBasicAuthHandler(mgr))
        handlers.append(urllib.request.HTTPDigestAuthHandler(mgr))
    op = urllib.request.build_opener(*handlers)
    headers = [("User-Agent", "Mozilla/5.0 (dhikra research downloader)")]
    if cookie:
        headers.append(("Cookie", cookie))
    if user and password:
        # some servers do not challenge, so send the header pre-emptively
        tok = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers.append(("Authorization", f"Basic {tok}"))
    op.addheaders = headers
    return op


def list_files(opener, folder: str) -> list[str]:
    url = f"{BASE}/{folder}/"
    try:
        with opener.open(url, timeout=60) as r:
            html = r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(f"  ACCESS DENIED for {url}")
            print("  -> check the username/password, or use --cookie")
        else:
            print(f"  HTTP {e.code} for {url}")
        return []
    except Exception as e:
        print(f"  could not reach {url}: {type(e).__name__}: {e}")
        return []

    names = []
    for href in AUDIO_RE.findall(html):
        name = href.split("/")[-1]
        if name and name not in names:
            names.append(name)
    return sorted(names)


def download(opener, folder: str, name: str, out_dir: str,
             retries: int = 3) -> str:
    """Returns 'ok', 'skip' or 'fail'."""
    dest = os.path.join(out_dir, name)
    if os.path.exists(dest) and os.path.getsize(dest) > MIN_BYTES:
        return "skip"
    url = f"{BASE}/{folder}/{urllib.parse.quote(name)}"
    tmp = dest + ".part"
    for attempt in range(1, retries + 1):
        try:
            with opener.open(url, timeout=180) as r, open(tmp, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
            if os.path.getsize(tmp) <= MIN_BYTES:
                raise IOError("file too small - probably an error page")
            os.replace(tmp, dest)
            return "ok"
        except Exception as e:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass
            if attempt == retries:
                print(f"    ! {name}: {type(e).__name__}: {str(e)[:70]}")
                return "fail"
            time.sleep(2 * attempt)
    return "fail"


def main():
    ap = argparse.ArgumentParser(
        description="Bulk-download TalkBank Pitt audio.",
        epilog="To find a cookie: open the media folder in Chrome, press F12, "
               "go to Network, refresh, click the request, and copy the "
               "'Cookie:' request header value.")
    ap.add_argument("--user", help="your TalkBank username")
    ap.add_argument("--password", help="your TalkBank password")
    ap.add_argument("--cookie", help='alternative auth, e.g. "session=abc123"')
    ap.add_argument("--out", default="pitt_audio", help="destination folder")
    ap.add_argument("--folders", nargs="*", default=DEFAULT_FOLDERS,
                    help="which corpus folders to fetch")
    args = ap.parse_args()

    if not (args.user and args.password) and not args.cookie:
        ap.error("provide --user and --password, or --cookie")

    os.makedirs(args.out, exist_ok=True)
    opener = _opener(args.user, args.password, args.cookie)

    print(f"destination: {os.path.abspath(args.out)}\n")
    total_ok = total_skip = total_fail = 0

    for folder in args.folders:
        print(f"[{folder}] reading file list...")
        names = list_files(opener, folder)
        if not names:
            print("  no files found - skipping\n")
            continue
        print(f"  {len(names)} recordings listed")

        ok = skip = fail = 0
        for i, name in enumerate(names, 1):
            status = download(opener, folder, name, args.out)
            if status == "ok":
                ok += 1
            elif status == "skip":
                skip += 1
            else:
                fail += 1
            if i % 20 == 0 or i == len(names):
                print(f"  {i}/{len(names)}   downloaded={ok} "
                      f"already-had={skip} failed={fail}")
        total_ok += ok
        total_skip += skip
        total_fail += fail
        print()

    have = len([f for f in os.listdir(args.out)
                if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))])
    print("=" * 60)
    print(f"downloaded {total_ok}, already had {total_skip}, failed {total_fail}")
    print(f"folder now contains {have} recordings")
    if total_fail:
        print("\nRun the same command again to retry the failures - "
              "completed files are skipped.")
    print("\nNext step:")
    print(f'  python scripts/extract_audio_features.py --audio "{os.path.abspath(args.out)}"')


if __name__ == "__main__":
    main()
