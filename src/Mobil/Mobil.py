class Mobil:
    def __init__(self, nomor_plat, gambar, model, warna, tahun, status_ketersediaan):
        """Initialize the Mobil class."""
        self.nomor_plat = nomor_plat
        self.gambar = gambar
        self.model = model
        self.warna = warna
        self.tahun = tahun
        self.status_ketersediaan = status_ketersediaan

    def get_mobil(self):
        """Return the Mobil object."""
        return self
    
    def get_mobil_by_cat(self, category):
        """Return the Mobil object by category."""
        # Implement logic to filter by category if needed
        return self
    
    def set_mobil(self, nomor_plat, gambar, model, warna, tahun, status_ketersediaan):
        """Set the Mobil object."""
        self.nomor_plat = nomor_plat
        self.gambar = gambar
        self.model = model
        self.warna = warna
        self.tahun = tahun
        self.status_ketersediaan = status_ketersediaan

    def __str__(self):
        """Return a string representation of the Mobil object."""
        return f"Mobil({self.nomor_plat}, {self.model}, {self.warna}, {self.tahun}, {self.status_ketersediaan})"