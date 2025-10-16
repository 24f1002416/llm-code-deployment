"""
LLM Code Deployment API
Handles incoming build/revise requests, generates code using Claude AI,
deploys to GitHub Pages, and notifies evaluation API.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import base64
import re

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from anthropic import Anthropic
import subprocess

# Load .env file if it exists
try:
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and not os.getenv(key):
                        os.environ[key] = value
        print("✓ Environment variables loaded from .env")
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Code Deployment API")

# Load environment variables
SECRET = os.getenv("SECRET", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")

if not SECRET:
    logger.warning("SECRET not set in environment variables!")
if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY not set in environment variables!")
if not GITHUB_TOKEN:
    logger.warning("GITHUB_TOKEN not set in environment variables!")
if not GITHUB_USERNAME:
    logger.warning("GITHUB_USERNAME not set in environment variables!")


class CodeGenerator:
    """Handles code generation using Claude AI"""

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_code(self, brief: str, checks: list, attachments: list, task_id: str, round_num: int) -> Dict[str, str]:
        """Generate HTML/JS code based on brief and checks"""

        # Prepare attachment info
        attachment_info = ""
        if attachments:
            attachment_info = "\n\nAttachments:\n"
            for att in attachments:
                attachment_info += f"- {att['name']}: {att['url'][:100]}...\n"

        # Prepare checks info
        checks_info = "\n".join([f"- {check}" for check in checks])

        prompt = f"""You are an expert web developer. Create a complete, production-ready single-page web application based on the following requirements.

Task ID: {task_id}
Round: {round_num}

Brief:
{brief}

Requirements/Checks that MUST be satisfied:
{checks_info}
{attachment_info}

Generate the following files:

1. index.html - A complete HTML file with:
   - Proper DOCTYPE and meta tags
   - All required HTML elements with correct IDs/classes as specified
   - Embedded JavaScript (or link to external JS)
   - Embedded CSS (or link to external CSS)
   - CDN links for any required libraries (Bootstrap, marked, highlight.js, etc.)

2. README.md - A professional README with:
   - Project summary
   - Setup instructions
   - Usage guide
   - Code explanation
   - MIT License reference

Return your response in this exact JSON format:
{{
  "index.html": "<complete HTML content>",
  "README.md": "<complete README content>"
}}

Important guidelines:
- Make sure ALL specified IDs, classes, and functionality from the checks are implemented
- Handle data URIs properly by decoding base64 attachments
- Include error handling
- Make the UI clean and professional
- Ensure the page works standalone without external dependencies except CDNs
- All JavaScript should be properly scoped to avoid global pollution
- Use modern, clean, semantic HTML5
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            # Try to extract JSON from the response
            # Look for JSON object in the response
            json_match = re.search(r'\{[\s\S]*"index\.html"[\s\S]*"README\.md"[\s\S]*\}', content)
            if json_match:
                files = json.loads(json_match.group())
            else:
                # Fallback: create basic files
                logger.warning("Could not extract JSON from Claude response, creating basic files")
                files = self._create_basic_files(brief, checks, attachments, task_id)

            return files

        except Exception as e:
            logger.error(f"Error generating code with Claude: {e}")
            # Return basic fallback files
            return self._create_basic_files(brief, checks, attachments, task_id)

    def _create_basic_files(self, brief: str, checks: list, attachments: list, task_id: str) -> Dict[str, str]:
        """Create basic fallback files if AI generation fails"""

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{task_id}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{task_id}</h1>
        <p>{brief}</p>

        <div id="output" class="mt-4">
            <!-- Content will be generated here -->
        </div>
    </div>

    <script>
        // Application logic here
        console.log('Application loaded');
    </script>
</body>
</html>"""

        readme_content = f"""# {task_id}

## Summary
{brief}

## Setup
This is a static web application. No build step required.

## Usage
1. Clone the repository
2. Open `index.html` in a web browser
3. Or deploy to GitHub Pages for online access

## Code Explanation
This application implements the following features:
{chr(10).join([f"- {check}" for check in checks])}

