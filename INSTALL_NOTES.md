# Installation Notes

## Fixed: Windows pip Installation Issue

If you encountered this error:
```
ERROR: Could not install packages due to an OSError: [WinError 2] The system cannot find the file specified
```

This has been **FIXED**. The solution was to:
1. Remove `python-dotenv` from requirements.txt
2. Add a custom .env loader directly in `main.py`

## Installation Steps

### 1. Install Dependencies

```bash
pip install --user -r requirements.txt
```

The `--user` flag installs packages to your user directory and avoids Windows permission issues.

### 2. Verify Installation

All required packages:
- ✅ fastapi==0.115.0
- ✅ uvicorn[standard]==0.32.0
- ✅ anthropic==0.39.0
- ✅ httpx==0.27.2

### 3. Test the API

```bash
# Start the server
python main.py
```

You should see:
```
✓ Environment variables loaded from .env
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test Health Check

In another terminal:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status":"ok","message":"LLM Code Deployment API is running"}
```

## How the .env Loading Works

The code now has a built-in .env loader in `main.py` that:
1. Looks for `.env` file in the project directory
2. Parses each line for `KEY=VALUE` pairs
3. Sets environment variables automatically
4. Works on Windows without any external dependencies

No need for `python-dotenv` package!

## Troubleshooting

### If server won't start

Check that your `.env` file exists:
```bash
ls .env
```

If not, copy from example:
```bash
cp .env.example .env
```

### If environment variables aren't loading

Check the `.env` file format:
```
SECRET=Armageddon@123
ANTHROPIC_API_KEY=sk-ant-xxxxx
GITHUB_TOKEN=ghp_xxxxx
GITHUB_USERNAME=your-username
```

- No spaces around `=`
- No quotes needed (unless value has spaces)
- No comments on the same line as values

### If you get module not found errors

Reinstall dependencies:
```bash
pip install --user --force-reinstall -r requirements.txt
```

## Ready to Deploy

Once local testing works:
1. Follow `DEPLOYMENT_GUIDE.md` to deploy to Render.com
2. Set environment variables on the deployment platform
3. Test the deployed API
4. Submit to Google Form

All fixed and ready to go! 🎉
