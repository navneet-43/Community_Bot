# 🎬 Rusk Media Auto-Screening Bot - Complete Guide

## ✅ What Changed

**BEFORE:** Users had to type `/start_screening` manually  
**NOW:** Screening starts AUTOMATICALLY when users join the server!

## 🚀 How It Works Now

### **Automatic Flow:**

1. **User clicks your server invite link** → Joins server
2. **Bot immediately sends DM** with welcome message
3. **Question 1 appears automatically** in their DMs
4. **User answers 7 questions** via dropdown menus
5. **Bot assigns roles automatically** based on answers
6. **User gets welcome message** in relevant channels
7. **User has access** to appropriate content channels

### **The 7 Questions:**

1. **Content Types** (multi-select): Scripted series, Unscripted reality shows, Anime
2. **City/Town** (single-select): Delhi, Mumbai, Bangalore, etc.
3. **Age Group** (single-select): Under 18, 18-24, 25-34, 35-45, 45+
4. **Gender** (single-select): Male, Female, Non-binary, Prefer not to say
5. **Genres** (multi-select): Romance/Drama, Comedy, Reality Competition, Dating shows, Anime, etc.
6. **Viewing Platform** (single-select): App User, YouTube, TV, Other Platform
7. **Education Level** (single-select): High School or Below, Some College/Diploma, Bachelor's Degree, Master's Degree or Higher

## 📊 What Happens After Screening

### **Automatic Role Assignment:**

**Content-Based Roles:**
- Selected "Scripted series" → **Scripted Viewers** role
- Selected "Unscripted reality" → **Unscripted Viewers** role
- Selected "Anime" → **Anime Fans** role

**Location-Based Roles:**
- From Delhi/Mumbai/Bangalore/etc. → **Tier-1 Cities** role
- From Tier-2 city → **Tier-2 Cities** role
- From Tier-3 city → **Tier-3 Cities** role

**Everyone Gets:**
- **Screened User** role (access to general screened content)

### **Channel Access:**

Users get access to channels based on their roles:
- **#scripted-content** → For Scripted Viewers
- **#unscripted-content** → For Unscripted Viewers
- **#anime-content** → For Anime Fans
- **#general-screened** → For all screened users

## 🎯 User Experience

### **When Someone Joins:**

**Step 1:** User clicks your Discord invite link
```
User joins "Rusk Media" server
```

**Step 2:** Bot sends welcome DM
```
Welcome to Rusk Media Community! 🎬
Thank you for joining! Please complete this quick 7-question screening 
to get access to relevant content channels.
```

**Step 3:** Question 1 appears automatically
```
Question 1/7 📋
Which of the following types of shows do you enjoy watching? 
(Select all that apply)

[Dropdown Menu]
🎬 Scripted series (fiction/web dramas)
📺 Unscripted reality/competition shows
🎌 Anime/animated series
```

**Step 4:** User selects and continues through all questions

**Step 5:** Completion message
```
Screening Complete! 🎉
Thank you for completing the screening process. You now have access 
to relevant content channels in the server!

Your Profile:
✅ Content Types: Scripted series, Anime
✅ City: Mumbai
✅ Age Group: 25-34
✅ Gender: Male

Assigned Roles:
✅ Scripted Viewers
✅ Anime Fans
✅ Tier-1 Cities
✅ Screened User

What's Next?
Head back to the Rusk Media server! You now have access to content 
channels based on your preferences.
```

**Step 6:** Welcome message in channels
```
In #scripted-content:
New Community Member! 🎉
Welcome @User to our scripted community!

In #general-screened:
New Screened Member! 🎬
Welcome @User to the Rusk Media community!
```

## ⚠️ Important Notes

### **DMs Must Be Enabled:**
- The screening happens via DM (Direct Messages)
- Users MUST have DMs enabled to receive questions
- If DMs are disabled, they get a message in #general-screened to enable DMs

### **Backup Command:**
- If auto-screening fails, users can type `/start_screening`
- This is a backup option in case DMs don't work

### **One-Time Screening:**
- Users only complete screening once
- If they already completed it, they won't see questions again
- Admins can reset users if needed

## 🎮 Testing the Bot

### **Test 1: Simulate New User**
1. Create a test Discord account or use an alt account
2. Get your server invite link
3. Click the link and join the server
4. Check DMs - you should immediately see welcome message + Question 1
5. Complete all 7 questions
6. Check your roles in the server

### **Test 2: Check Roles Were Assigned**
1. After completing screening
2. Go to server → Right-click your name → View Profile
3. Should see roles: Screened User + content roles + location role

### **Test 3: Check Channel Access**
1. After getting roles
2. Look at channel list
3. Should see channels you now have access to based on your answers

## 📈 Admin Features

### **View Statistics:**
Type `/admin_stats` to see:
- Total users
- Completed screenings
- Users by campaign

### **Database Storage:**
All data is stored in `rusk_media_bot.db`:
- User demographics
- Screening responses
- Role assignments
- Campaign tracking

## 🔧 How to Run the Bot

### **Start the Bot:**
```bash
cd /Users/navneetsingh/Desktop/community_bot
source venv/bin/activate
python bot.py
```

### **Keep Bot Running:**
The bot must be running 24/7 for auto-screening to work. Consider:
- Running on a server (VPS, AWS, etc.)
- Using a process manager like `pm2` or `systemd`
- Using a cloud hosting service

### **Stop the Bot:**
```bash
# Press Ctrl+C in the terminal
# Or kill the process:
pkill -f "python bot.py"
```

## 💡 Tips for Users

**Share this with your community:**
1. ✅ Make sure DMs are enabled before joining
2. ✅ Answer all 7 questions honestly
3. ✅ Check your roles after completing
4. ✅ Explore the channels you have access to

## 🎉 Benefits of Auto-Screening

✅ **Zero friction** - No commands to remember  
✅ **Immediate engagement** - Screening starts right away  
✅ **Better UX** - Smooth onboarding process  
✅ **Higher completion rate** - No manual step to trigger  
✅ **Automatic segmentation** - Users sorted into right groups instantly

## 📋 Campaign Tracking

The bot tracks where users came from:
- **AUTO_JOIN** - Regular server joins
- **DISCOVERY_2025** - Discovery campaign
- **FGD_SCRIPTED_SEPT24** - FGD scripted campaign
- etc.

You can create custom invite links and track which campaigns bring the most users!

---

**Your auto-screening bot is now live and ready to onboard users automatically! 🚀**

