import sqlite3
import random
import os
from datetime import datetime, timedelta

import sqlite3
import random
import os
from datetime import datetime, timedelta

class DatabaseManager:
    """Manages all database operations for the CarGoOwner application including setup,
    initialization, and dummy data generation."""
    
    def __init__(self):
        """Initialize the database manager and set up necessary paths."""
        # Calculate base path by going up two levels from this file
        current_file_path = os.path.abspath(__file__)
        src_dir = os.path.dirname(os.path.dirname(current_file_path))
        self.base_path = os.path.dirname(src_dir)
        
        # Set up database paths
        self.setupPaths()
        
    def setupPaths(self):
        """Set up all database-related paths and ensure directories exist."""
        self.db_dir = os.path.join(self.base_path, 'src', 'Database')
        
        # Create database directory if it doesn't exist
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
            print(f"Created database directory at {self.db_dir}")
            
        self.db_path = os.path.join(self.db_dir, 'CarGoOwner.db')
        self.schema_path = os.path.join(self.db_dir, 'schema.sql')

        print(f"Database path: {self.db_path}")
        print(f"Schema path: {self.schema_path}")

    def createDatabase(self):
        """Create a fresh database with dummy data.
        
        This method will:
        1. Remove any existing database
        2. Create a new database and tables
        3. Generate fresh dummy data for all tables
        
        Returns:
            bool: True if database creation was successful
        """
        try:
            # Remove existing database if it exists
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print("Removed existing database")
            
            # Create new database and tables
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Read and execute schema.sql
            with open(self.schema_path, 'r') as schema_file:
                schema_script = schema_file.read()
                cursor.executescript(schema_script)
            
            conn.commit()
            print("✓ Database schema created")
            
            # Generate dummy data for each table
            self.initializeMobil()
            print("✓ Mobil data generated")
            
            self.initializePelanggan()
            print("✓ Pelanggan data generated")
            
            self.initializePeminjaman()
            print("✓ Peminjaman data generated")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            return False

    def initializeMobil(self):
        """Generate dummy data for car inventory with realistic models and details."""
        # Define realistic car data pools
        car_models = [
            ('Toyota', ['Avanza', 'Innova', 'Camry', 'Corolla', 'Rush']),
            ('Honda', ['Civic', 'CR-V', 'HR-V', 'Brio', 'Jazz']),
            ('Suzuki', ['Ertiga', 'XL7', 'Baleno', 'Swift', 'Ignis']),
            ('Mitsubishi', ['Xpander', 'Pajero', 'Eclipse Cross', 'Outlander']),
            ('Daihatsu', ['Xenia', 'Terios', 'Ayla', 'Sigra', 'Rocky'])
        ]
        
        img_random = ['./src/Component/Mobil/mobil1.jpg', './src/Component/Mobil/mobil2.jpg', './src/Component/Mobil/mobil3.jpg', './src/Component/Mobil/mobil4.jpg', './src/Component/Mobil/mobil5.jpg','./src/Component/Mobil/mobil6.jpg']

        colors = ['Hitam', 'Putih', 'Silver', 'Merah', 'Biru', 'Abu-abu']
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 1))
        
        try:
            conn = sqlite3.connect(self.db_path)
            print("Connected to database")
            print("path: ", self.db_path)
            cursor = conn.cursor()
            
            # Generate 36 unique cars with Indonesian license plates
            cars_data = []
            used_plates = set()
            
            for _ in range(60):
                brand, models = random.choice(car_models)
                img = open(random.choice(img_random), 'rb').read()
                plate = self._generate_plate()
                while plate in used_plates:
                    plate = self._generate_plate()
                used_plates.add(plate)
                
                cars_data.append((
                    plate,
                    img,  # Gambar (BLOB) is set to None
                    f"{brand} {random.choice(models)}",
                    random.choice(colors),
                    random.choice(years),
                    random.choice([0, 1])  # StatusKetersediaan
                ))
            
            cursor.executemany('''
                INSERT INTO Mobil (NomorPlat, Gambar, Model, Warna, Tahun, StatusKetersediaan)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', cars_data)
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error initializing Mobil table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def initializePelanggan(self):
        """Generate dummy data for customers with realistic Indonesian names and details."""
        # Define data pools for generating realistic Indonesian customer data
        first_names = ['Ahmad', 'Budi', 'Dewi', 'Eko', 'Fitri', 'Gunawan', 'Hadi', 'Indah', 
                      'Joko', 'Kartika', 'Lina', 'Muhammad', 'Nina', 'Oscar', 'Putri', 'Rudi',
                      'Siti', 'Tono', 'Udin', 'Wati']
        
        last_names = ['Kusuma', 'Wijaya', 'Suharto', 'Setiawan', 'Hidayat', 'Nugroho',
                     'Suryadi', 'Hartono', 'Santoso', 'Wibowo', 'Pradana', 'Utama']
        
        cities = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Semarang', 'Malang']
        streets = ['Jalan Sudirman', 'Jalan Thamrin', 'Jalan Gatot Subroto', 'Jalan Merdeka',
                  'Jalan Diponegoro', 'Jalan Ahmad Yani', 'Jalan Pahlawan']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate 60 unique customers
            customers_data = []
            used_niks = set()
            
            for _ in range(60):
                # Generate unique 16-digit NIK
                nik = ''.join([str(random.randint(0, 9)) for _ in range(16)])
                while nik in used_niks:
                    nik = ''.join([str(random.randint(0, 9)) for _ in range(16)])
                used_niks.add(nik)
                
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                phone = f"08{random.randint(100000000, 999999999)}"
                address = f"{random.choice(streets)} No. {random.randint(1, 100)}, {random.choice(cities)}"
                
                customers_data.append((
                    nik,
                    name,
                    phone,
                    address,
                    random.randint(0, 100),  # CreditPoint
                    random.choice([0, 1])    # StatusPinjam
                ))
            
            cursor.executemany('''
                INSERT INTO Pelanggan (NIK, Nama, Kontak, Alamat, CreditPoint, StatusPinjam)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', customers_data)
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error initializing Pelanggan table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def initializePeminjaman(self):
        """Generate dummy rental data maintaining referential integrity with Mobil and Pelanggan tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch existing mobil and pelanggan data to maintain referential integrity
            cursor.execute('SELECT NomorPlat FROM Mobil')
            available_cars = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT NIK, Nama, Kontak FROM Pelanggan')
            available_customers = cursor.fetchall()
            
            # Generate 20 rental records
            rental_data = []
            current_date = datetime.now()
            
            for _ in range(50):
                # Random dates within reasonable range
                rental_date = current_date - timedelta(days=random.randint(0, 60))
                due_return_date = rental_date + timedelta(days=random.randint(3, 14))
                due_payment_date = due_return_date + timedelta(days=1)
                
                # Randomly decide if rental is completed
                is_returned = random.choice([0, 1])
                is_paid = random.choice([0, 1]) if is_returned else 0
                
                return_date = None
                payment_date = None
                if is_returned:
                    return_date = due_return_date + timedelta(days=random.randint(-2, 2))
                    if is_paid:
                        payment_date = return_date + timedelta(days=random.randint(0, 3))
                
                # Select random car and customer
                customer = random.choice(available_customers)
                
                rental_data.append((
                    random.choice(available_cars),  # NomorPlat
                    customer[0],  # NIK
                    customer[1],  # Nama
                    customer[2],  # Kontak
                    rental_date.strftime('%Y-%m-%d'),
                    return_date.strftime('%Y-%m-%d') if return_date else None,
                    payment_date.strftime('%Y-%m-%d') if payment_date else None,
                    due_return_date.strftime('%Y-%m-%d'),
                    due_payment_date.strftime('%Y-%m-%d'),
                    random.randint(500000, 2000000),  # BesarPembayaran
                    is_returned,
                    is_paid
                ))
            
            cursor.executemany('''
                INSERT INTO Peminjaman (
                    NomorPlat, NIK, Nama, Kontak, TanggalPeminjaman,
                    TanggalPengembalian, TanggalPembayaran, TenggatPengembalian,
                    TenggatPembayaran, BesarPembayaran, StatusPengembalian, StatusPembayaran
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', rental_data)
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error initializing Peminjaman table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _generate_plate(self):
        """Generate a random Indonesian license plate number.
        
        Returns:
            str: A formatted license plate number (e.g., 'B 1234 ABC')
        """
        regions = ['B', 'D', 'F', 'AB', 'AD', 'Z']
        numbers = f"{random.randint(1000, 9999)}"
        letters = ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ', k=3))
        return f"{random.choice(regions)} {numbers} {letters}"