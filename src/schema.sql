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
    NomorPlat TEXT NOT NULL,
    NIK TEXT NOT NULL,
    Nama TEXT NOT NULL,         
    Kontak TEXT NOT NULL,       
    TanggalPeminjaman DATETIME NOT NULL,
    TanggalPengembalian DATETIME,
    TanggalPembayaran DATETIME,
    TenggatPengembalian DATETIME NOT NULL,
    TenggatPembayaran DATETIME NOT NULL,
    BesarPembayaran INTEGER NOT NULL, 
    StatusPengembalian INTEGER DEFAULT 0 CHECK (StatusPengembalian IN (0, 1)), 
    StatusPembayaran INTEGER DEFAULT 0 CHECK (StatusPembayaran IN (0, 1)),     
    FOREIGN KEY (NomorPlat) REFERENCES Mobil(NomorPlat),
    FOREIGN KEY (NIK) REFERENCES Pelanggan(NIK)
);

CREATE TABLE Notifikasi (
    IDNotif INTEGER PRIMARY KEY AUTOINCREMENT,  
    IDPeminjaman INTEGER NOT NULL,
    JenisNotif TEXT NOT NULL,                 
    TanggalNotif DATETIME NOT NULL,
    FOREIGN KEY (IDPeminjaman) REFERENCES Peminjaman(IDPeminjaman)
);
