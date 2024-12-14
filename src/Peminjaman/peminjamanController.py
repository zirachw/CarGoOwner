import os
import sqlite3
import datetime

class PeminjamanController:
    def __init__(self, schema_path):
        # Initialize database paths
        self.schema_path = schema_path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(schema_path)))
        self.db_path = os.path.join(self.base_dir, "src/CarGoOwnerPeminjaman.db")
        
        # Initialize the database
        self.init_database()

    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            # Create required tables
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

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Pelanggan (
                    NIK TEXT PRIMARY KEY,
                    Nama TEXT NOT NULL,
                    Kontak TEXT NOT NULL,
                    Alamat TEXT NOT NULL,
                    CreditPoint INTEGER DEFAULT 0,
                    StatusPinjam INTEGER DEFAULT 0 CHECK (StatusPinjam IN (0, 1))
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Peminjaman (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nama TEXT NOT NULL,
                    NIK TEXT NOT NULL,
                    NomorPlat TEXT NOT NULL,
                    Kontak TEXT NOT NULL,
                    TanggalPeminjaman DATE NOT NULL,
                    TanggalPengembalian DATE,
                    TanggalPembayaran DATE,
                    TenggatPengembalian DATE NOT NULL,
                    TenggatPembayaran DATE NOT NULL,
                    BesarPembayaran INTEGER NOT NULL,
                    StatusPengembalian INTEGER DEFAULT 0 CHECK (StatusPengembalian IN (0, 1)),
                    StatusPembayaran INTEGER DEFAULT 0 CHECK (StatusPembayaran IN (0, 1)),
                    FOREIGN KEY (NomorPlat) REFERENCES Mobil(NomorPlat),
                    FOREIGN KEY (NIK) REFERENCES Pelanggan(NIK)
                )
            ''')

            # Clear existing data
            # cursor.execute('DELETE FROM Mobil')
            # cursor.execute('DELETE FROM Pelanggan')
            # cursor.execute('DELETE FROM Peminjaman')
            cursor.execute('SELECT COUNT(*) FROM Mobil')
            if cursor.fetchone()[0] == 0:
                sample_mobil = [
                    ('AB1234CD', None, 'Avanza', 'Merah', 2020, 1),
                    ('B5678EF', None, 'Jazz', 'Biru', 2021, 1),
                    ('C9101GH', None, 'Ertiga', 'Putih', 2019, 0),
                    ('D2345IJ', None, 'Livina', 'Hitam', 2020, 1),
                    ('E6789KL', None, 'Xpander', 'Abu-Abu', 2021, 0),
                ]
                cursor.executemany('''
                    INSERT INTO Mobil (NomorPlat, Gambar, Model, Warna, Tahun, StatusKetersediaan)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sample_mobil)

            # Insert sample data for Pelanggan if the table is empty
            cursor.execute('SELECT COUNT(*) FROM Pelanggan')
            if cursor.fetchone()[0] == 0:
                sample_pelanggan = [
                    ('3201234567890123', 'John Doe', 'Jl. Sudirman No. 1', '081234567890'),
                    ('3209876543210987', 'Jane Smith', 'Jl. Thamrin No. 2', '082345678901'),
                    ('3205678901234567', 'Michael Johnson', 'Jl. Merdeka No. 3', '083456789012'),
                    ('3203456789012345', 'Emily Davis', 'Jl. Gajah Mada No. 4', '084567890123'),
                    ('3201230987654321', 'Robert Brown', 'Jl. Diponegoro No. 5', '085678901234'),
                ]
                cursor.executemany('''
                    INSERT INTO Pelanggan (NIK, Nama, Alamat, Kontak)
                    VALUES (?, ?, ?, ?)
                ''', sample_pelanggan)

            # Insert sample data for Peminjaman if the table is empty
            cursor.execute('SELECT COUNT(*) FROM Peminjaman')
            if cursor.fetchone()[0] == 0:
                sample_peminjaman = [
                    ('John Doe', '3201234567890123', 'AB1234CD', '081234567890',
                    '2024-12-01', '2024-12-07', '2024-12-07',
                    '2024-12-07', '2024-12-07', 500000, 1, 1),
                    ('Jane Smith', '3209876543210987', 'B5678EF', '082345678901',
                    '2024-12-02', None, None, '2024-12-08', '2024-12-08',
                    600000, 0, 0),
                    ('Michael Johnson', '3205678901234567', 'C9101GH', '083456789012',
                    '2024-11-28', '2024-12-05', '2024-12-05',
                    '2024-12-05', '2024-12-05', 450000, 1, 1),
                    ('Emily Davis', '3203456789012345', 'D2345IJ', '084567890123',
                    '2024-11-30', None, None, '2024-12-06', '2024-12-06',
                    550000, 0, 0),
                    ('Robert Brown', '3201230987654321', 'E6789KL', '085678901234',
                    '2024-12-03', None, None, '2024-12-09', '2024-12-09',
                    700000, 0, 0),
                ]
                cursor.executemany('''
                    INSERT INTO Peminjaman (Nama, NIK, NomorPlat, Kontak, TanggalPeminjaman, 
                                            TanggalPengembalian, TanggalPembayaran, 
                                            TenggatPengembalian, TenggatPembayaran, 
                                            BesarPembayaran, StatusPengembalian, StatusPembayaran)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_peminjaman)

            conn.commit()
            print("Database initialized successfully.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()


    def fetch_peminjaman(self, offset=0, limit=10):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Nama, NIK, NomorPlat, Kontak, TanggalPeminjaman, TanggalPengembalian, 
                    TanggalPembayaran, TenggatPengembalian, BesarPembayaran, 
                    StatusPengembalian, StatusPembayaran
                FROM Peminjaman
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            records = cursor.fetchall()
            return records
        except sqlite3.Error as e:
            print(f"Error fetching Peminjaman: {e}")
            return []
        finally:
            if conn:
                conn.close()


    def fetch_total_peminjaman_count(self):
        """Fetch total count of Peminjaman records."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM Peminjaman')
            count = cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            print(f"Error fetching Peminjaman count: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def delete_peminjaman(self, peminjaman_ids):
        """Delete Peminjaman records by IDs."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.executemany('DELETE FROM Peminjaman WHERE ID = ?', [(id,) for id in peminjaman_ids])
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting Peminjaman: {e}")
            return False
        finally:
            if conn:
                conn.close()
    def get_available_pelanggan(self):
        """Fetch available Pelanggan (customers) who are not currently borrowing."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query to fetch Pelanggan where StatusPinjam is 0 (not currently borrowing)
            cursor.execute('SELECT NIK, Nama,Kontak FROM Pelanggan WHERE StatusPinjam = 0')
            available_pelanggan = cursor.fetchall()  # Returns a list of tuples (NIK, Nama)
            return available_pelanggan
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_available_mobil(self):
        """Fetch available Mobil (cars) that are not currently borrowed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query to fetch Mobil where StatusKetersediaan is 1 (available)
            cursor.execute('SELECT NomorPlat, Model FROM Mobil WHERE StatusKetersediaan = 1')
            available_mobil = cursor.fetchall()  # Returns a list of tuples (NomorPlat, Model)
            return available_mobil
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def add_peminjaman(self, nama, nik, nomor_plat, kontak, tanggal_peminjaman, tenggat_pengembalian, tenggat_pembayaran, besar_pembayaran):
        """Add a new peminjaman record to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Peminjaman (
                    Nama, NIK, NomorPlat, Kontak, TanggalPeminjaman, TenggatPengembalian, 
                    TenggatPembayaran, BesarPembayaran, StatusPengembalian, StatusPembayaran
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
            ''', (nama, nik, nomor_plat, kontak, tanggal_peminjaman, tenggat_pengembalian, tenggat_pembayaran, besar_pembayaran))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error while adding peminjaman: {e}")
            return False
        finally:
            if conn:
                conn.close()

