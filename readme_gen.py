"""
"""

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
# │  Utility helpers (Alan-style)   │
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
    parent_x = el.getparent().get("x")
    if parent_x: el.set("x", parent_x)

def justify_format(root, eid, new_text, length=0):
    if isinstance(new_text, int): new_text = f"{new_text:,}"
    find_and_replace(root, eid, new_text)
    just_len = max(0, length - len(str(new_text)))
    dot_map = {0:'', 1:' ', 2:'. '}
    dot_string = dot_map.get(just_len, ' ' + '.'*just_len + ' ')
    find_and_replace(root, f"{eid}_dots", dot_string)

def svg_overwrite(fname, *vals):
    # Order matches Alan’s usage:
    # age, commits, stars, repos, contributed, followers, loc_tuple
    age, comm, star, repo, contrib, follow, loc = vals
    tree = etree.parse(fname); root
