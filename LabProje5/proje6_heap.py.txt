import re

class WordNode:
    def __init__(self,word):
        self.word = word
        self.count = 1  # Kelime ilk eklendiğinde frekansı 1 olarak başlar

    def __lt__(self, other):
        # İlk anahtar: ilk harfin alfabetik sırası (Min-Heap)
        char_self = self.word[0].lower()
        char_other = other.word[0].lower()
        
        if char_self != char_other:
            return char_self <char_other
        # İkinci anahtar: İlk harf eşitse tekrar sayısını kontrol eder (Max-Heap)
        if self.count != other.count:
            return self.count >other.count
        # Ekstra güvenlik: Hem ilk harf hem frekans aynıysa tüm kelimeyi alfabetik sıralar
        return self.word.lower()<other.word.lower()
    
    def __repr__(self):
        return f"{self.word}({self.count})" # Düğümü yazdırırken Kelime formatını sağlar
    
class CustomHeap:
    def __init__(self):
        self.heap=[]    # Heap elemanlarını tutacağımız dinamik dizi

    def get_parent_index(self,index):   # Ağaç yapısındaki ebeveyn ve çocuk indekslerini bulma formülleri
        return (index-1)//2
    
    def get_left_child_index(self,index):
        return 2*index +1
    
    def get_right_child_index(self,index):
        return 2*index +2
    
    def swap(self, i, j):
        "İki düğümün dizideki yerlerini değiştirir"
        self.heap[i],self.heap[j] = self.heap[j],self.heap[i]

    def search_and_update(self,word):
        "Kelimeyi arayın, bulursanız tekrarı artırın, yükseltin."
        for i in range(len(self.heap)):
            if self.heap[i].word.lower() ==word.lower():
                self.heap[i].count +=1
                self.heapify_up(i)  # Frekans arttığı için yukarı çıkma ihtimali var
                return True
        return False
    
    def insert(self,word):
        "Yeni bir kelime ekleyin veya mevcut bir kelimeyi güncelleyin."
        if self.search_and_update(word):    # Kelime zaten varsa işlem search_and_update içinde halledilir
            return
        # Kelime yoksa yeni düğüm oluştur, sona ekle ve yukarı taşı
        new_node = WordNode(word)
        self.heap.append(new_node)
        self.heapify_up(len(self.heap)-1)

    def heapify_up(self,index):
        "Düğümün önceliği üst öğeden daha yüksekse en üst sıraya yükseltilir."
        parent_index = self.get_parent_index(index)
        while index > 0 and self.heap[index] < self.heap[parent_index]:
            self.swap(index,parent_index)
            index = parent_index
            parent_index = self.get_parent_index(index)

    def heapify_down(self,index):
        "Düğüm çekildikten sonra yığının düzenini korumak için aşağı iner."
        smallest = index
        left_child = self.get_left_child_index(index)
        right_child = self.get_right_child_index(index)
        size = len(self.heap)

        if left_child <size and self.heap[left_child]< self.heap[smallest]:
            smallest = left_child

        if right_child < size and self.heap[right_child]<self.heap[smallest]:
            smallest = right_child

        if smallest != index:
            self.swap(index,smallest)
            self.heapify_down(smallest)     # Özyineli (recursive) olarak aşağı inmeye devam et

    def extract(self):
        "En yüksek önceliğe (kök) sahip düğümü sürükleyip kaldırır."
        if len(self.heap)==0:
            return None
        if len(self.heap)==1:
            return self.heap.pop()
        
        root = self.heap[0]     # En öncelikli elemanı sakla
        self.heap[0]=self.heap.pop()    # En sondaki elemanı köke taşı
        self.heapify_down(0)    # Yeni kökü aşağı doğru kaydırarak dengele
        return root
    
def process_file(file_path):
    my_heap = CustomHeap()

    try:
        with open(file_path,"r",encoding="utf-8") as file:
            text = file.read()      # Noktalama işaretlerini yoksay ve sadece harflerden oluşan kelimeleri bulur
            # Yalnızca kelimeleri çıkarın ve virgülleri ve noktaları göz ardı edin
            words = re.findall(r"[a-zA-ZçğıöşüÇĞIÖŞÜ]+",text)
            
            for word in words:
                my_heap.insert(word)

    except FileNotFoundError:
        print(f"Hata: '{file_path}' dosyası bulunamadı.")
        return
    
    print("Sonuçlar önce ilk harfe (min-heap) sonra frekansa (max-heap) göre sıralanır:")
    print("="*60)

    extracted_node = my_heap.extract()  # Sıralı çıktıyı yazdırmak için ağaç boşalana kadar kök elemanı çekiyor
    while extracted_node is not None:
        print(f"=> {extracted_node.word}({extracted_node.count})")
        extracted_node = my_heap.extract()
print("="*60)

if __name__== "__main__":
    file_name = "test_metni.txt"
    process_file(file_name)
        
print("="*60)

        


            