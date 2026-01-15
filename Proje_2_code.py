class Book :
    def __init__(self, book, author, year):
        self.book = book
        self.author = author
        self.year = year

    def __str__  (self):
        return (f"kitap adı => {self.book}\nyazar adı => {self.author}\nyayın yılı => {self.year}\n")

class Library :
    def __init__(self):
        self.books = []

    # kitap ekleme fonksiyonu.

    def add_book(self, book,author, year):

        new_book = Book(book, author, year)
        self.books.append(new_book)
        print(f"Yeni kitap başarıyla eklendi >>\"{book}\"<<")
        return new_book 

    # kitaplari listele fnksiyonu.
    def list_books (self) :
        if not self.books :
            print("Kütüphanede Kitap Yok")
            return
        print("Kütüphanedeki Kitaplar:")
        for book in self.books :
            print(book)

    # Kitabin ismiyle arama. 
    def search_by_name(self, name):
        found = False
        for b in self.books :
            if b.book.lower() == name.lower():
                print(b)
                found = True

        if not found :
            print ("Kitap Bulunamadı.")

    # yazarin ismiyle arama.
    def search_by_author(self, author) : 
        found = False # kitabi bulunca "True" olur.
        for b in self.books :
            if b.author.lower() == author.lower():
                print(b)
                found = True # Kitab bulundu.
        if not found :
            print ("Bu yazara ait kitap Bulunamadı.")



    def remove_book (self, name) :
        for b in self.books :
            if b.book.lower() == name.lower() :
                self.books.remove(b)
                print(f"Kitap silindi >>{name}<<")
                return
        print("Silinecek kitap bulunamadi")


library_1 = Library()

while True:
    print("\nBeytül Hikmet kütüphanesine hoşgeldiniz\n")
    print("1. Kitap ekle")
    print("2. Kitap sil")
    print("3. Kitabı ismiyle ara")
    print("4. Kitabı yazarıyla ara")
    print("5. Tüm kitapları listele")
    print("6. Çıkış")

    choice = input("İşlem seç (1-6): ")

    if choice == "1":
        name = input("\nKitap adı: ")
        author = input("Yazar adı: ")
        try:
            year = int(input("Yayın yılı: "))
        except ValueError:
            print("Lütfen sayı giriniz")
            continue

        library_1.add_book(name, author, year)
    
    elif choice == "2":
        name = input("\nSilinecek kitap adı: ")

        library_1.remove_book(name)

    elif choice == "3":
        name = input("\nKitap adı: ")
        
        library_1.search_by_name(name)

    elif choice == "4":
        author = input("\nYazar adı:")
        
        library_1.search_by_author(author)

    elif choice == "5":
        print("\n")
        library_1.list_books()
    elif choice == "6":
        break

    else:
        print("\nGeşersiz seçim!")
