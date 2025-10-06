# 🎯 Rusk Media Hierarchical Screening System

## ✅ WHAT'S NEW

Your bot now creates **hierarchical nested groups** based on user responses!

### **Group Structure:**
```
Gender (Primary)
└── Age (Subgroup)
    └── Content Type (Sub-subgroup)
        └── Tier (Final subgroup)
```

## 📋 THE 4 SCREENING QUESTIONS

### **Question 1: Gender** (Primary Cohort)
- "What is your gender?"
- Options: Male, Female, Non-binary, Prefer not to say
- **This determines the PRIMARY cohort group**

### **Question 2: Age Group** (Subgroup within Gender)
- "What is your age group?"
- Options: Under 18, 18-24, 25-34, 35-45, 45+
- **This should be the subgroup within the primary cohort**

### **Question 3: Content Types** (Subgroup within Age)
- "Which of the following types of shows do you enjoy watching? (Select all that apply)"
- Options: Scripted series, Unscripted reality shows, Anime
- **Next subgroup within age** - Users can select MULTIPLE
- **If user selects both Scripted and Unscripted, they get added to BOTH groups**

### **Question 4: City** (Final Subgroup within Content)
- "Which city/town do you live in?"
- Cities are automatically categorized into Tier 1, 2, or 3
- **Next subgroup within content group**

## 🏗️ HOW GROUPS ARE CREATED

### **Example 1: Single Content Type**

**User Selects:**
- Gender: Female
- Age: 18-24
- Content: Scripted series
- City: Delhi

**Groups Created:**
```
Role: female-18_24-scripted-tier1
Channel: #female-18_24-scripted-tier1
```

**Hierarchy:**
1. **female** (Primary)
2. **female-18_24** (Age subgroup)
3. **female-18_24-scripted** (Content subgroup)
4. **female-18_24-scripted-tier1** (Final tier subgroup)

### **Example 2: Multiple Content Types**

**User Selects:**
- Gender: Male
- Age: 25-34
- Content: **Scripted AND Unscripted** (both selected)
- City: Mumbai

**Groups Created:**
```
Role 1: male-25_34-scripted-tier1
Channel 1: #male-25_34-scripted-tier1

Role 2: male-25_34-unscripted-tier1
Channel 2: #male-25_34-unscripted-tier1
```

**User Gets Access To:**
- ✅ #male-25_34-scripted-tier1
- ✅ #male-25_34-unscripted-tier1
- ❌ All other channels (NO ACCESS)

### **Example 3: Different Tier**

**User Selects:**
- Gender: Female
- Age: 35-45
- Content: Anime
- City: Patna (Tier 2)

**Groups Created:**
```
Role: female-35_45-anime-tier2
Channel: #female-35_45-anime-tier2
```

## 🌆 CITY TIER CLASSIFICATION

### **Tier 1 Cities (8 cities):**
- Bangalore/Bengaluru
- Delhi/New Delhi/NCR
- Chennai
- Hyderabad
- Mumbai
- Pune
- Kolkata/Calcutta
- Ahmedabad

### **Tier 2 Cities (20 cities):**
- Amritsar, Bhopal, Bhubaneswar, Chandigarh, Faridabad
- Ghaziabad, Jamshedpur, Jaipur, Kochi/Cochin, Lucknow
- Nagpur, Patna, Raipur, Surat, Visakhapatnam/Vizag
- Agra, Ajmer, Kanpur, Mysuru/Mysore, Srinagar

### **Tier 3 Cities:**
- All other cities not in Tier 1 or Tier 2

### **City Name Normalization:**

The bot automatically handles variations:
- **Delhi** = Delhi, New Delhi, NCR
- **Bangalore** = Bangalore, Bengaluru
- **Kolkata** = Kolkata, Calcutta
- **Kochi** = Kochi, Cochin
- **Visakhapatnam** = Visakhapatnam, Vizag
- **Mysuru** = Mysuru, Mysore

**Case insensitive:** "delhi", "Delhi", "DELHI" all work!

## 🎯 HOW THE SYSTEM WORKS

### **When User Joins:**

1. **User clicks server link** → Joins Discord server
2. **Bot sends DM** → Welcome message
3. **Question 1 (Gender)** → User selects: Female
4. **Question 2 (Age)** → User selects: 18-24
5. **Question 3 (Content)** → User selects: Scripted AND Anime (multiple!)
6. **Question 4 (City)** → User selects: Delhi

### **Bot Processing:**

