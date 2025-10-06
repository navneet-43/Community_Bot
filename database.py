import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class DatabaseManager:
    def __init__(self, db_path: str = 'rusk_media_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                display_name TEXT,
                phone_number TEXT,
                campaign TEXT,
                invite_link TEXT,
                screening_completed BOOLEAN DEFAULT FALSE,
                screening_data TEXT,  -- JSON string
                roles_assigned TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                invite_link TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Screening sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screening_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                campaign TEXT,
                current_question TEXT,
                answers TEXT,  -- JSON string
                is_completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str, display_name: str, 
                 campaign: str = None, invite_link: str = None) -> bool:
        """Add a new user to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, display_name, campaign, invite_link, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, display_name, campaign, invite_link))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                user_data = dict(zip(columns, row))
                
                # Parse JSON fields
                if user_data['screening_data']:
                    user_data['screening_data'] = json.loads(user_data['screening_data'])
                if user_data['roles_assigned']:
                    user_data['roles_assigned'] = json.loads(user_data['roles_assigned'])
                
                conn.close()
                return user_data
            
            conn.close()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_screening(self, user_id: int, screening_data: Dict, 
                            roles_assigned: List[str]) -> bool:
        """Update user's screening data and roles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET screening_data = ?, roles_assigned = ?, screening_completed = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (json.dumps(screening_data), json.dumps(roles_assigned), user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user screening: {e}")
            return False
    
    def start_screening_session(self, user_id: int, campaign: str) -> int:
        """Start a new screening session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO screening_sessions (user_id, campaign, current_question, answers)
                VALUES (?, ?, 'show_types', '{}')
            ''', (user_id, campaign))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id
        except Exception as e:
            print(f"Error starting screening session: {e}")
            return None
    
    def update_screening_session(self, user_id: int, question: str, answer: Any) -> bool:
        """Update screening session with new answer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current answers
            cursor.execute('''
                SELECT answers FROM screening_sessions 
                WHERE user_id = ? AND is_completed = FALSE
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                answers = json.loads(row[0]) if row[0] else {}
                answers[question] = answer
                
                cursor.execute('''
                    UPDATE screening_sessions 
                    SET answers = ?, current_question = ?
                    WHERE user_id = ? AND is_completed = FALSE
                ''', (json.dumps(answers), question, user_id))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
        except Exception as e:
            print(f"Error updating screening session: {e}")
            return False
    
    def complete_screening_session(self, user_id: int) -> Optional[Dict]:
        """Complete screening session and return final answers"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT answers FROM screening_sessions 
                WHERE user_id = ? AND is_completed = FALSE
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                answers = json.loads(row[0]) if row[0] else {}
                
                cursor.execute('''
                    UPDATE screening_sessions 
                    SET is_completed = TRUE
                    WHERE user_id = ? AND is_completed = FALSE
                ''', (user_id,))
                
                conn.commit()
                conn.close()
                return answers
            
            conn.close()
            return None
        except Exception as e:
            print(f"Error completing screening session: {e}")
            return None
    
    def add_campaign(self, name: str, description: str, invite_link: str) -> bool:
        """Add a new campaign"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO campaigns (name, description, invite_link)
                VALUES (?, ?, ?)
            ''', (name, description, invite_link))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding campaign: {e}")
            return False
    
    def get_campaigns(self) -> List[Dict]:
        """Get all campaigns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM campaigns WHERE is_active = TRUE')
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            campaigns = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            return campaigns
        except Exception as e:
            print(f"Error getting campaigns: {e}")
            return []
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Completed screenings
            cursor.execute('SELECT COUNT(*) FROM users WHERE screening_completed = TRUE')
            completed_screenings = cursor.fetchone()[0]
            
            # Users by campaign
            cursor.execute('''
                SELECT campaign, COUNT(*) as count 
                FROM users 
                WHERE campaign IS NOT NULL 
                GROUP BY campaign
            ''')
            campaign_stats = dict(cursor.fetchall())
            
            conn.close()
            return {
                'total_users': total_users,
                'completed_screenings': completed_screenings,
                'campaign_stats': campaign_stats
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}

