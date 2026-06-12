import mysql.connector

class DatabaseManager:
    def __init__(self):
        # xampp sunucu bağlantısı
        self.host = "127.0.0.1"
        self.user = "root" #kullnıcı adı
        self.password = "" 
        self.database = "netflixDB" #veritabanının adı
        self.connection = None
        self.cursor = None

    def connect(self):
        # veri tabanına bağlayan fonksiyon
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )

            #dictionary formatında çekmek için =true yaptık
            self.cursor = self.connection.cursor(dictionary=True)
            print("Bağlantı Başarıyla kuruldu!!")
            return True
        except mysql.connector.Error as err:
            print(f"Bağlantı kurulmadı : {err}")
            return False
        
    def close_connection(self):
        # bağlantıyı kapatatan fonksiyon
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Bağlantı koptu!!.")

# bağlantını başarlı olup olamadığını kontrol eder
if __name__== "__main__":
    db = DatabaseManager()
    db.connect()
    db.close_connection()







