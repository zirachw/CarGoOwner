import os
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class Mobil:
    """
    Class representing a customer (Mobil) with database operations.
    Handles all database-related functionality that was previously in MobilController.
    """
    Nomor_Plat: str
    Gambar: bytes
    Model: str
    Warna: str
    Tahun: int
    Status: bool
    
    def __init__(self, schema_path: str):
        """Initialize database connection and setup"""
        self.schema_path = schema_path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(schema_path)))
        self.db_path = os.path.join(self.base_dir, "src/CarGoOwnerMobil.db")
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables and sample data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Drop the existing Mobil table if it exists
            cursor.execute('DROP TABLE IF EXISTS Mobil')

            # Create the Mobil table with proper schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Mobil (
                    NomorPlat TEXT PRIMARY KEY,
                    Gambar BLOB,
                    Model TEXT NOT NULL,
                    Warna TEXT,
                    Tahun INTEGER NOT NULL,
                    StatusKetersediaan INTEGER NOT NULL CHECK (StatusKetersediaan IN (0, 1))  
                )
            ''')
            
            # Check if table needs sample data
            cursor.execute('SELECT COUNT(*) FROM Mobil')
            if cursor.fetchone()[0] == 0:
                # Insert sample customer data (sample_data list from original code)
                sample_data = [
                    # Add sample data here
                ]
                
                cursor.executemany('''
                    INSERT INTO Mobil (NomorPlat, Gambar, Model, Warna, Tahun, StatusKetersediaan)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sample_data)
                
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            if conn:
                conn.close()

    def get_mobil(self, page: int, items_per_page: int) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve paginated customer data from the database.
        
        Args:
            page: Current page number
            items_per_page: Number of items per page
            
        Returns:
            Tuple containing list of customer data and total number of records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM Mobil')
            total_records = cursor.fetchone()[0]
            
            # Get paginated data
            offset = (page - 1) * items_per_page
            cursor.execute('''
                SELECT * FROM Mobil 
                LIMIT ? OFFSET ?
            ''', (items_per_page, offset))
            
            # Convert to list of dictionaries
            columns = ['NomorPlat', 'Gambar', 'Model', 'Warna', 'Tahun', 'StatusKetersediaan']
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return data, total_records
            
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving customer data: {str(e)}")
        finally:
            if conn:
                conn.close()

    def set_mobil(self, mobil: Dict[str, Any], mode: str = "create") -> bool:
        """
        Create, update, or delete customer data in the database.
        
        Args:
            mobil: Dictionary containing customer data
            mode: Operation mode - "create", "edit", or "delete"
            
        Returns:
            bool: True if operation was successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if mode == "create":
                cursor.execute('''
                    INSERT INTO Mobil (NomorPlat, Gambar, Model, Warna, Tahun, StatusKetersediaan)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    mobil['NomorPlat'],
                    mobil['Gambar'],
                    mobil['Model'],
                    mobil['Warna'],
                    mobil['Tahun'],
                    mobil['StatusKetersediaan']
                ))
            elif mode == "edit":
                cursor.execute('''
                    UPDATE Mobil 
                    SET Gambar = ?, Model = ?, Warna = ?, Tahun = ?, StatusKetersediaan = ?
                    WHERE NomorPlat = ?
                ''', (
                    mobil['Gambar'],
                    mobil['Model'],
                    mobil['Warna'],
                    mobil['Tahun'],
                    mobil['StatusKetersediaan'],
                    mobil['NomorPlat']
                ))
            elif mode == "delete":
                # Support deleting a single customer or multiple customers
                nomor_plats = mobil['NomorPlat'] if isinstance(mobil['NomorPlat'], list) else [mobil['NomorPlat']]
                cursor.executemany(
                    'DELETE FROM Mobil WHERE NomorPlat = ?',
                    [(nomor_plat,) for nomor_plat in nomor_plats]
                )
            else:
                raise ValueError(f"Invalid mode: {mode}")
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            raise Exception(f"Error performing database operation: {str(e)}")
        finally:
            if conn:
                conn.close()

    def get_unique_colors(self):
        """Get unique colors from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT Warna FROM Mobil')
            colors = cursor.fetchall()
            return [color[0] for color in colors]
            
        except sqlite3.Error as e:
            print(f"Error getting unique colors: {e}")
            return []
            
        finally:
            if conn:
                conn.close()

    def get_unique_years(self):
        """Get unique years from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT Tahun FROM Mobil')
            years = cursor.fetchall()
            return [year[0] for year in years]
            
        except sqlite3.Error as e:
            print(f"Error getting unique years: {e}")
            return []
            
        finally:
            if conn:
                conn.close()