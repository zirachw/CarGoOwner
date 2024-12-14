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
                    LIMIT ?
                    OFFSET ?
                ''', (items_per_page, offset))

                columns = ['ID', 'NIK', 'Nama', 'Kontak', 'NomorPlat', 'TanggalPeminjaman', 'TanggalPengembalian', 'StatusPengembalian']
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(data)

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

