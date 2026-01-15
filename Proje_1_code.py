
import random

words = ["lion", "tiger", "elephant", "monkey", "zebra", "giraffe", "dog", "cat", "horse", "rabbit",
"apple", "banana", "orange", "grape", "mango", "strawberry", "cherry", "peach", "pear", "watermelon"]

animals = ["lion", "tiger", "elephant", "monkey", "zebra", "giraffe", "dog", "cat", "horse", "rabbit"]
fruits = ["apple", "banana", "orange", "grape", "mango", "strawberry", "cherry", "peach", "pear", "watermelon"]


def display_hangman(tries):
    stages = [
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / \\
           -
        """,
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / 
           -
        """,
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |      
           -
        """,
        """
           --------
           |      |
           |      O
           |     \\|
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |      |
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |    
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      
           |    
           |
           |
           -
        """
    ]
    return stages[tries]


# islem yapma fonksiyonuna alakali random harf gosterme fonksiyonu
def open_random_let (word, guessed_word): 
    hidden_indexs = [] 

    for i, letter in enumerate(guessed_word):

        if letter == "_":
            hidden_indexs.append(i)

    if not hidden_indexs:
        print ("Kelime zaten görünüyor!")
        return guessed_word 

    choose_ind = random.choice(hidden_indexs)

    guessed_word[choose_ind] = word[choose_ind]
    print(f"Gizli Harf Açıldı: '{word[choose_ind]}' ")
    return guessed_word 


# islem yapma fonksiyonu 
def solve_math(word, guessed_word, tries, bonus):
    print("=== İşlem çöz ===")
    print("İşlem seç yada çıkmak için 'iptal' yaz")
    # operation
    op = input("İşlem (+ - * /) yada 'iptal'").strip()

    if op.lower() == "iptal":
        print("Hiç bir şey değiştirmeden çıktın.")
        return tries , bonus , guessed_word
    

    if op not in {"+", "-", "*", "/"}:
        print("yanlış işlem seçimi, oyuna devam.")
        return tries , bonus , guessed_word
    
    # sayilari girme
    try :
        num_1 = float(input("Birinci sayıyı gir.").strip())
        num_2 = (input("İkinci sayıyı gir. (yada çıkmak için 'iptal')").strip())

        if num_2 == 'iptal': 
            print("Hiç bşr şey değiştirmeden çıktın.") 
            return tries , bonus , guessed_word
        
        num_2 = float(num_2)

    except ValueError :
        print ("Geçersiz sayı değeri, Oyuna dönüyorsun.")
        return tries , bonus , guessed_word

    # sifira bolme sarti
    if op == "/" and num_2 == 0:
        print("Error! sıfıra bölmek yanlış! kalan hata hakkından -1!")
        tries -= 1 
        return tries , bonus , guessed_word 
    
    # islemler
    if op == "+":
        correct_result = num_1 + num_2
    elif op == "-":
        correct_result = num_1 - num_2
    elif op == "*":
        correct_result = num_1 * num_2
    elif op == "/":
        correct_result = num_1 / num_2

    # sonucu girme
    try:
        user_answer = float(input("İşlemin sonucunu gir: ").strip())
    except ValueError:
        print("Geçersiz değer girdin!, -1 hata hakkı")
        tries -= 1
        return tries , bonus , guessed_word
    
    if user_answer == correct_result:
        bonus += 1
        print("Doğru Cevap! 1 Bonus Kazandın.")
        guessed_word = open_random_let(word, guessed_word) # fonksiyonu kullanma
    else:
        print(f"Yanlış!, Doğru Cevap {correct_result}, -1 hata hakkı")
        tries -=1 
    return tries , bonus , guessed_word 


# ipucu fonksiyonu 
def hint(word, bonus):
    if bonus < 1:
        print("En az 1 bonusun olması gerekiyor!")
        return bonus 
    
    # bonus -= 1
    
    if word in animals :
        category = "Hayvanlar"
    elif word in fruits :
        category = "Meyveler"

    # silinebilir kod parcasi.
    else : 
        category = "Bilinmiyor!" 
    print (f"İpucu: Kelime {category} kategorisinde")
    #############################
    return bonus



def play_game():
    word = random.choice(words)
    guessed_letters = []
    guessed_word = ["_"] * len(word)
    tries = 6
    bonus = 0
    print("Welcome to Hangman Game!!!")
    print('U Have to Guess the Hidden Word!')
    print("\n")
    print("Seçenekler: [H]arf tahmini | [İ]şlem çöz | [I]pucu | [Q]Çıkış")
    print(display_hangman(tries))
    print(" ".join(guessed_word))
    print("\n")

    while tries > 0 and "_" in guessed_word: 
        user_guess = input("Seçimin: ").strip()


        if user_guess == "Q":
            print("Oyundan başarılı bir şekilde çıktın BYE!")
            return # oyundan cikma 
    
        if user_guess == "İ":
            tries, bonus, guessed_word = solve_math(word, guessed_word, guessed_letters, tries, bonus)
            print(display_hangman(tries))
            print(f"Kalan bonus sayısı: {bonus}")
            print(" ".join(guessed_word))
            continue

        if user_guess == "I":
            bonus = hint(word, bonus)
            print(f"Kalan bonus sayısı {bonus}")
            print(" ".join(guessed_word))
            continue


        if not user_guess.isalpha() or len(user_guess) != 1:
            print("U entered wrong value!")
            continue


        # if user_guess == "H":
        if user_guess in guessed_letters:
            print ('U already entered this letter')
            continue

        guessed_letters.append(user_guess)

        if user_guess in word :
            print("\n")
            print(f'✅ "{user_guess}" is Right Letter!')

            for i, letter in enumerate(word):
                if letter == user_guess:
                    guessed_word[i] = user_guess
        else :
            print("\n")
            print(f'❌ "{user_guess}" is Wrong Letter!')
            tries -= 1

        print(display_hangman(tries))
        print(f"You Have {tries} Tries Left")
        print("\n")
        print( "Entered Letters: " + ", ".join(sorted(guessed_letters)))
        print("\n")
        print(" ".join(guessed_word))
        print("\n")
        # print(f"Kalan bonus sayısı {bonus}")


    if "_" not in guessed_word:
        print(f'🎉 You WON! | The word was {word}')
    else:
        print (f'😔 You LOST! | The word was {word}')

if __name__ == "__main__":
    play_game()
