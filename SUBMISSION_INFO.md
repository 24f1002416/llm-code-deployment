# Google Form Submission Information

## What to Submit

When filling out the Google Form, you'll need these three values:

### 1. API Endpoint URL
```
https://your-app-name.onrender.com/deploy
```
**Important**: Include `/deploy` at the end!

Replace `your-app-name` with your actual deployment name from Render.com (or your chosen platform).

### 2. Secret Value
```
Armageddon@123
```
**Important**: This is fixed and already set in your `.env.example` file. Do not change it!

### 3. GitHub Repository URL
```
https://github.com/your-username/llm-code-deployment
```
Replace with your actual GitHub username and repository name.

## Quick Checklist Before Submitting

- [ ] API is deployed and running
- [ ] Tested health check: `curl https://your-app.onrender.com/` returns `{"status":"ok",...}`
- [ ] Environment variables are set on deployment platform:
  - [ ] `SECRET=Armageddon@123`
  - [ ] `ANTHROPIC_API_KEY=sk-ant-...`
  - [ ] `GITHUB_TOKEN=ghp_...`
  - [ ] `GITHUB_USERNAME=your-username`
- [ ] Tested a full deployment locally
- [ ] GitHub repo is public
- [ ] All code is pushed to GitHub

## After Submitting

1. **Monitor your deployment**
   - Keep your API running
   - Check logs regularly
   - Ensure it stays awake (Render free tier sleeps after 15 min)

2. **When you receive a request**
   - The instructor will POST to your `/deploy` endpoint
   - Your API will automatically:
     - Generate code using Claude
     - Create a GitHub repo
     - Enable GitHub Pages
     - Notify the evaluation API
   - Check your logs to verify it worked
   - Check your GitHub for the new repository

3. **Round 2**
   - You may receive a second request with `"round": 2`
   - Your API will automatically handle it
   - It will update the existing repository

## Expected Timeline

1. **Submit form** → Instructors receive your information
2. **Within 24-48 hours** → Instructors send Round 1 request
3. **Your API processes** → Should complete within 5-10 minutes
4. **Instructors evaluate** → May take several hours/days
5. **Round 2 request** → Usually sent after Round 1 evaluation

## Troubleshooting

### If you don't receive a request
- Verify your API endpoint is publicly accessible
- Check that you submitted the correct URL with `/deploy`
- Ensure the secret matches exactly

### If your API fails
- Check logs on your deployment platform
- Verify all environment variables are set
- Test locally first
- Check API keys are valid

### If GitHub repo creation fails
- Verify GitHub token has correct permissions
- Check token hasn't expired
- Ensure GITHUB_USERNAME is correct

## Cost Tracking

**Keep an eye on:**
- Anthropic API usage at https://console.anthropic.com/
- Render.com usage (should stay within free tier)
- GitHub remains free for public repos

**Expected costs:**
- ~$0.01-0.05 per request to Claude API
- Total project cost should be < $1

## Support

**Documentation:**
- `README.md` - Complete documentation
- `DEPLOYMENT_GUIDE.md` - Detailed deployment steps
- `QUICK_START.md` - Quick reference

**Need help?**
1. Check the logs first
2. Review troubleshooting sections
3. Test locally to isolate issues
4. Verify all environment variables

Good luck with your submission! 🎉
