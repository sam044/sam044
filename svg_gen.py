from __future__ import annotations
import os
import requests
from lxml import etree

# ── Config / Secrets ─────────────────────────────────────────
USER_NAME: str = os.getenv("USER_NAME", "sam044")
TOKEN = os.getenv("ACCESS_TOKEN")
if not TOKEN:
    raise RuntimeError("ACCESS_TOKEN missing. Add it in Settings → Secrets and variables → Actions.")

HEADERS = {"authorization": f"Bearer {TOKEN}"}
GQL_URL = "https://api.github.com/graphql"

SVG_FILES = ["banner.svg"]   # only update your single banner
# If you also keep light/dark variants later, add them here.

# ── Helpers (Alan-style) ─────────────────────────────────────
def simple_request(fname: str, q: str, v: dict):
    r = requests.post(GQL_URL, json={"query": q, "variables": v}, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        payload = r.json()
        if "errors" in payload:
            raise RuntimeError(f"{fname} failed (GraphQL): {payload['errors']}")
        return payload
    raise RuntimeError(f"{fname} failed → {r.status_code}: {r.text}")

def find_and_replace(root, element_id: str, new_text: str):
    el = root.find(f".//*[@id='{element_id}']")
    if el is None:
        return
    el.text = str(new_text)
    # Keep original x alignment (Alan trick)
    parent_x = el.getparent().get("x")
    if parent_x:
        el.set("x", parent_x)

def justify_format(root, eid: str, new_text, length: int = 0):
    """Writes value and adjusts dot filler length for alignment (like Alan)."""
    if isinstance(new_text, int):
        new_text = f"{new_text:,}"
    find_and_replace(root, eid, new_text)
    just_len = max(0, length - len(str(new_text)))
    dot_map = {0: "", 1: " ", 2: ". "}
    dot_string = dot_map.get(just_len, " " + "." * just_len + " ")
    find_and_replace(root, f"{eid}_dots", dot_string)

# ── GraphQL data fetchers (stars/repos/commits/followers/contrib) ─────────────
def follower_getter(username: str) -> int:
    q = """
    query($login:String!){
      user(login:$login){
        followers { totalCount }
      }
    }"""
    return int(simple_request("follower_getter", q, {"login": username})["data"]["user"]["followers"]["totalCount"])

def total_owned_repos(username: str) -> int:
    q = """
    query($login:String!){
      user(login:$login){
        repositories(ownerAffiliations: OWNER, isFork:false) { totalCount }
      }
    }"""
    return int(simple_request("total_owned_repos", q, {"login": username})["data"]["user"]["repositories"]["totalCount"])

def total_stars_owned_repos(username: str) -> int:
    q = """
    query($login:String!, $cursor:String){
      user(login:$login){
        repositories(first:100, after:$cursor, ownerAffiliations: OWNER, isFork:false){
          pageInfo { hasNextPage endCursor }
          nodes { stargazers { totalCount } }
        }
      }
    }"""
    total = 0
    cursor = None
    while True:
        data = simple_request("total_stars_owned_repos", q, {"login": username, "cursor": cursor})["data"]["user"]["repositories"]
        total += sum(int(n["stargazers"]["totalCount"]) for n in data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]
    return total

def commits_last_year(username: str) -> int:
    q = """
    query($login:String!){
      user(login:$login){
        contributionsCollection {
          totalCommitContributions
        }
      }
    }"""
    return int(simple_request("commits_last_year", q, {"login": username})["data"]["user"]["contributionsCollection"]["totalCommitContributions"])

def contributed_repos_count(username: str) -> int:
    # repos the user has contributed to in the last year (non-owners also)
    q = """
    query($login:String!, $cursor:String){
      user(login:$login){
        repositoriesContributedTo(first:100, after:$cursor, includeUserRepositories:false, contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]){
          pageInfo { hasNextPage endCursor }
          totalCount
        }
      }
    }"""
    # totalCount is available at the first page; still loop for safety if needed later
    data = simple_request("contributed_repos_count", q, {"login": username, "cursor": None})["data"]["user"]["repositoriesContributedTo"]
    return int(data["totalCount"])

# ── Main: update ONLY stats fields in the SVG ─────────────────────────────────
if __name__ == "__main__":
    # Pull live stats
    followers = follower_getter(USER_NAME)
    repos     = total_owned_repos(USER_NAME)
    stars     = total_stars_owned_repos(USER_NAME)
    commits   = commits_last_year(USER_NAME)
    contrib   = contributed_repos_count(USER_NAME)

    # Write into each SVG template listed
    for svg in SVG_FILES:
        tree = etree.parse(svg); root = tree.getroot()
        # These IDs must exist in your SVG (they do in Alan's template):
        # repo_data / repo_data_dots
        # star_data / star_data_dots
        # commit_data / commit_data_dots
        # follower_data / follower_data_dots
        # contrib_data  (no dots id in Alan’s sample—add one if you want)
        justify_format(root, "repo_data",    repos,   6)
        justify_format(root, "star_data",    stars,   14)
        justify_format(root, "commit_data",  commits, 22)
        justify_format(root, "follower_data",followers,10)
        find_and_replace(root, "contrib_data", f"{contrib}")

        tree.write(svg, encoding="utf-8", xml_declaration=True)

    print("✅ banner.svg updated (repos/stars/commits/followers/contributed)")
