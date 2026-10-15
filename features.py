"""URL features + human-readable reasons. Shared by train.py and app.py."""
import re
from urllib.parse import urlparse

KEYWORDS = ["login","verify","secure","account","update","bank","signin","confirm",
            "password","paypal","wallet","free","bonus","upi","kyc"]
SHORTENERS = ["bit.ly","tinyurl.com","goo.gl","t.co","is.gd","cutt.ly"]
BAD_TLDS = ["xyz","top","tk","ml","ga","cf","gq","click","work","zip"]
FEATURE_NAMES = ["url_len","host_len","dots","hyphens","at_symbol","digits","is_ip","https",
                 "subdomains","keyword_hits","shortener","bad_tld","double_slash","has_port",
                 "path_len","special_chars"]

def _parse(url):
    url = url.strip()
    p = urlparse(url if "://" in url else "http://" + url)
    return url, p, (p.hostname or "").lower()

def extract(url):
    url, p, host = _parse(url)
    parts, low = host.split("."), url.lower()
    return [len(url), len(host), host.count("."), host.count("-"), int("@" in url),
            sum(c.isdigit() for c in host),
            int(bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host))),
            int(p.scheme == "https"), max(len(parts) - 2, 0),
            sum(k in low for k in KEYWORDS), int(any(s in host for s in SHORTENERS)),
            int(parts[-1] in BAD_TLDS), int("//" in p.path), int(p.port is not None),
            len(p.path), len(re.findall(r"[?=&%_~]", url))]

def reasons(url):
    """Returns list of (level, text) shown under the riskometer. level: bad / warn / good"""
    url, p, host = _parse(url)
    f = dict(zip(FEATURE_NAMES, extract(url)))
    out = []
    if f["is_ip"]: out.append(("bad", "Uses an IP address instead of a website name"))
    if f["at_symbol"]: out.append(("bad", "Contains an @ symbol that hides the real destination"))
    if f["shortener"]: out.append(("warn", "Shortened link hides where it really goes"))
    if f["bad_tld"]: out.append(("warn", "Uses a domain ending often seen in scams"))
    if f["keyword_hits"] >= 2: out.append(("bad", "Several bait words like login, verify, account"))
    elif f["keyword_hits"] == 1: out.append(("warn", "Contains a bait word like login or verify"))
    if f["subdomains"] >= 3: out.append(("warn", "Unusually many subdomains"))
    if f["hyphens"] >= 2: out.append(("warn", "Many hyphens in the website name"))
    if f["url_len"] > 75: out.append(("warn", "Very long link"))
    if not f["https"]: out.append(("warn", "Not using a secure HTTPS connection"))
    else: out.append(("good", "Uses a secure HTTPS connection"))
    if not any(l != "good" for l, _ in out): out.append(("good", "No common phishing signs found"))
    return out