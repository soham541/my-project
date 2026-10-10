#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "User-Agent": "GitRank-CLI",
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def github_request(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def search_repos(query, per_page=10):
    q = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={per_page}"
    data = github_request(url)
    return data.get("items", [])


def main():
    parser = argparse.ArgumentParser(description="Search and fetch GitHub repositories manually.")
    parser.add_argument("query", nargs="?", default="stars:>1000", help="GitHub search query")
    parser.add_argument("--limit", type=int, default=10, help="Number of repos to fetch")
    parser.add_argument("--save", help="Optional JSON file to save results")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")
    args = parser.parse_args()

    try:
        items = search_repos(args.query, per_page=args.limit)
    except Exception as exc:
        print(f"Error fetching GitHub repos: {exc}")
        sys.exit(1)

    results = []
    for item in items:
        results.append({
            "fullName": item.get("full_name"),
            "name": item.get("name"),
            "owner": (item.get("owner") or {}).get("login"),
            "stars": item.get("stargazers_count"),
            "forks": item.get("forks_count"),
            "language": item.get("language"),
            "description": item.get("description"),
            "url": item.get("html_url"),
            "homepage": item.get("homepage"),
        })

    if args.pretty:
        print(json.dumps(results, indent=2))
    else:
        for repo in results:
            print(f"{repo['fullName']} | ⭐ {repo['stars']} | 🔀 {repo['forks']} | {repo['language'] or 'Unknown'}")

    if args.save:
        with open(args.save, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"\nSaved {len(results)} repos to {args.save}")


if __name__ == "__main__":
    main()
