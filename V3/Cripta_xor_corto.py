Lista_bit_parola = []
Lista_bit_chiave = []
Lista_bit_chiper = []

Key = 34235126
Parola = "Ciao, io sono Mario"

lunghezza_Parola = len(Parola) * 2
while len(str(Key)) < lunghezza_Parola:
    Key = Key + Key

for c in Parola:
    c_byte = c.encode("utf-8")[0]
    c_bits = format(c_byte, "08b")
    Lista_bit_parola.append(c_bits)

i = 0
while i < len(str(Key)):
    coppia = str(Key)[i:i+2]
    c_bits = format(int(coppia), "08b")
    Lista_bit_chiave.append(c_bits)
    i = i + 2
    
for i in range(len(Lista_bit_parola)):
    parola = Lista_bit_parola[i]
    chiave = Lista_bit_chiave[i]
    
    xor_riga = ""
    for j in range(len(parola)):
        xor_bit = str(int(parola[j]) ^ int(chiave[j]))
        xor_riga += xor_bit
    
    Lista_bit_chiper.append(xor_riga)

Lista_bit_chiper = [riga * 2 for riga in Lista_bit_chiper]

for r in Lista_bit_chiper:
    numero = int(r, 2)
    print(chr(numero), end="")
