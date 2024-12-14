class NotifikasiController:
    def __init__(self):
        self.currentTask = None

    def setNotifTask(self, task_name):
        self.currentTask = task_name

    def clickedJadwalPengembalian(self):
        self.setNotifTask("Jadwal Pengembalian")

    def clickedPembayaranRental(self):
        self.setNotifTask("Pembayaran Rental")
        
    def getNotifTask(self):
        print("Current Task: ", self.currentTask)
        return self.currentTask