# LLM Code Deployment API

A FastAPI service that automatically generates web applications using Claude AI, deploys them to GitHub Pages, and notifies an evaluation API. Built for the IIT Madras Tools in Data Science project.

## Features

- **POST endpoint** `/deploy` that accepts JSON requests with app briefs
- **Secret verification** for authentication
- **LLM code generation** using Claude Sonnet 4.5 API
- **GitHub integration** - creates repos, pushes code, enables Pages
- **Automatic deployment** to GitHub Pages
- **Evaluation API notification** with exponential backoff retry
- **Handles revisions** (round 2 requests)

## Architecture

1. Receives POST request with app brief and requirements
2. Verifies secret token
3. Returns HTTP 200 immediately (processing happens asynchronously)
4. Uses Claude AI to generate HTML/JS/CSS based on requirements
5. Creates GitHub repository with unique name
6. Pushes generated files + LICENSE + README
7. Enables GitHub Pages deployment
8. Notifies evaluation API with repo details and retry logic

## Setup

### Prerequisites

- Python 3.10 or higher
- GitHub account
- Anthropic API key (Claude)
- GitHub Personal Access Token

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your API keys and username:

```env
# Secret value (fixed - do not change)
SECRET=Armageddon@123

# Get from https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Create at https://github.com/settings/tokens/new
# Required permissions: repo, workflow
GITHUB_TOKEN=ghp_xxxxx

# Your GitHub username
GITHUB_USERNAME=your-github-username

# Optional: Port (defaults to 8000)
PORT=8000
```

**Important**:
- Keep your `.env` file secure and never commit it
- The SECRET is already set to `Armageddon@123` - do not change it
- You'll submit `Armageddon@123` as the secret in the Google Form

## Local Testing

### Start the server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Test the health check

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status": "ok", "message": "LLM Code Deployment API is running"}
```

### Test the deployment endpoint

Create a test request file `test_request.json`:

```json
{
  "email": "test@example.com",
  "secret": "your-secret-from-env",
  "task": "test-task-123",
  "round": 1,
  "nonce": "test-nonce-456",
  "brief": "Create a simple HTML page with a heading 'Hello World' and a paragraph with id='content' that says 'This is a test'",
  "checks": [
    "Page has h1 with 'Hello World'",
    "Page has p#content with test message"
  ],
  "evaluation_url": "https://httpbin.org/post",
  "attachments": []
}
```

Send the request:

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

Expected response:
```json
{
  "status": "accepted",
  "message": "Request received and processing"
}
```

Check the logs to see the deployment progress. The API will:
1. Generate code using Claude
2. Create a GitHub repository
3. Push files to the repo
4. Enable GitHub Pages
5. Notify the evaluation URL

## Deployment to Production

### Option 1: Render.com (Recommended)

1. Create account at [render.com](https://render.com)

2. Click "New +" → "Web Service"

3. Connect your GitHub repository

4. Configure:
   - **Name**: llm-code-deployment
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

5. Add environment variables:
   - `SECRET`
   - `ANTHROPIC_API_KEY`
   - `GITHUB_TOKEN`
   - `GITHUB_USERNAME`
   - `PORT` (use 10000 or leave default)

6. Deploy!

Your API URL will be: `https://llm-code-deployment-xxxx.onrender.com`

### Option 2: Railway.app

