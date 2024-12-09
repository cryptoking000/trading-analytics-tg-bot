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
                'ETH_wallet_address': 'TEXT',
                'BTC_wallet_address': 'TEXT',
                'USDT_wallet_address': 'TEXT',
                'total_amount': 'INTEGER'
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

    # def add_user(self, chat_id: int, username: str = None, 
    #              expired_time: str = None, paid: bool = False,
    #              transaction_hash: str = None,
    #              last_active: str = None,
    #             ) -> bool:
    #     """Add or update a user in the database"""
    #     try:
    #         with sqlitecloud.connect(self.connection_string) as conn:
    #             cursor = conn.cursor()
    #             cursor.execute('''
    #                 INSERT INTO user_data 
    #                 (chat_id, username, expired_time, paid, transaction_hash, last_active)
    #                 VALUES (?, ?, ?, ?, ?, ?)
    #                 ON CONFLICT(chat_id) DO UPDATE SET
    #                     username=excluded.username,
    #                     expired_time=excluded.expired_time,
    #                     paid=excluded.paid,
    #                     transaction_hash=excluded.transaction_hash,
    #                     last_active=excluded.last_active
    #             ''', (chat_id,last_active))
    #             conn.commit()
    #             return True
    #     except Exception as e:
    #         print(f"Error adding/updating user: {e}")
    #         return False

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
                        "ETH_wallet_address": row[10],
                        "BTC_wallet_address": row[11],
                        "USDT_wallet_address": row[12],
                        "payment_method": row[13],
                        "total_amount": row[14]
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
                        "ETH_wallet_address": result[10],
                        "BTC_wallet_address": result[11],
                        "USDT_wallet_address": result[12],
                        "payment_method": result[13],
                        "total_amount": result[14]
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def update_user_data(self, chat_id: int, **kwargs) -> bool:
        """Update user payment status and related fields
        
        Args:
            chat_id (int): The chat ID of the user to update
            **kwargs: Fields to update, which can include:
                - paid (bool): Payment status
                - payment_method (str): Method of payment
                - transaction_hash (str): Transaction hash
                - expired_time (str): Expiration timestamp
                - ETH_wallet_address (str): ETH wallet address
                - BTC_wallet_address (str): BTC wallet address
                - USDT_wallet_address (str): USDT wallet address
                - total_amount (float): Total amount paid
                
        Returns:
            bool: True if update successful, False otherwise
        """
        VALID_FIELDS = {
            'paid': 'paid = ?',
            'payment_method': 'payment_method = ?',
            'transaction_hash': 'transaction_hash = ?', 
            'expired_time': 'expired_time = ?',
            'ETH_wallet_address': 'ETH_wallet_address = ?',
            'BTC_wallet_address': 'BTC_wallet_address = ?',
            'USDT_wallet_address': 'USDT_wallet_address = ?',
            'total_amount': 'total_amount = ?',
            'username': 'username = ?',
            'last_active': 'last_active = ?',
            'last_paid_date': 'last_paid_date = ?',
            'total_paid_budget': 'total_paid_budget = ?'
        }

        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query based on provided fields
                update_fields = []
                values = []
                
                # Process only valid fields
                for field, sql in VALID_FIELDS.items():
                    if field in kwargs:
                        update_fields.append(sql)
                        values.append(kwargs[field])

                # Handle paid status update specially
                if kwargs.get('paid'):
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_fields.extend([
                        'last_paid_date = ?',
                        'total_paid_budget = COALESCE(total_paid_budget, 0) + 1'
                    ])
                    values.append(current_time)
                
                # Handle total_amount update
                if 'total_amount' in kwargs:
                    update_fields.append('total_amount = COALESCE(total_amount, 0) + ?')
                    values.append(kwargs['total_amount'])
                
                if not update_fields:
                    return False
                    
                # Build and execute update query
                query = f'''
                    UPDATE user_data 
                    SET {', '.join(update_fields)}
                    WHERE chat_id = ?
                '''
                values.append(chat_id)
                
                # First check if user exists
                cursor.execute('SELECT 1 FROM user_data WHERE chat_id = ?', (chat_id,))
                exists = cursor.fetchone()
                
                if not exists:
                    # Insert new user if doesn't exist
                    cursor.execute('INSERT INTO user_data (chat_id) VALUES (?)', (chat_id,))
                
                # Now do the update
                cursor.execute(query, tuple(values))
                conn.commit()
                print(f"User payment data updated for chat_id: {chat_id}")
                return True
                
        except Exception as e:
            print(f"Error updating user payment data: {e}")
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

    def get_expiry_date(self, chat_id: int) -> Optional[datetime]:
        """Get the expiry date for a user's subscription
        
        Args:
            chat_id (int): The chat ID of the user
            
        Returns:
            Optional[datetime]: The expiry date if found, None otherwise
        """
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT expired_time 
                    FROM user_data 
                    WHERE chat_id = ?
                ''', (chat_id,))
                
                result = cursor.fetchone()
                if result and result[0]:
                    return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
                return None
                
        except Exception as e:
            print(f"Error getting expiry date: {e}")
            return None
# Create database instance
db = UserDatabaseManager()   