# Render.com Deployment Guide for eBay Webhook

## Option 1: Direct Repository Connection (Recommended)

### Repository Setup
1. **Repository**: `MurderWizard/pokemon` (main repository)
   - Or use the current local files by pushing them to GitHub

### Render.com Web Service Configuration
1. **Name**: `pokemon-webhook`
2. **Environment**: `Python 3`
3. **Plan**: `Free`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn app_simple:app --bind 0.0.0.0:$PORT`

### Environment Variables
```
TG_TOKEN = your_telegram_bot_token_here
EBAY_VERIFICATION_TOKEN = verification_code_12345
```

## Option 2: render.yaml Auto-Detection

If your repository has the `render.yaml` file in the root, Render will auto-detect and use those settings.

## Required Files in Repository Root
```
├── app_simple.py          # Main Flask webhook app
├── requirements.txt       # Python dependencies
├── render.yaml           # Render configuration (optional)
└── README.md             # Documentation
```

## Testing Your Deployed Endpoint

Once deployed, your webhook will be available at:
`https://pokemon-webhook.onrender.com`

### Test Health Check
```bash
curl https://pokemon-webhook.onrender.com/health
```

### Test eBay Challenge Response
```bash
curl "https://pokemon-webhook.onrender.com/ebay/marketplace_account_deletion?challenge_code=test123"
```
Expected response: `{"challengeResponse": "test123"}`

## eBay Developer Portal Configuration

1. Go to eBay Developer Portal → Your App → Notifications
2. Set Notification Endpoint URL to: `https://pokemon-webhook.onrender.com/ebay/marketplace_account_deletion`
3. Set Verification Token to match your `EBAY_VERIFICATION_TOKEN` environment variable
4. Save and test the endpoint

## Troubleshooting

### Common Issues:
1. **Build fails**: Check that `requirements.txt` is in repository root
2. **App won't start**: Verify `app_simple.py` exists and has correct Flask app variable
3. **Environment variables**: Ensure TG_TOKEN and EBAY_VERIFICATION_TOKEN are set in Render dashboard

### Logs:
- Check Render dashboard → Your Service → Logs for detailed error information

## Files Status ✅
- ✅ `app_simple.py` - Minimal Flask webhook server
- ✅ `requirements.txt` - Clean dependencies (Flask, gunicorn, requests, python-dotenv)
- ✅ `render.yaml` - Auto-detection configuration
- ✅ All files ready for deployment