1. Create account at [railway.app](https://railway.app)

2. Click "New Project" → "Deploy from GitHub repo"

3. Select your repository

4. Add environment variables in the Variables tab

5. Railway will auto-detect Python and deploy

Your API URL will be: `https://your-app.up.railway.app`

### Option 3: Fly.io

1. Install flyctl:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login:
```bash
flyctl auth login
```

3. Launch app:
```bash
flyctl launch
```

4. Set secrets:
```bash
flyctl secrets set SECRET=your-secret
flyctl secrets set ANTHROPIC_API_KEY=your-key
flyctl secrets set GITHUB_TOKEN=your-token
flyctl secrets set GITHUB_USERNAME=your-username
```

5. Deploy:
```bash
flyctl deploy
```

### Option 4: Heroku

1. Install Heroku CLI

2. Create app:
```bash
heroku create llm-code-deployment
```

3. Set config vars:
```bash
heroku config:set SECRET=your-secret
heroku config:set ANTHROPIC_API_KEY=your-key
heroku config:set GITHUB_TOKEN=your-token
heroku config:set GITHUB_USERNAME=your-username
```

4. Create `Procfile`:
```
web: python main.py
```

5. Deploy:
```bash
git push heroku main
```

## API Documentation

### POST /deploy

Accepts a JSON request to generate and deploy an application.

**Request Body:**
```json
{
  "email": "student@example.com",
  "secret": "your-secret-value",
  "task": "unique-task-id",
  "round": 1,
  "nonce": "unique-nonce",
  "brief": "Description of what to build",
  "checks": ["List", "of", "requirements"],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "file.txt",
      "url": "data:text/plain;base64,..."
    }
  ]
}
```

**Response:**
```json
{
  "status": "accepted",
  "message": "Request received and processing"
}
```

**Status Codes:**
- `200 OK` - Request accepted and processing
- `403 Forbidden` - Invalid secret
- `500 Internal Server Error` - Processing error

### GET /

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "LLM Code Deployment API is running"
}
```

## How It Works

### Code Generation

The API uses Claude Sonnet 4.5 to generate production-ready code based on:
- The app brief
- Requirements/checks to satisfy
- Attached files (data URIs)
- Task-specific constraints

Claude generates:
- `index.html` - Complete single-page application
- `README.md` - Professional documentation
- `LICENSE` - MIT license (added automatically)

### GitHub Deployment

1. Creates repository with naming: `{task-id}-round{round-number}`
2. Uploads files using GitHub API
3. Enables GitHub Pages on main branch
4. Returns repository URL, commit SHA, and Pages URL

### Evaluation Notification

Sends POST to evaluation URL with exponential backoff:
- Retry delays: 1s, 2s, 4s, 8s, 16s
- Maximum 5 attempts
- Includes repo metadata and nonce

## Google Form Submission

When submitting to the Google Form, provide:

1. **API URL**: Your deployed endpoint URL
   - Example: `https://llm-code-deployment-xxxx.onrender.com/deploy`

2. **Secret**: `Armageddon@123`

3. **GitHub Repo URL**: This API's repository URL
   - Example: `https://github.com/your-username/llm-code-deployment`

## Troubleshooting

### "Invalid secret" error

Make sure the `SECRET` in your `.env` is set to `Armageddon@123`.

### GitHub API rate limits

If you hit rate limits:
- Use a GitHub Personal Access Token (not password)
- Ensure token has `repo` and `workflow` scopes
- Consider implementing caching for round 2 updates

### Claude API errors

- Verify `ANTHROPIC_API_KEY` is valid
- Check your API usage limits
- Review logs for specific error messages

### GitHub Pages not working

- Pages can take 1-2 minutes to deploy
- Check repository Settings → Pages
- Ensure `index.html` exists in the repo root
- Verify repository is public

### Evaluation API not receiving notifications

- Check logs for HTTP errors
- Verify evaluation_url is reachable
- Ensure JSON payload format matches spec
- The API retries up to 5 times automatically

## Code Structure

```
main.py
├── CodeGenerator          # Handles Claude AI code generation
│   ├── generate_code()    # Main generation logic
│   └── _create_basic_files()  # Fallback if AI fails
├── GitHubDeployer         # Handles GitHub operations
│   └── create_and_deploy() # Creates repo, pushes files, enables Pages
├── notify_evaluation_api() # Sends notifications with retry
├── /deploy endpoint       # Main API endpoint
└── process_deployment()   # Async background processor
```

## Security Notes

- Never commit `.env` file
- Keep your `SECRET` secure
- Use environment variables for all credentials
- GitHub tokens should have minimal required permissions
- Consider implementing rate limiting for production
- Validate all inputs before processing

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the logs for error messages
2. Review the troubleshooting section
3. Verify all environment variables are set correctly
4. Test locally before deploying to production

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

To enable debug logging:

```python
# In main.py, change logging level:
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Support for multiple LLM providers
- [ ] Caching of generated code for round 2 updates
- [ ] Webhook support for async status updates
- [ ] Admin dashboard for monitoring deployments
- [ ] Rate limiting and request queuing
- [ ] Database for tracking deployment history
