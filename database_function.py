import sqlitecloud
from typing import Optional, Dict, Any
from datetime import datetime
connection_string = 'sqlitecloud://cqxv3cfvhz.sqlite.cloud:8860/Telegram-Bot-database?apikey=9AK557xjOuWgMqol4itbtJiAEiCiR5uF9r8QI7OvvlI'

class UserDatabaseManager:
    """Database manager class for SQLite Cloud operations"""
    
    def __init__(self):
        self.connection_string = connection_string
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                # First check if table exists
                cursor.execute('''
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='user_data'
                ''')
                table_exists = cursor.fetchone() is not None

                if not table_exists:
                    # Create table if it doesn't exist
                    cursor.execute('''
                        CREATE TABLE user_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chat_id INTEGER UNIQUE,
                            username TEXT,
                            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_active TIMESTAMP,
                            paid BOOLEAN DEFAULT FALSE,
                            expired_time TIMESTAMP,
                            total_paid_budget INTEGER DEFAULT 0,
                            last_paid_date TIMESTAMP,
                            transaction_hash TEXT,
                            payment_method TEXT
                           )
                    ''')
                else:
                    self._update_table_columns(cursor)
                
                conn.commit()
        except Exception as e:
            print(f"Error creating/updating tables: {e}")

    def _update_table_columns(self, cursor):
        """Update table schema if new columns need to be added"""
        try:
            # Get existing columns
            cursor.execute('PRAGMA table_info(user_data)')
            existing_columns = {row[1] for row in cursor.fetchall()}

            # Define expected columns with their types
            expected_columns = {
                # 'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                'chat_id': 'INTEGER UNIQUE',
                'username': 'TEXT',
                'registration_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'last_active': 'TIMESTAMP',
                'paid': 'BOOLEAN DEFAULT FALSE',
                'expired_time': 'TIMESTAMP',
                'total_paid_budget': 'INTEGER DEFAULT 0',
                'last_paid_date': 'TIMESTAMP',
                'transaction_hash': 'TEXT',
                'payment_method': 'TEXT',
                'wallet_address': 'TEXT'
            }

            # Add missing columns
            for column_name, column_type in expected_columns.items():
                if column_name not in existing_columns:
                    alter_query = f'ALTER TABLE user_data ADD COLUMN {column_name} {column_type}'
                    cursor.execute(alter_query)
                    print(f"Added new column: {column_name}")

        except Exception as e:
            print(f"Error updating table columns: {e}")

    def add_column(self, column_name: str, column_type: str) -> bool:
        """Add a new column to the user_data table"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                # Check if column exists
                cursor.execute('PRAGMA table_info(user_data)')
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                if column_name not in existing_columns:
                    cursor.execute(f'ALTER TABLE user_data ADD COLUMN {column_name} {column_type}')
                    conn.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error adding column: {e}")
            return False

    def add_user(self, chat_id: int, username: str = None, 
                 expired_time: str = None, paid: bool = False,
                 transaction_hash: str = None,
                 last_active: str = None,
                ) -> bool:
        """Add or update a user in the database"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_data 
                    (chat_id, username, expired_time, paid, transaction_hash, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(chat_id) DO UPDATE SET
                        username=excluded.username,
                        expired_time=excluded.expired_time,
                        paid=excluded.paid,
                        transaction_hash=excluded.transaction_hash,
                        last_active=excluded.last_active
                ''', (chat_id, username, expired_time, paid, transaction_hash, last_active))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding/updating user: {e}")
            return False

    def get_all_users(self) -> list:
        """Get all users from database"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM user_data')
                results = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "chat_id": row[1],
                        "username": row[2],
                        "expired_time": row[3],
                        "paid": row[4],
                        "transaction_hash": row[5],
                        "registration_date": row[6],
                        "last_active": row[7],
                        "total_paid_budget": row[8],
                        "last_paid_date": row[9],
                        "wallet_address": row[10],
                        "payment_method": row[11]
                    }
                    for row in results
                ]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        
    def get_user(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by chat_id"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM user_data WHERE chat_id = ?
                ''', (chat_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "chat_id": result[1],
                        "username": result[2],
                        "expired_time": result[3],
                        "paid": result[4],
                        "transaction_hash": result[5],
                        "registration_date": result[6],
                        "last_active": result[7],
                        "total_paid_budget": result[8],
                        "last_paid_date": result[9],
                        "wallet_address": result[10],
                        "payment_method": result[11]
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    def update_user_payment(self, chat_id: int, **kwargs) -> bool:
        """Update user payment status and related fields"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query based on provided fields
                update_fields = []
                values = []
                
                if 'paid' in kwargs:
                    update_fields.append('paid = ?')
                    values.append(kwargs['paid'])
                    
                if 'payment_method' in kwargs:
                    update_fields.append('payment_method = ?')
                    values.append(kwargs['payment_method'])
                    
                if 'transaction_hash' in kwargs:
                    update_fields.append('transaction_hash = ?')
                    values.append(kwargs['transaction_hash'])
                    
                if 'expired_time' in kwargs:
                    update_fields.append('expired_time = ?')
                    values.append(kwargs['expired_time'])
                    
                if 'wallet_address' in kwargs:
                    update_fields.append('wallet_address = ?')
                    values.append(kwargs['wallet_address'])
                    
                if 'paid' in kwargs and kwargs['paid']:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_fields.extend([
                        'last_paid_date = ?',
                        'total_paid_budget = total_paid_budget + 1'
                    ])
                    values.append(current_time)
                
                if not update_fields:
                    return False
                    
                query = f'''
                    UPDATE user_data 
                    SET {', '.join(update_fields)}
                    WHERE chat_id = ?
                '''
                values.append(chat_id)
                
                cursor.execute(query, tuple(values))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error updating user data: {e}")
            return False

    def delete_user(self, chat_id: int) -> bool:
        """Delete a user from database"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_data WHERE chat_id = ?', (chat_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
# Create database instance
db = UserDatabaseManager()   