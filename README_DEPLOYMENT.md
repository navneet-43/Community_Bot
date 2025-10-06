# Discord Bot Deployment Guide

## 🚀 Deploy to Railway.app (Recommended)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub account

### Step 2: Deploy Your Bot
1. **Push to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/community_bot.git
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Click "New Project" on Railway
   - Select "Deploy from GitHub repo"
   - Choose your `community_bot` repository
   - Railway will automatically detect it's a Python project

### Step 3: Set Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

```
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_server_id_here
DATABASE_PATH=rusk_media_bot.db
```

### Step 4: Deploy
- Railway will automatically build and deploy your bot
- Check the logs to ensure it's running
- Your bot will be online 24/7!

---

## 🎯 Alternative: Deploy to Render.com

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `discord-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

### Step 3: Set Environment Variables
Add the same environment variables as above.

### Step 4: Deploy
- Render will build and deploy automatically
- Free tier includes 750 hours/month (enough for 24/7)

---

## 📊 Monitoring Your Bot

### Railway.app
- View logs in real-time
- Monitor resource usage
- Automatic restarts on failure

### Render.com
- View logs in dashboard
- Monitor uptime
- Automatic scaling

---

## 🔧 Troubleshooting

### Common Issues:
1. **Bot not responding**: Check logs for errors
2. **Environment variables**: Ensure they're set correctly
3. **Database issues**: Railway provides PostgreSQL, Render provides persistent storage

### Logs to Check:
- Connection to Discord
- Command syncing
- Member join events
- Database operations

---

## 💰 Cost Comparison

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| Railway | $5 credit/month | $5+/month |
| Render | 750 hours/month | $7+/month |
| Heroku | None | $5+/month |

**Recommendation**: Start with Railway.app for reliability, or Render.com for simplicity.