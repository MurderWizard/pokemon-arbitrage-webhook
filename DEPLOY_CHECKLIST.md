# 🚀 Railway Deployment Checklist

## Quick 5-Minute Setup

### ✅ Step 1: Create GitHub Repository
1. Go to: https://github.com/new
2. Repository name: `pokemon-arbitrage-webhook`
3. **Make it Public** (required for Railway free tier)
4. **Don't initialize** with README
5. Click "Create repository"

### ✅ Step 2: Push Code to GitHub
After creating the repo, run these commands (GitHub will show them):

```bash
git remote add origin https://github.com/YOUR_USERNAME/pokemon-arbitrage-webhook.git
git branch -M main
git push -u origin main
```

### ✅ Step 3: Deploy to Railway
1. Go to: https://railway.app
2. **Sign up with GitHub**
3. Click **"Deploy from GitHub repo"**
4. Select your `pokemon-arbitrage-webhook` repository
5. Railway will auto-detect Python and start deploying

### ✅ Step 4: Add Environment Variables
In Railway dashboard > Variables tab, add:
```
TG_TOKEN=7688729602:AAEoi5jAtR-n3XOxJI7DSonbLoqJSEXaXvA
EBAY_VERIFICATION_TOKEN=pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123
```

### ✅ Step 5: Get Your Railway URL
- After deployment: `https://pokemon-arbitrage-webhook-[random].up.railway.app`
- **eBay endpoint:** `https://pokemon-arbitrage-webhook-[random].up.railway.app/marketplace-deletion`

### ✅ Step 6: Update eBay Developer Portal
1. Login to eBay Developer Portal
2. Go to your app settings
3. Update **Marketplace Account Deletion** endpoint to your Railway URL
4. **Test the endpoint** - it should pass eBay's validation!

## 🎉 Expected Result
- ✅ Valid HTTPS webhook on Railway
- ✅ eBay compliance validation passes
- ✅ Production-ready deployment
- ✅ No more SSL or port issues!

## Files Included
- `app.py` - Railway-optimized Flask server
- `requirements-railway.txt` - Minimal dependencies
- `Procfile` - Railway startup command
- `railway.json` - Railway configuration
- `LICENSE` - MIT license for public repo
- `.gitignore` - Clean ignore rules
