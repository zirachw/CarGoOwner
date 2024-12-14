PRAGMA foreign_keys = ON;

CREATE TABLE Mobil (
    NomorPlat TEXT PRIMARY KEY,  
    Gambar BLOB,
    Model TEXT NOT NULL,         
    Warna TEXT,                  
    Tahun INTEGER NOT NULL,
    StatusKetersediaan INTEGER NOT NULL CHECK (StatusKetersediaan IN (0, 1))  
);

CREATE TABLE Pelanggan (
    NIK TEXT PRIMARY KEY,        
    Nama TEXT NOT NULL,          
    Kontak TEXT NOT NULL,        
    Alamat TEXT,                 
    CreditPoint INTEGER DEFAULT 0,
    StatusPinjam INTEGER DEFAULT 0 CHECK (StatusPinjam IN (0, 1))  
);

CREATE TABLE Peminjaman (
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
);