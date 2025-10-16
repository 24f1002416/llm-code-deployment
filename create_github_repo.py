"""
Create GitHub repository using the GitHub API
"""
import os
import json
try:
    import httpx
    has_httpx = True
except ImportError:
    has_httpx = False
    try:
        import urllib.request
        import urllib.parse
    except ImportError:
        print("Error: No HTTP library available")
        exit(1)

# Load from environment or replace with your values
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "your-github-token-here")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "your-github-username")

def create_repo_httpx():
    """Create repository using httpx"""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": "llm-code-deployment",
        "description": "LLM Code Deployment API for IIT Madras TDS Project - Automated web app generation using Claude AI",
        "private": False
    }

    with httpx.Client() as client:
        response = client.post(url, json=data, headers=headers)

    if response.status_code == 201:
        repo_info = response.json()
        print("SUCCESS: Repository created successfully!")
        print(f"Repo URL: {repo_info['html_url']}")
        print(f"Clone URL: {repo_info['clone_url']}")
        return repo_info['clone_url']
    elif response.status_code == 422:
        print("WARNING: Repository 'llm-code-deployment' already exists")
        return f"https://github.com/{GITHUB_USERNAME}/llm-code-deployment.git"
    else:
        print(f"ERROR: Error creating repository: {response.status_code}")
        print(response.text)
        return None

def create_repo_urllib():
    """Create repository using urllib"""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    data = {
        "name": "llm-code-deployment",
        "description": "LLM Code Deployment API for IIT Madras TDS Project - Automated web app generation using Claude AI",
        "private": False
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as response:
            repo_info = json.loads(response.read().decode('utf-8'))
            print("SUCCESS: Repository created successfully!")
            print(f"Repo URL: {repo_info['html_url']}")
            print(f"Clone URL: {repo_info['clone_url']}")
            return repo_info['clone_url']
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print("WARNING: Repository 'llm-code-deployment' already exists")
            return f"https://github.com/{GITHUB_USERNAME}/llm-code-deployment.git"
        else:
            print(f"ERROR: Error creating repository: {e.code}")
            print(e.read().decode('utf-8'))
            return None

if __name__ == "__main__":
    print("Creating GitHub repository...")
    print()

    if has_httpx:
        print("Using httpx library...")
        clone_url = create_repo_httpx()
    else:
        print("Using urllib library...")
        clone_url = create_repo_urllib()

    if clone_url:
        print()
        print("Next steps:")
        print(f"1. git remote add origin {clone_url}")
        print("2. git push -u origin main")
    else:
        print()
        print("Manual steps:")
        print("1. Go to https://github.com/new")
        print("2. Repository name: llm-code-deployment")
        print("3. Description: LLM Code Deployment API for IIT Madras TDS Project")
        print("4. Make it Public")
        print("5. Don't initialize with README (we already have code)")
        print("6. Create repository")
        print(f"7. git remote add origin https://github.com/{GITHUB_USERNAME}/llm-code-deployment.git")
        print("8. git push -u origin main")
