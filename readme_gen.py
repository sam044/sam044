from __future__ import annotations
import datetime
import os
import time
from pathlib import Path

import requests
from dateutil import relativedelta
from lxml import etree

# ──────────────────────────────────────
#  ░░ USER CONFIG 
# ──────────────────────────────────────
USER_NAME: str = os.getenv("USER_NAME", "sam044")
BIRTHDAY  = datetime.datetime(2004, 4, 4)     # used for "Uptime" / Age line if present
SVG_FILES = ["banner.svg"]                   # single dark banner
CACHE_DIR = Path("cache"); CACHE_DIR.mkdir(exist_ok=True)
COMMENT_SIZE = 7

HEADERS = {"authorization": "token " + os.environ["ACCESS_TOKEN"]}

# ──────────────────────────────────────
#  INTERNAL COUNTERS (debug timing)
# ──────────────────────────────────────
QUERY_COUNT = {k: 0 for k in [
    "user_getter", "follower_getter",
    "graph_repos_stars", "commits_last_year",
    "contributed_repos_count"
]}

# ╭──────────────────────────────────╮
# │  Utility helpers  │
# ╰──────────────────────────────────╯
def uptime_string(bday: datetime.datetime) -> str:
    diff = relativedelta.relativedelta(datetime.datetime.utcnow(), bday)
    return f"{diff.years} year{'s'*(diff.years!=1)}, {diff.months} month{'s'*(diff.months!=1)}, {diff.days} day{'s'*(diff.days!=1)}"

def perf_counter(fn, *args):
    start = time.perf_counter(); out = fn(*args)
    return out, time.perf_counter() - start

def formatter(lbl: str, dt: float):
    print(f"   {lbl:<22}: {dt*1000:>8.2f} ms" if dt<1 else f"   {lbl:<22}: {dt:>8.2f} s ")

def query_count(k: str): QUERY_COUNT[k] += 1