```
User Profile:
- Gender: female
- Age: 18_24
- Content: [scripted, anime]  ← MULTIPLE!
- City: Delhi → Tier 1

Groups to Create:
1. female-18_24-scripted-tier1
2. female-18_24-anime-tier1

Channels to Create:
1. #female-18_24-scripted-tier1 (private, only for this group)
2. #female-18_24-anime-tier1 (private, only for this group)
```

### **Result:**

✅ User gets 2 roles
✅ User gets access to 2 channels
✅ Both channels are PRIVATE (only visible to users in that specific group)
❌ User CANNOT see any other groups' channels

## 🔐 PRIVACY & ACCESS CONTROL

### **Channel Permissions:**

Each channel is **completely private**:
- ❌ Default role: **No access** (can't even see the channel)
- ✅ Specific role only: **Full access**
- ✅ Bot: **Always has access** (for management)

### **Example Permissions:**

```
Channel: #female-18_24-scripted-tier1

Permissions:
- @everyone: ❌ Cannot read messages
- @female-18_24-scripted-tier1: ✅ Can read messages
- @Rusk Media Bot: ✅ Can read messages
```

## 📊 EXAMPLE SCENARIOS

### **Scenario 1: Overlapping Groups**

**User A:**
- Female, 18-24, Scripted, Delhi (Tier 1)
- Group: `female-18_24-scripted-tier1`

**User B:**
- Female, 18-24, Scripted, Mumbai (Tier 1)
- Group: `female-18_24-scripted-tier1`

**Result:** Both users are in the SAME group and can see each other's messages!

### **Scenario 2: Different Age, Same Everything Else**

**User A:**
- Male, 18-24, Scripted, Delhi
- Group: `male-18_24-scripted-tier1`

**User B:**
- Male, 25-34, Scripted, Delhi
- Group: `male-25_34-scripted-tier1`

**Result:** Different groups! They CANNOT see each other's channels.

### **Scenario 3: Multiple Content Types**

**User A:**
- Female, 25-34, Scripted + Unscripted + Anime, Mumbai
- Groups: 
  - `female-25_34-scripted-tier1`
  - `female-25_34-unscripted-tier1`
  - `female-25_34-anime-tier1`

**Result:** User A has access to 3 different channels!

## 🎬 USER EXPERIENCE

### **What User Sees After Screening:**

```
Screening Complete! 🎉

Your Profile:
✅ Gender: Female
✅ Age Group: 18-24
✅ Content Types: Scripted series, Anime
✅ City: Delhi (TIER1)

Your Groups:
✅ female-18_24-scripted-tier1
✅ female-18_24-anime-tier1

Your Channels:
📺 #female-18_24-scripted-tier1
📺 #female-18_24-anime-tier1

What's Next?
Head back to the Rusk Media server! You now have access to your 
personalized channels.
```

### **In Discord Server:**

User will ONLY see:
- #female-18_24-scripted-tier1
- #female-18_24-anime-tier1

All other channels are **invisible** to them!

## 🚀 BENEFITS

### **1. Perfect Segmentation**
- Users only see content relevant to their exact demographic
- No clutter from irrelevant groups

### **2. Multiple Content Types**
- Users can join multiple content groups if they like different types
- Flexible based on user preferences

### **3. Tier-Based Organization**
- Separate discussions for different city tiers
- Better targeting for regional content

### **4. Scalable**
- Bot automatically creates new groups as needed
- No manual channel/role creation required

### **5. Privacy**
- Each group is completely isolated
- Users can't access groups they don't belong to

## 📈 GROUP NAMING CONVENTION

### **Format:**
```
{gender}-{age}-{content}-{tier}
```

### **Examples:**
```
male-18_24-scripted-tier1
female-25_34-unscripted-tier2
male-35_45-anime-tier3
female-under_18-scripted-tier1
male-45_plus-unscripted-tier2
```

### **Channel Names:**
Same as role names, with `#` prefix in Discord

## 🔧 TECHNICAL DETAILS

### **Automatic Creation:**
- Roles are created on-demand when first user needs them
- Channels are created with proper permissions automatically
- No pre-creation required

### **Database Storage:**
All user data stored:
- Gender, Age, Content preferences, City, Tier
- Role assignments
- Screening completion status
- Campaign tracking

### **Admin Tools:**
- `/admin_stats` - View screening statistics
- Database tracks all user segments

---

## ✅ YOUR BOT IS NOW LIVE!

The hierarchical screening system is active and will:
1. ✅ Ask 4 questions in order
2. ✅ Create nested groups based on answers
3. ✅ Assign users to appropriate groups
4. ✅ Create private channels for each group
5. ✅ Handle multiple content type selections
6. ✅ Normalize city names automatically
7. ✅ Classify cities into tiers

**Test it with a new member and watch the magic happen! 🎉**

