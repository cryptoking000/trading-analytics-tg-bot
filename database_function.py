import sqlitecloud
from typing import Optional, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
connection_string = os.getenv("DATABASE_URL")

class UserDatabaseManager:
    """Database manager class for SQLite Cloud operations"""
    
    # def __init__(self):
    #     self.connection_string = connection_string
    #     print("🔗 Connecting to the database...")
    #     self._create_tables()
    #     print("✅ Database connection established.")

    # def _create_tables(self):
    #     """Create necessary database tables if they don't exist"""
    #     try:
    #         with sqlitecloud.connect(self.connection_string) as conn:
    #             cursor = conn.cursor()
    #             # First check if table exists
    #             cursor.execute('''
    #                 SELECT name FROM sqlite_master 
    #                 WHERE type='table' AND name='user_data'
    #             ''')
    #             table_exists = cursor.fetchone() is not None

    #             if not table_exists:
    #                 # Create table if it doesn't exist
    #                 cursor.execute('''
    #                     CREATE TABLE user_data (
    #                         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                         chat_id INTEGER UNIQUE,
    #                         is_group BOOLEAN DEFAULT FALSE,
    #                         username TEXT,
    #                         registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #                         last_active TIMESTAMP,
    #                         is_paid BOOLEAN DEFAULT FALSE,
    #                         expired_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #                         total_paid_budget INTEGER DEFAULT 0,
    #                         last_paid_date TIMESTAMP,
    #                         transaction_hash TEXT,
    #                         ETH_wallet_address TEXT,
    #                         BTC_wallet_address TEXT,
    #                         USDT_wallet_address TEXT,
    #                         payment_method TEXT,
    #                         total_amount INTEGER DEFAULT 0  
    #                     )
    #                 ''')
    #                 print("🆕 New table 'user_data' created.")
    #             else:
    #                 self._update_table_columns(cursor)
                
    #             conn.commit()
    #     except Exception as e:
    #         print(f"Error creating/updating tables: {e}")

    # def _update_table_columns(self, cursor):
    #     """Update table schema if new columns need to be added"""
    #     try:
    #         # Get existing columns
    #         cursor.execute('PRAGMA table_info(user_data)')
    #         existing_columns = {row[1] for row in cursor.fetchall()}

    #         # Define expected columns with their types
    #         expected_columns = {
    #             'chat_id': 'INTEGER UNIQUE',
    #             'is_group': 'BOOLEAN DEFAULT FALSE',
    #             'username': 'TEXT',
    #             'registration_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    #             'last_active': 'TIMESTAMP',
    #             'is_paid': 'BOOLEAN DEFAULT FALSE',
    #             'expired_time': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    #             'total_paid_budget': 'INTEGER DEFAULT 0',
    #             'last_paid_date': 'TIMESTAMP',
    #             'transaction_hash': 'TEXT',
    #             'ETH_wallet_address': 'TEXT',
    #             'BTC_wallet_address': 'TEXT',
    #             'USDT_wallet_address': 'TEXT',
    #             'payment_method': 'TEXT',
    #             'total_amount': 'INTEGER DEFAULT 0'  # Fixed default value for total_amount
    #         }

    #         # Add missing columns
    #         for column_name, column_type in expected_columns.items():
    #             if column_name not in existing_columns:
    #                 alter_query = f'ALTER TABLE user_data ADD COLUMN {column_name} {column_type}'
    #                 cursor.execute(alter_query)
    #                 print(f"Added new column: {column_name}")

    #     except Exception as e:
    #         print(f"Error updating table columns: {e}")

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
                    print(f"✅ Column '{column_name}' added successfully.")
                    return True
                return False
        except Exception as e:
            print(f"Error adding column: {e}")
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
                        "is_group": row[2],
                        "username": row[3],
                        "registration_date": row[4],
                        "last_active": row[5],
                        "is_paid": row[6],
                        "expired_time": row[7],
                        "total_paid_budget": row[8],
                        "last_paid_date": row[9],
                        "transaction_hash": row[10],
                        "ETH_wallet_address": row[11],
                        "BTC_wallet_address": row[12],
                        "USDT_wallet_address": row[13],
                        "payment_method": row[14],
                        "total_amount": row[15]
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
                        "is_group": result[2],
                        "username": result[3],
                        "registration_date": result[4],
                        "last_active": result[5], 
                        "is_paid": result[6],
                        "expired_time": result[7],
                        "total_paid_budget": result[8],
                        "last_paid_date": result[9],
                        "transaction_hash": result[10],
                        "ETH_wallet_address": result[11],
                        "BTC_wallet_address": result[12],
                        "USDT_wallet_address": result[13],
                        "payment_method": result[14],
                        "total_amount": result[15]
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def update_user_data(self, chat_id: int, **kwargs) -> bool:
        """Update user data, always updating last_active and username if provided
        
        Args:
            chat_id (int): The chat ID of the user to update
            **kwargs: Optional fields to update:
                - username (str): Username to update
                - any other user data fields
                
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()

                # Always update last_active
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_fields = ['last_active = ?']
                values = [current_time]
                print(f"🕒 Setting last_active to {current_time}")

                is_group = 1 if str(chat_id).startswith('-100') else 0
                update_fields.append('is_group = ?')
                values.append(is_group)
                
                # Check if user exists
                cursor.execute('SELECT expired_time FROM user_data WHERE chat_id = ?', (chat_id,))
                existing_user = cursor.fetchone()
                print(f"👤 Checking user {chat_id}: {'Exists' if existing_user else 'New user'} is_group: {is_group}")
                if existing_user:
                    # Always update username if provided
                    if 'username' in kwargs:
                        update_fields.append('username = ?')
                        values.append(kwargs['username'])
                        print(f"📝 Updating username to: {kwargs['username']}")

                    # Update paid status based on expired time
                    if existing_user:  # If expired time exists
                        print(existing_user)
                        if existing_user[0] is None:
                            expired_time = datetime.now()
                        else:
                            expired_time = datetime.strptime(existing_user[0], '%Y-%m-%d %H:%M:%S')
                        is_paid = 1 if datetime.now() < expired_time else 0
                        update_fields.append('is_paid = ?')
                        values.append(is_paid)
                        print(f"💰 Subscription status: {'Active' if is_paid else 'Expired'}")
                        print(f"📅 expired time: {expired_time}")     
                    else:
                        is_paid = 0  # Default to False if no expired time
                        update_fields.append('is_paid = ?')
                        values.append(is_paid)
                        print(f"📅📅 expired time: {expired_time}")
                    # Update other provided fields
                    for field, value in kwargs.items():
                        if field not in ['username', 'chat_id'] and value is not None:
                            update_fields.append(f'{field} = ?')
                            values.append(value)
                            print(f"✏️ Updating {field} to: {value}")

                    # Execute update
                    query = f'''
                        UPDATE user_data 
                        SET {', '.join(update_fields)}
                        WHERE chat_id = ?
                    '''
                    values.append(chat_id)
                    cursor.execute(query, tuple(values))
                    print("🔄 Executing UPDATE query")

                else:
                    # Create new user with minimal required fields
                    fields = ['chat_id', 'last_active']
                    values = [chat_id, current_time]
                    print(f"➕ Creating new user with chat_id: {chat_id}")

                    if 'username' in kwargs:
                        fields.append('username')
                        values.append(kwargs['username'])
                        print(f"👤 Setting initial username: {kwargs['username']}")

                    # Add any other provided fields
                    for field, value in kwargs.items():
                        if field not in ['username', 'chat_id', 'last_active']:
                            fields.append(field)
                            values.append(value)
                            print(f"📝 Setting initial {field}: {value}")

                    placeholders = ['?' for _ in fields]
                    query = f'''
                        INSERT INTO user_data ({', '.join(fields)})
                        VALUES ({', '.join(placeholders)})
                    '''
                    cursor.execute(query, tuple(values))
                    print("➕ Executing INSERT query")

                conn.commit()
                print("✅ Database transaction committed successfully")
                return True

        except Exception as e:
            print(f"❌ Error updating user data: {e}")
            print(f"📋 Debug info - chat_id: {chat_id}, kwargs: {kwargs}")
            return False

    def delete_user(self, chat_id: int) -> bool:
        """Delete a user from database"""
        try:
            with sqlitecloud.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_data WHERE chat_id = ?', (chat_id,))
                conn.commit()
                print(f"🗑️ User with chat_id {chat_id} deleted.")
                return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def get_expired_date(self, chat_id: int) -> Optional[datetime]:
        """Get the expired date for a user's subscription
        
        Args:
            chat_id (int): The chat ID of the user
            
        Returns:
            Optional[datetime]: The expired date if found, None otherwise
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
            print(f"Error getting expired date: {e}")
            return None

# Create database instance
db = UserDatabaseManager()   