import os
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from pathlib import Path

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
    Status: int
    
    def __init__(self):
        """Initialize database connection and setup"""
        self.db_path = Path(__file__).parent.parent / "Database/CarGoOwner.db"
        self.schema_path = Path(__file__).parent.parent / "schema.sql"
            
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

    def get_mobil_filtered(self, page: int, items_per_page: int, year: int = None, color: str = None) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve paginated customer data from the database with optional filters for year and color.
        
        Args:
            page: Current page number
            items_per_page: Number of items per page
            year: Optional filter for the year
            color: Optional filter for the color
            
        Returns:
            Tuple containing list of customer data and total number of records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build the query with optional filters
            query = 'SELECT * FROM Mobil WHERE 1=1'
            params = []
            
            if year is not None:
                query += ' AND Tahun = ?'
                params.append(year)
                
            if color is not None:
                query += ' AND Warna = ?'
                params.append(color)
                
            # Get total count with filters
            count_query = f'SELECT COUNT(*) FROM ({query})'
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            print(total_records)
            
            # Add pagination to the query
            query += ' LIMIT ? OFFSET ?'
            params.extend([items_per_page, (page - 1) * items_per_page])
            
            cursor.execute(query, params)
            
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