#!/usr/bin/env python3
"""
Check database status
"""

from database import DatabaseManager

db = DatabaseManager('rusk_media_bot.db')

print("=== DATABASE STATUS ===")
stats = db.get_user_stats()
print(f"Total users: {stats.get('total_users', 0)}")
print(f"Completed screenings: {stats.get('completed_screenings', 0)}")

print("\n=== RECENT USERS ===")
users = db.get_all_users()
for user in users[-5:]:  # Last 5 users
    print(f"- {user['username']} (ID: {user['user_id']}) - Completed: {user.get('screening_completed', False)}")

print("\n=== RECENT SCREENING SESSIONS ===")
sessions = db.get_all_screening_sessions()
for session in sessions[-5:]:  # Last 5 sessions
    print(f"- Session {session['id']}: User {session['user_id']} - Status: {session['status']}")
