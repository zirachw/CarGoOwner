CREATE TABLE Mobil (
    NomorPlat VARCHAR(20) PRIMARY KEY,
    Gambar BLOB,
    Model VARCHAR(100) NOT NULL,
    Warna VARCHAR(50),
    Tahun INT NOT NULL,
    StatusKetersediaan BOOLEAN NOT NULL
);

CREATE TABLE Pelanggan (
    NIK VARCHAR(20) PRIMARY KEY,
    Nama VARCHAR(100) NOT NULL,
    Kontak VARCHAR(50) NOT NULL,
    Alamat VARCHAR(255),
    CreditPoint INT DEFAULT 0,
    StatusPinjam BOOLEAN DEFAULT FALSE
);

CREATE TABLE Peminjaman (
    IDPeminjaman INT AUTO_INCREMENT PRIMARY KEY,
    NomorPlat VARCHAR(20) NOT NULL,
    NIK VARCHAR(20) NOT NULL,
    Nama VARCHAR(100) NOT NULL,
    Kontak VARCHAR(50) NOT NULL,
    TanggalPeminjaman DATETIME NOT NULL,
    TanggalPengembalian DATETIME,
    TanggalPembayaran DATETIME,
    TenggatPengembalian DATETIME NOT NULL,
    TenggatPembayaran DATETIME NOT NULL,
    BesarPembayaran BIGINT NOT NULL,
    StatusPengembalian BOOLEAN DEFAULT FALSE,
    StatusPembayaran BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (NomorPlat) REFERENCES Mobil(NomorPlat),
    FOREIGN KEY (NIK) REFERENCES Pelanggan(NIK)
);

CREATE TABLE Notifikasi (
    IDNotif INT AUTO_INCREMENT PRIMARY KEY,
    IDPeminjaman INT NOT NULL,
    JenisNotif VARCHAR(50) NOT NULL,
    TanggalNotif DATETIME NOT NULL,
    FOREIGN KEY (IDPeminjaman) REFERENCES Peminjaman(IDPeminjaman)
);
