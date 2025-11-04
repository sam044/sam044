"""
Sam Flynn — Automated GitHub Profile Banner
────────────────────────────────────────────────────────────
• Pulls live GitHub stats via GraphQL v4
• Rewrites banner.svg in-place with dotted alignment
• Minimal, single-banner adaptation of Alan's system
"""

from __future__ import annotations
import os, requests
from lxml import etree

# ──────────────────────────────────────
#  ░░ CONFIG ░░
# ──────────────────────────────────────
USER_NAME = os.getenv("USER_NAME", "sam044")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise RuntimeError("Missing ACCESS_TOKEN. Add it under repo → Settings → Secrets → Actions.")
HEADERS = {"authorization": f"Bearer {ACCESS_TOKEN}"}
GRAPHQL_URL = "https://api.github.com/graphql"
SVG_FILE = "banner.svg"

# ──────────────────────────────────────
#  ░░ HELPERS ░░
# ──────────────────────────────────────
def simple_request(name: str, query: str, variables: dict) -> dict:
    r = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables},
                      headers=HEADERS, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"{name} failed ({r.status_code}): {r.text}")
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"{name} error: {data['errors']}")
    return data["data"]

def find_and_replace(root, eid: str, new_text: str):
    el = root.find(f".//*[@id='{eid}']")
    if el is None:
        return
    el.text = str(new_text)
    # keep same x alignment (Alan-style)
    parent_x = el.getparent().get("x")
    if parent_x:
        el.set("x", parent_x)

def justify_format(root, eid: str, new_text, length: int = 0):
    """Writes value and adjusts filler dot length for alignment (Alan-style)."""
    if isinstance(new_text, int):
        new_text = f"{new_text:,}"
    find_and_replace(root, eid, new_text)
    just_len = max(0, length - len(str(new_text)))
    dot_map = {0: "", 1: " ", 2: ". "}
    dot_string = dot_map.get(just_len, " " + "." * just_len + " ")
    find_and_replace(root, f"{eid}_dots", dot_string)

# ──────────────────────────────────────
#  ░░ DATA FETCHERS ░░
# ──────────────────────────────────────
def follower_count(username: str) -> int:
    q = """query($login:String!){user(login:$login){followers{totalCount}}}"""
    d = simple_request("followers", q, {"login": username})
    return d["user"]["followers"]["totalCount"]

def repo_count(username: str) -> int:
    q = """query($login:String!){user(login:$login){
      repositories(ownerAffiliations: OWNER, isFork:false){totalCount}}}"""
    d = simple_request("repos", q, {"login": username})
    return d["user"]["repositories"]["totalCount"]

def star_count(username: str) -> int:
    q = """query($login:String!, $cursor:String){
      user(login:$login){
        repositories(first:100, after:$cursor, ownerAffiliations: OWNER, isFork:false){
          nodes{stargazers{totalCount}}
          pageInfo{hasNextPage endCursor}
        }}}"""
    total, cursor = 0, None
    while True:
        d = simple_request("stars", q, {"login": username, "cursor": cursor})
        repos = d["user"]["repositories"]
        total += sum(r["stargazers"]["totalCount"] for r in repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    return total

def commit_count(username: str) -> int:
    q = """query($login:String!){user(login:$login){
      contributionsCollection{totalCommitContributions}}}"""
    d = simple_request("commits", q, {"login": username})
    return d["user"]["contributionsCollection"]["totalCommitContributions"]

# ──────────────────────────────────────
#  ░░ MAIN ░░
# ──────────────────────────────────────
if __name__ == "__main__":
    print("Updating banner.svg with live GitHub stats...")

    followers = follower_count(USER_NAME)
    repos = repo_count(USER_NAME)
    stars = star_count(USER_NAME)
    commits = commit_count(USER_NAME)

    # load your existing SVG
    tree = etree.parse(SVG_FILE)
    root = tree.getroot()

    # replace numeric data — add filler IDs in your SVG for style if desired
    justify_format(root, "repo_data", repos, 6)
    justify_format(root, "star_data", stars, 14)
    justify_format(root, "commit_data", commits, 22)
    justify_format(root, "follower_data", followers, 10)

    tree.write(SVG_FILE, encoding="utf-8", xml_declaration=True)
    print("✅ banner.svg updated successfully.")
