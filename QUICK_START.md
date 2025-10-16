# Quick Start Guide

## What You Have

A complete LLM Code Deployment API that:
1. Receives POST requests with app briefs
2. Uses Claude AI to generate web applications
3. Creates GitHub repositories automatically
4. Deploys to GitHub Pages
5. Notifies evaluation APIs

## Files Created

```
project/
├── main.py                  # Main FastAPI application
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── Procfile                # For Heroku deployment
├── runtime.txt             # Python version specification
├── test_request.json       # Sample test request
├── README.md               # Complete documentation
├── DEPLOYMENT_GUIDE.md     # Step-by-step deployment
└── QUICK_START.md          # This file
```

## 5-Minute Setup

### 1. Get API Keys (5 minutes)

**Anthropic (Claude):**
- Visit: https://console.anthropic.com/settings/keys
- Create new key
- Copy it (starts with `sk-ant-`)

**GitHub:**
- Visit: https://github.com/settings/tokens/new
- Name: "LLM Deployment"
- Permissions: `repo` ✅ and `workflow` ✅
- Generate and copy (starts with `ghp_`)

### 2. Create .env File (1 minute)

```bash
cp .env.example .env
```

Edit `.env` with your API keys (SECRET is already set):
```env
SECRET=Armageddon@123
ANTHROPIC_API_KEY=sk-ant-xxxxx
GITHUB_TOKEN=ghp_xxxxx
GITHUB_USERNAME=your-github-username
```

**Note**: Do not change the SECRET value.

### 3. Test Locally (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

In another terminal:
```bash
# Test health check
curl http://localhost:8000/

# Should return: {"status":"ok","message":"LLM Code Deployment API is running"}
```

### 4. Deploy (10 minutes)

**Recommended: Render.com**

1. Go to https://render.com/ and sign up
2. New Web Service → Connect your GitHub repo
3. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `python main.py`
4. Add environment variables (copy from your .env)
5. Deploy!

Your URL: `https://your-app.onrender.com`

### 5. Test Production (2 minutes)

```bash
curl https://your-app.onrender.com/
```

### 6. Submit to Google Form

You need these three values:

1. **API URL**: `https://your-app.onrender.com/deploy`
2. **Secret**: `Armageddon@123`
3. **Repo URL**: `https://github.com/your-username/your-repo-name`

## What Happens When You Receive a Request?

```
1. Instructor sends POST to your /deploy endpoint
   ↓
2. Your API verifies the secret
   ↓
3. Returns HTTP 200 immediately
   ↓
4. Background process:
   - Calls Claude AI to generate code
   - Creates GitHub repository
   - Pushes code + LICENSE + README
   - Enables GitHub Pages
   - Notifies evaluation API
   ↓
5. Instructor evaluates your generated app
   ↓
6. Instructor may send Round 2 request
   ↓
7. Your API updates the existing repo
```

## Key Features

### Secret Verification
- Protects your endpoint from unauthorized access
- Fixed as `Armageddon@123` - used in both `.env` and Google Form

### Claude AI Integration
- Uses Sonnet 4.5 model
- Generates production-ready HTML/JS/CSS
- Follows all requirements in the brief
- Creates professional README files

### GitHub Automation
- Creates unique repos for each task
- Naming: `{task-id}-round{round-number}`
- Auto-enables GitHub Pages
- Includes MIT LICENSE

### Retry Logic
- Automatically retries evaluation API notifications
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Up to 5 attempts

## Common Issues & Solutions

### "Invalid secret"
→ Make sure `.env` SECRET is set to `Armageddon@123`

### "ANTHROPIC_API_KEY not set"
→ Add it to environment variables on your deployment platform

### GitHub token errors
→ Verify token has `repo` and `workflow` permissions

### Slow responses
→ Normal on free tier - first request after inactivity takes 30-60s

## Cost Estimate

- **Render.com**: Free (750 hours/month)
- **Anthropic API**: ~$0.003 per request (estimate)
- **GitHub**: Free for public repos

**Total for project**: < $1 (assuming ~50-100 test requests)

## Next Steps

1. ✅ Set up environment variables
2. ✅ Test locally
3. ✅ Deploy to production
4. ✅ Test production endpoint
5. ✅ Submit to Google Form
6. 🎯 Wait for instructor's request
7. 🎯 Monitor logs when request arrives
8. 🎯 Verify deployment worked
9. 🎯 Handle Round 2 if needed

## Need More Help?

- **Detailed docs**: See `README.md`
- **Step-by-step deployment**: See `DEPLOYMENT_GUIDE.md`
- **Test the API**: Edit `test_request.json` and send it
- **Check logs**: View in your deployment platform dashboard

## Pro Tips

1. **Test before submission**: Send a real request to verify everything works
2. **Monitor API usage**: Check Anthropic console for usage
3. **Never commit .env**: The `.env` file is in `.gitignore` - keep it that way
4. **Save your tokens**: Store GitHub token safely - you can't retrieve it again
5. **Check email**: The request will come from instructors to your API

Good luck! 🚀
