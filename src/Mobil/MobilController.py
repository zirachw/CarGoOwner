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
                    ('J 2024 OWI', self.read_image('src/Component/Mobil/arduino.jpg'), 'ESEMKA', 'Hitam', 2019, 0),
                    ('RI 1', self.read_image('src/Component/Mobil/bater.jpg'), 'MV3 Garuda', 'Putih', 2025, 1),
                    ('D 1715 HN', self.read_image('src/Component/Mobil/battery.jpeg'), 'Toyota Avanza', 'Cream', 2007, 1),
                    ('D 1120 HX', self.read_image('src/Component/Mobil/Nice.jpeg'), 'Pagani Huayra', 'Biru', 2021, 1),
                    ('KT 1 A', self.read_image('src/Component/Mobil/battery.jpeg'), 'Porsche 911 GT3', 'Putih', 2021, 1),
                    ('B 1', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model S', 'Hitam', 2020, 1),
                    ('B 2', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 3', 'Putih', 2020, 1),
                    ('B 3', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model X', 'Hitam', 2020, 1),
                    ('B 4', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model Y', 'Putih', 2020, 1),
                    ('B 5', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Cybertruck', 'Hitam', 2020, 1),
                    ('B 6', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Roadster', 'Putih', 2020, 1),
                    ('B 7', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Semi', 'Hitam', 2020, 1),
                    ('B 8', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 2', 'Putih', 2020, 1),
                    ('B 9', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 4', 'Hitam', 2020, 1),
                    ('B 10', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 5', 'Putih', 2020, 1),
                    ('B 11', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 6', 'Hitam', 1945, 1),
                    ('B 12', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 7', 'Putih', 1945, 1),
                    ('B 13', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 8', 'Hitam', 1945, 1),
                    ('B 14', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 9', 'Putih', 1945, 1),
                    ('B 15', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 10', 'Hitam', 1945, 1),
                    ('B 16', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 11', 'Putih', 1945, 1),
                    ('B 17', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 12', 'Hitam', 1945, 1),
                    ('B 18', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 13', 'Putih', 1945, 1),
                    ('B 19', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 14', 'Hitam', 1945, 1),
                    ('B 20', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 15', 'Putih', 1945, 1),
                    ('B 21', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 16', 'Hitam', 1945, 1),
                    ('B 22', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 17', 'Putih', 1945, 1),
                    ('B 23', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 18', 'Hitam', 1945, 1),
                    ('B 24', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 19', 'Putih', 1945, 1),
                    ('B 25', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 20', 'Hitam', 1945, 1),
                    ('B 26', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 21', 'Putih', 1945, 1),
                    ('B 27', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 22', 'Hitam', 1945, 1),
                    ('B 28', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 23', 'Putih', 1945, 1),
                    ('B 29', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 24', 'Hitam', 1945, 1),
                    ('B 30', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 25', 'Putih', 1945, 1),
                    ('B 31', self.read_image('src/Component/Mobil/battery.jpeg'), 'Tesla Model 26', 'Hitam', 1945, 1),
                    # Add more sample data as needed
                ]
                
                cursor.executemany('''
                    INSERT INTO Mobil (NomorPlat, Gambar, Model, Warna, Tahun, StatusKetersediaan)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sample_data)
                
            conn.commit()
            
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

    def read_image(self, file_path):
        """Read an image file from the given path."""
        with open(file_path, 'rb') as file:
            return file.read()

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

    def filter_mobil(self, color=None, year=None, limit=10, offset=0):
        """Filter Mobil objects based on color and year with pagination."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = 'SELECT * FROM Mobil WHERE 1=1'
            params = []
            if color:
                query += ' AND Warna = ?'
                params.append(color)
            if year:
                query += ' AND Tahun = ?'
                params.append(year)
            query += ' LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Mobil(*row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Error filtering Mobil: {e}")
            return []
            
        finally:
            if conn:
                conn.close()