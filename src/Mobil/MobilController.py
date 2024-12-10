import sys
import os
import sqlite3
from .Mobil import Mobil  # Ensure correct import

class MobilController:
    def __init__(self, schema_path):
        """Initialize the MobilController class."""
        self.schema_path = schema_path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(schema_path)))
        self.db_path = os.path.join(self.base_dir, 'src/CarGoOwnerMobil.db')

        self.init_database()

    def init_database(self):
        """Initialize the database and create tables with sample customer data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
            
            cursor.execute('SELECT COUNT(*) FROM Mobil')
            if cursor.fetchone()[0] == 0:
                sample_data = [
                    ('J 2024 OWI', None, 'ESEMKA', 'Hitam', 2019, 0),
                    ('RI 1', None, 'NIGGA', 'Puthin', 2025, 1),
                    ('B 1234 ABC', None, 'Toyota Avanza', 'Hitam', 2018, 1),
                    ('B 2345 BCD', None, 'Toyota Innova', 'Putih', 2019, 1),
                    ('D 1452 HM', None, 'Avanza 2005', 'Cream', 2005, 1),
                    # Add more sample data as needed
                ]
                
                cursor.executemany('''
                    INSERT INTO Mobil (NomorPlat, Gambar, Model, Warna, Tahun, StatusKetersediaan)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sample_data)
                
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            
        finally:
            if conn:
                conn.close()

    def create_mobil(self, mobil: Mobil):
        """Create a new Mobil object."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Mobil (NomorPlat, Gambar, Model, Warna, Tahun, StatusKetersediaan)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (mobil.nomor_plat, mobil.gambar, mobil.model, mobil.warna, mobil.tahun, mobil.status_ketersediaan))
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error creating Mobil: {e}")
            
        finally:
            if conn:
                conn.close()

    def read_mobil(self, nomor_plat: str) -> Mobil:
        """Read a Mobil object by its NomorPlat."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Mobil WHERE NomorPlat = ?', (nomor_plat,))
            row = cursor.fetchone()
            if row:
                return Mobil(*row)
            return None
            
        except sqlite3.Error as e:
            print(f"Error reading Mobil: {e}")
            return None
            
        finally:
            if conn:
                conn.close()

    def update_mobil(self, mobil: Mobil):
        """Update an existing Mobil object."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Mobil
                SET Gambar = ?, Model = ?, Warna = ?, Tahun = ?, StatusKetersediaan = ?
                WHERE NomorPlat = ?
            ''', (mobil.gambar, mobil.model, mobil.warna, mobil.tahun, mobil.status_ketersediaan, mobil.nomor_plat))
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error updating Mobil: {e}")
            
        finally:
            if conn:
                conn.close()

    def delete_mobil(self, nomor_plat: str):
        """Delete an existing Mobil object."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Mobil WHERE NomorPlat = ?', (nomor_plat,))
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error deleting Mobil: {e}")
            
        finally:
            if conn:
                conn.close()

    def list_mobil(self, limit=10, offset=0):
        """List Mobil objects with pagination."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Mobil LIMIT ? OFFSET ?', (limit, offset))
            rows = cursor.fetchall()
            return [Mobil(*row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Error listing Mobil: {e}")
            return []
            
        finally:
            if conn:
                conn.close()