import sqlitecloud
from typing import Optional, Dict, Any
from datetime import datetime

class UserDatabaseManager:
    """Database manager class for SQLite Cloud operations"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER UNIQUE,
                        username TEXT,
                        expired_time TIMESTAMP,
                        paid BOOLEAN DEFAULT FALSE,
                        transaction_key TEXT,
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")

    def add_user(self, chat_id: int, username: str = None, 
                 expired_time: str = None, paid: bool = False,
                 transaction_key: str = None,
                 last_active: str = None,
                ) -> bool:
        """Add or update a user in the database"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users 
                    (chat_id, username, expired_time, paid, transaction_key, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(chat_id) DO UPDATE SET
                        username=excluded.username,
                        expired_time=excluded.expired_time,
                        paid=excluded.paid,
                        transaction_key=excluded.transaction_key,
                        last_active=excluded.last_active
                ''', (chat_id, username, expired_time, paid, transaction_key, last_active))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding/updating user: {e}")
            return False

    def get_user(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by chat_id"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users WHERE chat_id = ?
                ''', (chat_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "chat_id": result[1],
                        "username": result[2],
                        "expired_time": result[3],
                        "paid": result[4],
                        "transaction_key": result[5],
                        "registration_date": result[6],
                        "last_active": result[7]
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def update_user_payment(self, chat_id: int, paid: bool, 
                          transaction_key: str, expired_time: str) -> bool:
        """Update user payment status"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET paid = ?, transaction_key = ?, expired_time = ?
                    WHERE chat_id = ?
                ''', (paid, transaction_key, expired_time, chat_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating payment: {e}")
            return False

    def delete_user(self, chat_id: int) -> bool:
        """Delete a user from database"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE chat_id = ?', (chat_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

# Create a singleton instance
db = UserDatabaseManager('sqlitecloud://cqxv3cfvhz.sqlite.cloud:8860/telegram-database1?apikey=LatG9mr0j4cxwXHUjj9713u08qd5NmKtXfynbbabZP0')