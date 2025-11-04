from __future__ import annotations
import datetime as dt, hashlib, json, os, re, time
from pathlib import Path
from typing import Dict, Any, Iterable
import requests
from lxml import etree

# ──────────────────────────────────────
#  ░░ USER CONFIG (keep yours) ░░
# ──────────────────────────────────────
USER_NAME: str = os.getenv("USER_NAME", "Alans44")   # <- override in workflow to yours
BIRTHDAY = dt.datetime(2004, 4, 4)                   # yyyy, m, d (keep if you print age)
SVG_FILES = ["banner.svg"]                           # keep your file list; light/dark optional
CACHE_DIR = Path("cache"); CACHE_DIR.mkdir(exist_ok=True)
COMMENT_SIZE = 7                                     # if you reserve comment lines in SVG

# ──────────────────────────────────────
#  ░░ INTERNALS ░░
# ──────────────────────────────────────
GQL = "https://api.github.com/graphql"
GH_TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"bearer {GH_TOKEN}"} if GH_TOKEN else {}

def _gql(query: str, variables: Dict[str, Any] | None = None) -> Dict[str, Any]:
    r = requests.post(GQL, json={"query": query, "variables": variables or {}}, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GraphQL HTTP {r.status_code}: {r.text}")
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]

def _cache_path(name: str) -> Path:
    key = hashlib.sha256(name.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{key}.json"

def cache_get(name: str, max_age_s: int) -> Any | None:
    p = _cache_path(name)
    if not p.exists(): return None
    if time.time() - p.stat().st_mtime > max_age_s: return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def cache_put(name: str, obj: Any) -> None:
    _cache_path(name).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def get_user_stats(login: str) -> Dict[str, Any]:
    """Pulls live stats with a single GraphQL round-trip (plus a languages pass that’s cached)."""
    q = """
    query($login: String!) {
      user(login: $login) {
        name
        login
        followers { totalCount }
        following { totalCount }
        repositories(privacy: PUBLIC, isFork: false) { totalCount }
        starredRepositories { totalCount }
        pullRequests(states: MERGED) { totalCount }
        issues(states: CLOSED) { totalCount }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
          pullRequestContributionsByRepository { contributions { totalCount } }
        }
        repositoriesContributedTo(contributionTypes: [COMMIT], privacy: PUBLIC, includeUserRepositories: false) {
          totalCount
        }
        topRepositories(first: 8, orderBy: {field: STARGAZERS, direction: DESC}) {
          nodes { name stargazerCount }
        }
      }
    }"""
    d = _gql(q, {"login": login})["user"]

    # Language-bytes snapshot (cached ~1 day) using REST to stay cheap; approx LOC = bytes/50.
    lang_cache_key = f"langs:{login}"
    langs = cache_get(lang_cache_key, max_age_s=24*3600)
    if langs is None:
        # pull first 100 public repos’ languages (good enough for a banner)
        # (GraphQL languagesCollection exists but can be heavy; REST per-repo with ETags is fine)
        langs = {}
        page = 1
        while page <= 2:  # cap to ~200 repos for rate safety
            rr = requests.get(
                f"https://api.github.com/users/{login}/repos",
                params={"per_page": 100, "page": page, "type": "public", "sort": "updated"},
                headers=HEADERS, timeout=30
            )
            rr.raise_for_status()
            repos = rr.json()
            if not repos: break
            for repo in repos:
                lr = requests.get(repo["languages_url"], headers=HEADERS, timeout=30)
                if lr.status_code == 200:
                    for lang, bytes_ in lr.json().items():
                        langs[lang] = langs.get(lang, 0) + int(bytes_)
            page += 1
        cache_put(lang_cache_key, langs)

    total_lang_bytes = sum(langs.values()) or 1
    top_langs = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:5]
    approx_loc = total_lang_bytes // 50  # rough byte→LOC heuristic

    # Flatten stats for templating
    stats = {
        "name": d.get("name") or login,
        "login": d["login"],
        "followers": d["followers"]["totalCount"],
        "following": d["following"]["totalCount"],
        "public_repos": d["repositories"]["totalCount"],
        "stars": d["starredRepositories"]["totalCount"],
        "merged_prs": d["pullRequests"]["totalCount"],
        "closed_issues": d["issues"]["totalCount"],
        "commits_year": d["contributionsCollection"]["totalCommitContributions"]
                        + d["contributionsCollection"]["restrictedContributionsCount"],
        "repos_contributed_to": d["repositoriesContributedTo"]["totalCount"],
        "top_repo_stars": sum(n["stargazerCount"] for n in d["topRepositories"]["nodes"]),
        "approx_loc": int(approx_loc),
        "age_years": int((dt.datetime.utcnow() - BIRTHDAY).days // 365),
        "top_langs": [{"name": k, "pct": round(v * 100 / total_lang_bytes, 1)} for k, v in top_langs],
    }
    return stats

def _update_svg(svg_path: Path, stats: Dict[str, Any]) -> None:
    """
    Update text nodes by matching data-stat attributes.
    Example in SVG:
      <text id="commits" data-stat="commits_year">0</text>
      <text id="followers" data-stat="followers">0</text>
    For top languages (optional):
      <text data-stat="lang_1">Python 45%</text> ... up to lang_5
    """
    parser = etree.XMLParser(remove_comments=False)
    root = etree.parse(str(svg_path), parser)

    # Fill simple numeric/name fields
    for el in root.xpath('//*[@data-stat]'):
        key = el.attrib.get("data-stat")
        if key.startswith("lang_"):
            # lang_1 .. lang_5
            try:
                idx = int(key.split("_")[1]) - 1
                if idx < len(stats["top_langs"]):
                    li = stats["top_langs"][idx]
                    el.text = f"{li['name']} {li['pct']}%"
                else:
                    el.text = ""
            except Exception:
                pass
        else:
            if key in stats:
                el.text = f"{stats[key]}"

    # Optional: write a generated-on comment block for debugging/versioning
    comment = etree.Comment(f"generated {dt.datetime.utcnow().isoformat(timespec='seconds')}Z")
    if COMMENT_SIZE:
        root.getroot().append(comment)

    svg_path.write_bytes(etree.tostring(root, xml_declaration=True, encoding="UTF-8"))

def main():
    if not HEADERS:
        raise SystemExit("Missing GH_TOKEN/GITHUB_TOKEN for API access.")
    stats = get_user_stats(USER_NAME)
    for f in SVG_FILES:
        p = Path(f)
        if p.exists():
            _update_svg(p, stats)
        else:
            print(f"[warn] {p} not found, skipping")
    # If you also rewrite README.md badges/text, you can add that here.

if __name__ == "__main__":
    main()
