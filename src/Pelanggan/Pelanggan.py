import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from pathlib import Path

@dataclass
class Pelanggan:
    NIK: str
    Nama: str
    Kontak: str
    Alamat: str
    CreditPoint: int
    StatusPinjam: bool
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "Database/CarGoOwner.db"

    def getPelanggan(self, page: int, items_per_page: int) -> Tuple[List[Dict[str, Any]], int]:
        try:
            print(self.db_path)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM Pelanggan')
            total_records = cursor.fetchone()[0]
            
            offset = (page - 1) * items_per_page
            cursor.execute('''
                SELECT * FROM Pelanggan 
                LIMIT ? OFFSET ?
            ''', (items_per_page, offset))
            
            columns = ['NIK', 'Nama', 'Kontak', 'Alamat', 'CreditPoint', 'StatusPinjam']
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return data, total_records
            
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving customer data: {str(e)}")
        finally:
            if conn:
                conn.close()

    def setPelanggan(self, pelanggan: Dict[str, Any], mode: str = "create") -> bool:
        """Create, update, or delete customer data in the database.
        
        Args:
            pelanggan: Dictionary containing customer data
            mode: Operation mode - "create", "edit", or "delete"
            
        Returns:
            bool: True if operation was successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if mode == "create":
                cursor.execute('''
                    INSERT INTO Pelanggan (NIK, Nama, Kontak, Alamat, CreditPoint, StatusPinjam)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pelanggan['NIK'],
                    pelanggan['Nama'],
                    pelanggan['Kontak'],
                    pelanggan['Alamat'],
                    pelanggan.get('CreditPoint', 100),  # Default credit point
                    pelanggan.get('StatusPinjam', 0)    # Default status
                ))
            elif mode == "edit":
                cursor.execute('''
                    UPDATE Pelanggan 
                    SET NIK = ?, Nama = ?, Kontak = ?, Alamat = ?
                    WHERE NIK = ?
                ''', (
                    pelanggan['NIK'],
                    pelanggan['Nama'],
                    pelanggan['Kontak'],
                    pelanggan['Alamat'],
                    pelanggan['original_NIK']  # Original NIK for identification
                ))
            elif mode == "delete":
                niks = pelanggan['NIKs'] if isinstance(pelanggan['NIKs'], list) else [pelanggan['NIKs']]
                cursor.executemany(
                    'DELETE FROM Pelanggan WHERE NIK = ?',
                    [(nik,) for nik in niks]
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

    def getAllNIKs(self) -> set:

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT NIK FROM Pelanggan')
            return {row[0] for row in cursor.fetchall()}
            
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving NIKs: {str(e)}")
        finally:
            if conn:
                conn.close()