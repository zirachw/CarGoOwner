import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                           QFrame, QSizePolicy, QCheckBox, QToolButton, QDesktopWidget)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QIcon
import sqlite3
from pathlib import Path

class Peminjaman:
    def __init__(self, parent=None):
        self.db_path = Path(__file__).parent.parent / "Database/CarGoOwner.db"

    def FilterNotifikasi(self, task, current_page, items_per_page):
        if task == "Jadwal Pengembalian":
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM Peminjaman')
                totalRecords = cursor.fetchone()[0]

                offset = (current_page - 1) * items_per_page
                cursor.execute(f'''
                    SELECT ID, NIK, Nama, Kontak, NomorPlat, TanggalPeminjaman, TanggalPengembalian, StatusPengembalian FROM Peminjaman
                    WHERE StatusPengembalian = 0 AND TenggatPengembalian < DATE(CURRENT_TIMESTAMP, '+7 hours')
                    LIMIT ?
                    OFFSET ?
                ''', (items_per_page, offset))

                columns = ['ID', 'NIK', 'Nama', 'Kontak', 'NomorPlat', 'TanggalPeminjaman', 'TanggalPengembalian', 'StatusPengembalian']
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return data, totalRecords
            
            except sqlite3.Error as e:
                print(f"Error loading data: {e}")
            
            finally:
                if conn:
                    conn.close()

        elif task == "Pembayaran Rental":
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM Peminjaman')
                totalRecords = cursor.fetchone()[0]

                offset = (current_page - 1) * items_per_page
                cursor.execute(f'''
                    SELECT ID, NIK, Nama, Kontak, NomorPlat, TenggatPembayaran, BesarPembayaran, StatusPembayaran FROM Peminjaman
                    WHERE StatusPembayaran = 0 AND TenggatPembayaran < DATE(CURRENT_TIMESTAMP, '+7 hours')
                    LIMIT ?
                    OFFSET ?
                ''', (items_per_page, offset))

                columns = ['ID', 'NIK', 'Nama', 'Kontak', 'NomorPlat', 'TenggatPembayaran', 'BesarPembayaran', 'StatusPembayaran']
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return data, totalRecords
            
            except sqlite3.Error as e:
                print(f"Error loading data: {e}")
            
            finally:
                if conn:
                    conn.close()

    def FilterLaporan(self, task, month, current_page, items_per_page):
        """
        Filter and fetch report data based on task type and period.
        
        Args:
            task (str): Type of report to generate (e.g., "Pendapatan")
            month (str): Month filter (e.g., "Jan", "Feb", or "All Periode")
            current_page (int): Current page number for pagination
            items_per_page (int): Number of items to display per page
            
        Returns:
            tuple: (list of data dictionaries, total record count)
        """
        if task == "Pendapatan":
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Base query parts
                select_clause = """
                    SELECT ID, Nama, TanggalPeminjaman, TanggalPengembalian, 
                           TanggalPembayaran, BesarPembayaran,
                           CAST(BesarPembayaran AS INTEGER) as IntBesarPembayaran
                    FROM Peminjaman
                """
                
                # Add month filter if specific month selected
                if month != 'All Periode':
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
                    month_idx = month_names.index(month) + 1
                    select_clause += f" AND strftime('%m', TanggalPembayaran) = '{month_idx:02d}'"

                # Get total count
                count_query = f"SELECT COUNT(*) FROM ({select_clause})"
                cursor.execute(count_query)
                total_records = cursor.fetchone()[0]

                # Add pagination
                offset = (current_page - 1) * items_per_page
                select_clause += f" LIMIT {items_per_page} OFFSET {offset}"
                
                # Execute main query
                cursor.execute(select_clause)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                columns = ['ID', 'Nama', 'TanggalPeminjaman', 'TanggalPengembalian',
                          'TanggalPembayaran', 'BesarPembayaran', 'IntBesarPembayaran']
                data = [dict(zip(columns, row)) for row in rows]

                return data, total_records

            except sqlite3.Error as e:
                print(f"Error loading data: {e}")
                return [], 0
                
            finally:
                if conn:
                    conn.close()        