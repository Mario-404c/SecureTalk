Lista_numeri_unicode = []
Lista_bit_numeri_unicode = []
Lista_bit_key = []
Lista_bit_xor = []

# chiper: 䥉㴽㸾䍃Ḟ᠘ࠈ畵᜗㰼獳剒塘晦繾彟∢㐴䍃

Key = 34235126

chiper = input("Frase criptata: ")

lunghezza_chiper = len(chiper) * 2
while len(str(Key)) < lunghezza_chiper:
    Key = Key + Key

for c in chiper:
    Lista_numeri_unicode.append(ord(c))
    
for c in Lista_numeri_unicode:
    bits = format(int(c), "016b")
    
    Lista_bit_numeri_unicode.append(bits)

i=0
while i <  len(str(Key)):
    coppia = str(Key)[i:i+2]
    bit = format(int(coppia), "08b")
    Lista_bit_key.append(bit)
    i = i+2

Lista_bit_key = [riga * 2 for riga in Lista_bit_key]


for i in range(len(Lista_bit_numeri_unicode)):
    parola = Lista_bit_numeri_unicode[i]
    chiave = Lista_bit_key[i]
    
    xor_riga = ""
    for j in range(len(parola)):
        xor_bit = str(int(parola[j]) ^ int(chiave[j]))
        xor_riga += xor_bit
    
    Lista_bit_xor.append(xor_riga)

for e in Lista_bit_xor:
    bit = e[:8]
    numero = int(bit, 2)
    print(chr(numero), end="")