# Quick Deployment Guide

## Step-by-Step Deployment Instructions

### Step 1: Get Required API Keys

#### Anthropic API Key
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

#### GitHub Personal Access Token
1. Go to https://github.com/settings/tokens/new
2. Give it a descriptive name: "LLM Code Deployment"
3. Select scopes:
   - ✅ `repo` (all)
   - ✅ `workflow`
4. Click "Generate token"
5. Copy the token (starts with `ghp_`)
6. **Important**: Save it immediately - you won't see it again!

### Step 2: Local Setup

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/llm-code-deployment.git
cd llm-code-deployment

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env` with your API keys (SECRET is already set):
```env
SECRET=Armageddon@123
ANTHROPIC_API_KEY=sk-ant-xxxxx
GITHUB_TOKEN=ghp_xxxxx
GITHUB_USERNAME=your-github-username
PORT=8000
```

**Note**: The SECRET is fixed as `Armageddon@123` - do not change it.

### Step 3: Test Locally

```bash
# Start the server
python main.py
```

In another terminal:
```bash
# Test health check
curl http://localhost:8000/

# Test the deployment endpoint (test_request.json already has correct secret)
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

Watch the logs to see the deployment process.

### Step 4: Deploy to Production (Render.com - Recommended)

#### Why Render.com?
- Free tier available
- Automatic HTTPS
- Easy environment variable management
- Auto-deploy from GitHub
- Good for Python apps

#### Deployment Steps:

1. **Create Render Account**
   - Go to https://render.com/
   - Sign up with GitHub (recommended)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Grant Render access to the repo

3. **Configure Service**
   - **Name**: `llm-code-deployment` (or your choice)
   - **Environment**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free

4. **Add Environment Variables**
   Click "Environment" tab and add:
   ```
   SECRET = Armageddon@123
   ANTHROPIC_API_KEY = sk-ant-xxxxx
   GITHUB_TOKEN = ghp_xxxxx
   GITHUB_USERNAME = your-github-username
   PORT = 10000
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - Your URL will be: `https://llm-code-deployment-xxxx.onrender.com`

6. **Test Deployed API**
   ```bash
   curl https://your-app-name.onrender.com/
   ```

### Step 5: Submit to Google Form

You'll need to submit:

1. **API Endpoint URL**
   ```
   https://your-app-name.onrender.com/deploy
   ```
   (Note: Include `/deploy` at the end!)

2. **Secret Value**
   ```
   Armageddon@123
   ```

3. **GitHub Repository URL**
   ```
   https://github.com/your-username/llm-code-deployment
   ```

### Alternative: Deploy to Railway.app

Railway is another excellent option with a generous free tier:

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in "Variables" tab
6. Railway auto-deploys!

Your URL will be: `https://llm-code-deployment.up.railway.app`

### Alternative: Deploy to Fly.io

For more control and better free tier limits:

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app (follow prompts)
flyctl launch

# Set secrets
flyctl secrets set SECRET=Armageddon@123
flyctl secrets set ANTHROPIC_API_KEY=sk-ant-xxx
flyctl secrets set GITHUB_TOKEN=ghp-xxx
flyctl secrets set GITHUB_USERNAME=your-username

# Deploy
flyctl deploy
```

## Testing Your Deployed API

### Test 1: Health Check

```bash
curl https://your-deployed-url.com/
```

Expected response:
```json
{"status":"ok","message":"LLM Code Deployment API is running"}
```

### Test 2: Full Deployment Test

Create `prod_test.json`:
```json
{
  "email": "your-email@example.com",
  "secret": "Armageddon@123",
  "task": "prod-test-sum-of-sales",
  "round": 1,
  "nonce": "test-nonce-789",
  "brief": "Create a simple page with heading 'Test App' and a div with id='status' that shows 'Working!'",
  "checks": [
    "Has h1 with 'Test App'",
    "Has div#status with 'Working!'"
  ],
  "evaluation_url": "https://httpbin.org/post",
  "attachments": []
}
```

Send request:
```bash
curl -X POST https://your-deployed-url.com/deploy \
  -H "Content-Type: application/json" \
  -d @prod_test.json
```

Expected response:
```json
{
  "status": "accepted",
  "message": "Request received and processing"
}
```

Then check:
1. Your GitHub account for a new repo: `prod-test-sum-of-sales-round1`
2. The repo should have: `index.html`, `README.md`, `LICENSE`
3. GitHub Pages should be enabled
4. Visit: `https://your-username.github.io/prod-test-sum-of-sales-round1/`

## Troubleshooting

### Issue: "Invalid secret" error

**Solution**: Make sure the `SECRET` in your environment variables is set to `Armageddon@123` exactly.

### Issue: "ANTHROPIC_API_KEY not set"

**Solution**:
- Check your environment variables in your deployment platform
- Make sure there are no extra spaces in the key
- Verify the key is valid at https://console.anthropic.com/

### Issue: GitHub repo creation fails

**Solution**:
- Verify your `GITHUB_TOKEN` has `repo` and `workflow` permissions
- Check your GitHub token hasn't expired
- Make sure `GITHUB_USERNAME` matches your actual GitHub username (case-sensitive)

### Issue: Deployment times out

**Solution**:
- The free tier on Render/Railway may have cold starts (30-60 seconds)
- First request after inactivity takes longer
- Consider upgrading to a paid tier for production use

### Issue: GitHub Pages not accessible

**Solution**:
- GitHub Pages takes 1-2 minutes to deploy after repo creation
- Check repo Settings → Pages to verify it's enabled
- Make sure the repo is public
- Verify `index.html` exists in the repo root

## Monitoring Your API

### View Logs (Render.com)
1. Go to your service dashboard
2. Click "Logs" tab
3. See real-time logs of requests and deployments

### View Logs (Railway.app)
1. Click on your service
2. Click "Deployments"
3. Click on the latest deployment
4. View logs in real-time

### View Logs (Fly.io)
```bash
flyctl logs
```

## Cost Considerations

### Free Tier Limits

**Render.com Free Tier:**
- 750 hours/month
- Spins down after 15 minutes of inactivity
- Takes 30-60 seconds to wake up

**Railway Free Tier:**
- $5 credit/month
- No sleep on inactivity
- Faster cold starts

**Anthropic API:**
- Pay per token
- Sonnet 4.5: ~$3 per million input tokens
- Each request uses ~1000-2000 tokens
- Estimate: ~100-200 requests per $1

**GitHub:**
- Unlimited public repos
- GitHub Pages: Free for public repos

### Recommendations

For the project submission:
- Use Render.com or Railway free tier
- Monitor your Anthropic API usage
- Test with a few requests before submitting
- Total cost should be < $5 for the entire project

## Final Checklist

Before submitting:

- [ ] API is deployed and publicly accessible
- [ ] Health check endpoint returns 200 OK
- [ ] Test deployment creates a GitHub repo successfully
- [ ] GitHub Pages is enabled and accessible
- [ ] All environment variables are set correctly
- [ ] Secret is securely stored and not committed to git
- [ ] You have the three required values for Google Form:
  - [ ] API endpoint URL (with `/deploy`)
  - [ ] Secret value
  - [ ] GitHub repo URL

## Support

If you encounter issues:

1. Check the logs on your deployment platform
2. Test locally first to isolate the issue
3. Verify all environment variables are set
4. Check API keys are valid and have correct permissions
5. Review the main README.md for detailed troubleshooting

Good luck with your submission!
