# Railway Deployment Instructions

## Quick Deploy to Railway

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub
   - Connect your GitHub account

2. **Deploy via Railway Dashboard**
   - Click "Deploy from GitHub repo"
   - Select this repository
   - Railway will auto-detect Python and deploy

3. **Set Environment Variables**
   In Railway dashboard, go to Variables tab and add:
   ```
   TG_TOKEN=7688729602:AAEoi5jAtR-n3XOxJI7DSonbLoqJSEXaXvA
   EBAY_VERIFICATION_TOKEN=pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123
   ```

4. **Get Your Railway URL**
   - After deployment, Railway provides a URL like: `your-app-name.up.railway.app`
   - Your eBay endpoint will be: `https://your-app-name.up.railway.app/marketplace-deletion`

5. **Update eBay Developer Portal**
   - Login to eBay Developer Portal
   - Go to your app settings
   - Update the Marketplace Account Deletion endpoint to your Railway URL
   - Save and test the endpoint

## Alternative: Railway CLI Deploy

1. **Install Railway CLI**
   ```bash
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login and Deploy**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables**
   ```bash
   railway variables set TG_TOKEN=7688729602:AAEoi5jAtR-n3XOxJI7DSonbLoqJSEXaXvA
   railway variables set EBAY_VERIFICATION_TOKEN=pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123
   ```

## Files for Railway Deployment

- `app.py` - Main Flask application (Railway-optimized)
- `requirements-railway.txt` - Minimal dependencies for Railway
- `Procfile` - Tells Railway how to start the app
- `railway.json` (optional) - Railway configuration

## Benefits of Railway

✅ **Automatic HTTPS** - Railway provides valid SSL certificates  
✅ **Zero Config** - No server setup, firewall, or DNS configuration  
✅ **High Uptime** - Professional hosting with monitoring  
✅ **eBay Compatible** - Trusted domains that pass eBay validation  
✅ **Easy Scaling** - Automatic scaling based on traffic  
✅ **Free Tier** - $5/month credit, plenty for webhook usage  

## Expected Railway URL

Your webhook will be accessible at:
`https://pokemon-arbitrage-[random].up.railway.app/marketplace-deletion`

This URL will automatically work with eBay's validation!
