import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "User-Agent": "GitRank-Bot",
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

CATEGORIES = {
    "ai-ml": {
        "query": "stars:>10000 machine learning OR llm OR deep-learning OR ai",
        "categoryName": "AI & Machine Learning",
        "limit": 10,
    },
    "web": {
        "query": "stars:>10000 react OR vue OR frontend OR javascript OR typescript",
        "categoryName": "Web Development",
        "limit": 10,
    },
    "devops": {
        "query": "stars:>8000 docker OR kubernetes OR devops OR cloud-native",
        "categoryName": "DevOps & Cloud Native",
        "limit": 8,
    },
    "databases": {
        "query": "stars:>5000 database OR vector-database OR analytics OR postgres",
        "categoryName": "Databases & Storage",
        "limit": 8,
    },
    "security": {
        "query": "stars:>4000 security OR pentesting OR cybersecurity OR vulnerability",
        "categoryName": "Cyber Security",
        "limit": 8,
    },
    "mobile": {
        "query": "stars:>5000 mobile OR flutter OR react-native OR cross-platform",
        "categoryName": "Mobile & Cross-Platform",
        "limit": 8,
    },
    "systems": {
        "query": "stars:>5000 rust OR go OR linux OR systems-programming",
        "categoryName": "Systems & Languages",
        "limit": 8,
    },
    "alternatives": {
        "query": "stars:>3000 self-hosted OR firebase-alternative OR open-source-alternative",
        "categoryName": "Open Source Alternatives",
        "limit": 8,
    },
    "trending": {
        "query": "stars:>500 created:>2024-01-01",
        "categoryName": "Trending & Hot",
        "limit": 12,
    },
}


def github_request(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def normalize_repo(item, category, category_name):
    name = item.get("name") or "repository"
    owner = (item.get("owner") or {}).get("login") or "unknown"
    full_name = item.get("full_name") or f"{owner}/{name}"
    language = item.get("language") or "JavaScript"
    description = (item.get("description") or "").strip() or "A popular open-source project."
    homepage = item.get("homepage") or ""
    repo_id = item.get("id")

    return {
        "id": f"{owner}-{name}-{repo_id}",
        "name": name,
        "owner": owner,
        "fullName": full_name,
        "stars": int(item.get("stargazers_count") or 0),
        "forks": int(item.get("forks_count") or 0),
        "language": language,
        "category": category,
        "categoryName": category_name,
        "description": description[:220],
        "topics": [],
        "license": (item.get("license") or {}).get("name") or "MIT",
        "githubUrl": item.get("html_url") or f"https://github.com/{full_name}",
        "homepageUrl": homepage,
        "cloneUrl": item.get("clone_url") or f"https://github.com/{full_name}.git",
        "weeklyGrowth": estimate_weekly_growth(item.get("pushed_at")),
        "trendingRank": 0,
        "isSponsored": False,
        "readmeSnippet": f"git clone {item.get('clone_url') or f'https://github.com/{full_name}.git'}\ncd {name}",
        "globalRank": 0,
    }


def estimate_weekly_growth(pushed_at):
    if not pushed_at:
        return "+500/wk"
    try:
        dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        delta_days = (datetime.now(dt.tzinfo) - dt).days
        if delta_days < 7:
            return "+2,500/wk"
        if delta_days < 30:
            return "+1,200/wk"
        if delta_days < 90:
            return "+700/wk"
        return "+300/wk"
    except Exception:
        return "+500/wk"


def fetch_repos_for_category(category, config):
    query = urllib.parse.quote(config["query"])
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={config['limit']}"
    try:
        payload = github_request(url)
        items = payload.get("items", [])
        return [normalize_repo(item, category, config["categoryName"]) for item in items]
    except Exception as exc:
        print(f"[WARN] Failed to fetch category {category}: {exc}")
        return []


def apply_global_ranking(repos):
    ranked = sorted(repos, key=lambda r: r["stars"], reverse=True)
    for index, repo in enumerate(ranked, start=1):
        repo["globalRank"] = index
    return ranked


def dedupe_repos(repos):
    seen = {}
    result = []
    for repo in repos:
        key = repo["fullName"].lower()
        if key not in seen:
            seen[key] = repo
            result.append(repo)
        elif repo["stars"] > seen[key]["stars"]:
            for idx, existing in enumerate(result):
                if existing["fullName"].lower() == key:
                    result[idx] = repo
                    seen[key] = repo
                    break
    return result


def update_script_js(repos):
    json_blob = json.dumps(repos, indent=2)
    target_file = "script.js"

    with open(target_file, "r", encoding="utf-8") as fh:
        content = fh.read()

    pattern = r"// Injected repository dataset\s*const reposData = \[[\s\S]*?\];"
    new_block = f"// Injected repository dataset\nconst reposData = {json_blob};"
    updated = re.sub(pattern, new_block, content, count=1)

    if updated == content:
        raise RuntimeError("Could not find reposData block in script.js")

    with open(target_file, "w", encoding="utf-8") as fh:
        fh.write(updated)

    print(f"Updated {target_file} with {len(repos)} repositories.")


def main():
    print("GitRank: fetching repository data from GitHub API...")

    repo_list = []
    for category, config in CATEGORIES.items():
        repos = fetch_repos_for_category(category, config)
        repo_list.extend(repos)
        print(f"Fetched {category}: {len(repos)} repositories")

    repo_list = dedupe_repos(repo_list)
    repo_list = apply_global_ranking(repo_list)

    for index, repo in enumerate(repo_list[:10], start=1):
        print(f"#{index} {repo['fullName']} - {repo['stars']} stars")

    try:
        update_script_js(repo_list)
    except Exception as exc:
        print(f"[WARN] script.js update failed: {exc}")
        fallback_path = "repos_data.json"
        with open(fallback_path, "w", encoding="utf-8") as fh:
            json.dump(repo_list, fh, indent=2)
        print(f"Fallback data saved to {fallback_path}")

    print(f"Final total: {len(repo_list)} repositories")


if __name__ == "__main__":
    main()