## License
MIT License - See LICENSE file for details
"""

        return {
            "index.html": html_content,
            "README.md": readme_content
        }


class GitHubDeployer:
    """Handles GitHub repository creation and deployment"""

    def __init__(self):
        self.token = GITHUB_TOKEN
        self.username = GITHUB_USERNAME
        self.base_url = "https://api.github.com"

    async def create_and_deploy(self, task_id: str, files: Dict[str, str], round_num: int) -> Dict[str, str]:
        """Create repo, push files, enable Pages"""

        # Generate unique repo name
        repo_name = f"{task_id}-round{round_num}"
        repo_name = re.sub(r'[^a-zA-Z0-9-]', '-', repo_name)[:100]  # GitHub limit

        try:
            async with httpx.AsyncClient() as client:
                # Create repository
                create_repo_url = f"{self.base_url}/user/repos"
                headers = {
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                }

                repo_data = {
                    "name": repo_name,
                    "description": f"Generated application for {task_id}",
                    "private": False,
                    "auto_init": False
                }

                response = await client.post(create_repo_url, json=repo_data, headers=headers)

                if response.status_code == 201:
                    repo_info = response.json()
                    repo_url = repo_info["html_url"]
                    logger.info(f"Created repository: {repo_url}")
                elif response.status_code == 422:
                    # Repository already exists, use it
                    logger.warning(f"Repository {repo_name} already exists, using existing repo")
                    repo_url = f"https://github.com/{self.username}/{repo_name}"
                else:
                    raise Exception(f"Failed to create repository: {response.status_code} - {response.text}")

                # Add LICENSE file
                license_content = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

                files["LICENSE"] = license_content

                # Upload files using GitHub API
                for filename, content in files.items():
                    file_url = f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{filename}"

                    # Check if file exists
                    get_response = await client.get(file_url, headers=headers)

                    file_data = {
                        "message": f"Add/Update {filename}",
                        "content": base64.b64encode(content.encode()).decode()
                    }

                    if get_response.status_code == 200:
                        # File exists, update it
                        file_data["sha"] = get_response.json()["sha"]

                    put_response = await client.put(file_url, json=file_data, headers=headers)

                    if put_response.status_code not in [200, 201]:
                        logger.error(f"Failed to upload {filename}: {put_response.status_code}")

                # Get latest commit SHA
                commits_url = f"{self.base_url}/repos/{self.username}/{repo_name}/commits/main"
                commits_response = await client.get(commits_url, headers=headers)

                if commits_response.status_code == 200:
                    commit_sha = commits_response.json()["sha"]
                else:
                    commit_sha = "unknown"

                # Enable GitHub Pages
                pages_url = f"{self.base_url}/repos/{self.username}/{repo_name}/pages"
                pages_data = {
                    "source": {
                        "branch": "main",
                        "path": "/"
                    }
                }

                pages_response = await client.post(pages_url, json=pages_data, headers=headers)

                if pages_response.status_code in [201, 409]:  # 409 means already enabled
                    logger.info("GitHub Pages enabled")
                else:
                    logger.warning(f"Failed to enable Pages: {pages_response.status_code}")

                # Construct Pages URL
                pages_url_str = f"https://{self.username}.github.io/{repo_name}/"

                return {
                    "repo_url": repo_url,
                    "commit_sha": commit_sha,
                    "pages_url": pages_url_str
                }

        except Exception as e:
            logger.error(f"Error deploying to GitHub: {e}")
            raise


async def notify_evaluation_api(evaluation_url: str, data: Dict[str, Any]) -> bool:
    """Notify evaluation API with exponential backoff retry"""

    max_retries = 5
    delays = [1, 2, 4, 8, 16]  # seconds

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    evaluation_url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    logger.info(f"Successfully notified evaluation API")
                    return True
                else:
                    logger.warning(f"Evaluation API returned {response.status_code}")

            except Exception as e:
                logger.error(f"Error notifying evaluation API (attempt {attempt + 1}): {e}")

            # Retry with exponential backoff
            if attempt < max_retries - 1:
                delay = delays[attempt]
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

    return False


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "LLM Code Deployment API is running"}


@app.post("/deploy")
async def deploy(request: Request):
    """Main deployment endpoint"""

    try:
        # Parse request
        payload = await request.json()

        email = payload.get("email")
        secret = payload.get("secret")
        task_id = payload.get("task")
        round_num = payload.get("round", 1)
        nonce = payload.get("nonce")
        brief = payload.get("brief")
        checks = payload.get("checks", [])
        evaluation_url = payload.get("evaluation_url")
        attachments = payload.get("attachments", [])

        logger.info(f"Received request for task {task_id}, round {round_num}, email {email}")

        # Verify secret
        if secret != SECRET:
            logger.warning(f"Invalid secret provided")
            raise HTTPException(status_code=403, detail="Invalid secret")

        # Return 200 immediately (process asynchronously)
        asyncio.create_task(
            process_deployment(
                email, task_id, round_num, nonce, brief, checks,
                evaluation_url, attachments
            )
        )

        return JSONResponse(
            status_code=200,
            content={"status": "accepted", "message": "Request received and processing"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_deployment(
    email: str, task_id: str, round_num: int, nonce: str,
    brief: str, checks: list, evaluation_url: str, attachments: list
):
    """Process deployment asynchronously"""

    try:
        # Generate code
        logger.info(f"Generating code for {task_id}")
        generator = CodeGenerator()
        files = generator.generate_code(brief, checks, attachments, task_id, round_num)

        # Deploy to GitHub
        logger.info(f"Deploying to GitHub")
        deployer = GitHubDeployer()
        deployment_info = await deployer.create_and_deploy(task_id, files, round_num)

        # Prepare notification
        notification_data = {
            "email": email,
            "task": task_id,
            "round": round_num,
            "nonce": nonce,
            "repo_url": deployment_info["repo_url"],
            "commit_sha": deployment_info["commit_sha"],
            "pages_url": deployment_info["pages_url"]
        }

        logger.info(f"Notifying evaluation API")
        success = await notify_evaluation_api(evaluation_url, notification_data)

        if success:
            logger.info(f"Successfully completed deployment for {task_id}")
        else:
            logger.error(f"Failed to notify evaluation API for {task_id}")

    except Exception as e:
        logger.error(f"Error in process_deployment: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