def simple_request(fname: str, q: str, v: dict):
    r = requests.post("https://api.github.com/graphql",
                      json={"query": q, "variables": v},
                      headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        if "errors" in data:
            raise RuntimeError(f"{fname} failed (GraphQL): {data['errors']}")
        return data
    raise RuntimeError(f"{fname} failed → {r.status_code}: {r.text}")

# ╭──────────────────────────────────╮
# │  SVG helpers (IDs must match)    │
# ╰──────────────────────────────────╯
def find_and_replace(root, element_id: str, new_text: str):
    el = root.find(f".//*[@id='{element_id}']")
    if el is None: return
    el.text = str(new_text)
    # Removed setting x attribute to prevent text overlap
    # parent_x = el.getparent().get("x")
    # if parent_x: el.set("x", parent_x)

def justify_format(root, eid, new_text, length=0):
    if isinstance(new_text, int): new_text = f"{new_text:,}"
    find_and_replace(root, eid, new_text)
    # Removed dot generation - dots no longer needed
    # just_len = max(0, length - len(str(new_text)))
    # dot_map = {0:'', 1:' ', 2:'. '}
    # dot_string = dot_map.get(just_len, ' ' + '.'*just_len + ' ')
    # find_and_replace(root, f"{eid}_dots", dot_string)

def svg_overwrite(fname, *vals):
    # Order matches aaa’s usage:
    # age, commits, stars, repos, contributed, followers, loc_tuple
    age, comm, star, repo, contrib, follow, loc = vals
    tree = etree.parse(fname); root = tree.getroot()
    # Optional age (if your SVG has id="age_data" and "age_data_dots")
    justify_format(root, 'age_data', age)
    justify_format(root, 'commit_data',   comm,   22)
    justify_format(root, 'star_data',     star,   14)
    justify_format(root, 'repo_data',     repo,    6)
    justify_format(root, 'contrib_data',  contrib)
    justify_format(root, 'follower_data', follow, 10)
    # LOC placeholders (aaa’s SVG shows these IDs; keep zeros if you don’t render them)
    justify_format(root, 'loc_data', loc[2], 9)
    justify_format(root, 'loc_add',  loc[0])
    justify_format(root, 'loc_del',  loc[1], 7)
    tree.write(fname, encoding='utf-8', xml_declaration=True)

# ╭──────────────────────────────────╮
# │  GraphQL helpers (exact names)   │
# ╰──────────────────────────────────╯
def user_getter(username: str):
    query_count('user_getter')
    q = """query($login:String!){ user(login:$login){ id createdAt }}"""
    data = simple_request('user_getter', q, {"login": username})["data"]["user"]
    return {"id": data['id']}, data['createdAt']

def follower_getter(username: str) -> int:
    query_count('follower_getter')
    q = """query($login:String!){ user(login:$login){ followers{ totalCount }}}"""
    return int(simple_request('follower_getter', q, {"login": username})["data"]["user"]["followers"]["totalCount"])

def graph_repos_stars(kind: str, aff: list[str], cursor=None):
    query_count('graph_repos_stars')
    q = """query($owner_affiliation:[RepositoryAffiliation],$login:String!,$cursor:String){
      user(login:$login){
        repositories(first:100, after:$cursor, ownerAffiliations:$owner_affiliation, isFork:false){
          totalCount
          edges{ node{ stargazers{ totalCount } } }
          pageInfo{ endCursor hasNextPage }
        }
      }}"""
    vars = {"owner_affiliation": aff, "login": USER_NAME, "cursor": cursor}
    r = simple_request('graph_repos_stars', q, vars)["data"]["user"]["repositories"]
    if kind == 'repos':
        # Follow next pages to be exact for stars; totalCount is included here already
        return r["totalCount"]
    # Sum stars across all pages
    stars = sum(e["node"]["stargazers"]["totalCount"] for e in r["edges"])
    while r["pageInfo"]["hasNextPage"]:
        vars["cursor"] = r["pageInfo"]["endCursor"]
        r = simple_request('graph_repos_stars', q, vars)["data"]["user"]["repositories"]
        stars += sum(e["node"]["stargazers"]["totalCount"] for e in r["edges"])
    return stars

def commits_last_year(username: str) -> int:
    query_count('commits_last_year')
    q = """query($login:String!){
      user(login:$login){ contributionsCollection { totalCommitContributions }}}"""
    return int(simple_request('commits_last_year', q, {"login": username})["data"]["user"]["contributionsCollection"]["totalCommitContributions"])

def contributed_repos_count(username: str) -> int:
    query_count('contributed_repos_count')
    q = """query($login:String!, $cursor:String){
      user(login:$login){
        repositoriesContributedTo(first:100, after:$cursor, includeUserRepositories:false,
          contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]){
          pageInfo { hasNextPage endCursor }
          totalCount
        }}}"""
    r = simple_request('contributed_repos_count', q, {"login": username, "cursor": None})["data"]["user"]["repositoriesContributedTo"]
    return int(r["totalCount"])

# ╭──────────────────────────────────╮
# │  Main (matches aaa’s flow)     │
# ╰──────────────────────────────────╯
if __name__ == '__main__':
    print('Calculation times:')
    (user_data, acc_date), t_user = perf_counter(user_getter, USER_NAME)
    formatter('account data', t_user)
    age_str, t_age = perf_counter(uptime_string, BIRTHDAY)
    formatter('age calculation', t_age)

    # Stars & repos via the same helper
    star_data = graph_repos_stars('stars', ["OWNER"])
    repo_data = graph_repos_stars('repos', ["OWNER"])

    contrib_data = contributed_repos_count(USER_NAME)
    follower_data = follower_getter(USER_NAME)
    commit_data = commits_last_year(USER_NAME)

    # LOC not implemented here (same as aaa’s public script baseline)
    loc_total = ['0', '0', '0']  # add real LOC later if you want

    for svg in SVG_FILES:
        svg_overwrite(svg, age_str, commit_data, star_data, repo_data, contrib_data, follower_data, loc_total)

    print('Total GraphQL calls:', sum(QUERY_COUNT.values()))
