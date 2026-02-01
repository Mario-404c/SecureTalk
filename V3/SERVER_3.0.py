import time
import socket
import threading
import os, struct
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio

NomeServ = "Server"
CHUNK = 4096

i = 0
frasedecrypt = ""
Frasecrypt = ""
char = ''
codice = ''
chiave = ''
session = PromptSession()

# ----------------- FUNZIONI CRITTOGRAFIA -----------------

def crea_chiave(char, codice, chiave, password):
    for c in password:
        char = c
        codice = ord(char)
        chiave = chiave + str(codice)
    chiave = (int(chiave) / 2) * 4
    chiave = int(chiave)
    return str(chiave)

#       --Cesare--

def cripta_cesare(mess, chiave, Frasecrypt, i):
    alfabeto = "<|b'0#c)d_e$@&61fg!=£hi*j5:klmçùn]2?op^qrs(tuàv,wx+yz7 A+BC.8DèEF;3GHIJaLM[NOòPQéR4>STU-èV*WìX9YZ"
    while len(chiave) < len(mess):
        if len(str(chiave)) > len(mess):
            chiave = chiave
        else:
            chiave = chiave + chiave
    i = 0
    Frasecrypt = ""
    for c in mess:
        posizA = alfabeto.index(c)
        posizB = int(chiave[i])
        newposizA = (posizA + posizB) % 97
        Frasecrypt += alfabeto[newposizA]
        i += 1
    return Frasecrypt

def decripta_cesare(Frasecrypt, chiave, i, frasedecrypt):
    alfabeto = "<|b'0#c)d_e$@&61fg!=£hi*j5:klmçùn]2?op^qrs(tuàv,wx+yz7 A+BC.8DèEF;3GHIJaLM[NOòPQéR4>STU-èV*WìX9YZ"
    while len(chiave) < len(Frasecrypt):
        if len(str(chiave)) > len(Frasecrypt):
            chiave = chiave
        else:
            chiave = chiave + chiave
    frasedecrypt = ""
    for idx, c in enumerate(Frasecrypt):
        posizA = alfabeto.index(c)
        posizB = int(chiave[idx])
        newposizA = (posizA - posizB) % 97
        frasedecrypt += alfabeto[newposizA]
    return frasedecrypt

#       --Cesare--
#         --Xor--

def cripta_Xor(mess, Key):
    Lista_bit_parola = []
    Lista_bit_chiave = []
    Lista_bit_chiper = []

    Lista_bit_parola.clear()
    Lista_bit_chiave.clear()
    Lista_bit_chiper.clear()

    lunghezza_Parola = len(mess) * 2
    while len(str(Key)) < lunghezza_Parola:
        Key = Key + Key

    for c in mess:
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

    mess_chiper = ""
    for r in Lista_bit_chiper:
        numero = int(r, 2)
        mess_chiper = mess_chiper + chr(numero)
    
    return mess_chiper

def decripta_Xor(chiper, Key):
    Lista_numeri_unicode = []
    Lista_bit_numeri_unicode = []
    Lista_bit_key = []
    Lista_bit_xor = []

    Lista_numeri_unicode.clear()
    Lista_bit_numeri_unicode.clear()
    Lista_bit_key.clear()
    Lista_bit_xor.clear()

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

    mess_decrypt = ""

    for e in Lista_bit_xor:
        bit = e[:8]
        numero = int(bit, 2)
        mess_decrypt = mess_decrypt + chr(numero)
    
    return mess_decrypt
#         --Xor--
# ----------------- FUNZIONI SOCKET -----------------
def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def ricevi(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("Connessione chiusa dal server")
                break
            elif data.decode() == "<<IMG>>":
                raw_hdr_len = recvall(conn, 4)
                hdr_len = struct.unpack('!I', raw_hdr_len)[0]
                header_bytes = recvall(conn, hdr_len)
                header_str = header_bytes.decode()
                filename, filesize = header_str.split('|')
                filesize = int(filesize)
                received = 0
                with open("ricevuta_" + filename, "wb") as f:
                    while received < filesize:
                        to_read = min(CHUNK, filesize - received)
                        chunk = recvall(conn, to_read)
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                print(f"{NomeServ} ha inviato una foto salvata come ricevuta_{filename}")
            else:
                chiper = data.decode()
                if Alg == "cesare":
                    frasedecry = decripta_cesare(chiper, chiave, i, frasedecrypt)
                elif Alg == "xor":
                    frasedecry = decripta_Xor(chiper, chiave)
                    
                print(NomeServ, ": ", frasedecry)
                
        except Exception as e:
            print("Errore ricezione:", e)
            break

async def invia_async(client):
    with patch_stdout():  
        while True:
            try:
                mess = await session.prompt_async("Tu: ")
            except (EOFError, KeyboardInterrupt):
                print("\nChiusura invio richiesta dall'utente")
                break
            if mess == "<<IMG>>":
                FILEPATH = input("Scrivi il nome del file da mandare: ")
                client.send("<<IMG>>".encode())
                filesize = os.path.getsize(FILEPATH)
                filename = os.path.basename(FILEPATH)
                header = f"{filename}|{filesize}".encode()
                hdr_len = struct.pack('!I', len(header))
                client.sendall(hdr_len)
                client.sendall(header)
                with open(FILEPATH, "rb") as f:
                    while True:
                        chunk = f.read(CHUNK)
                        if not chunk:
                            break
                        client.sendall(chunk)
                print("Foto inviata!")
            else:
                if Alg == "cesare":
                    messcry = cripta_cesare(mess, chiave, Frasecrypt, i)
                elif Alg == "xor":
                    messcry = cripta_Xor(mess, chiave)
                client.send(messcry.encode())

# ----------------- SCRIPT PRINCIPALE -----------------
indirizzo = "0.0.0.0"
print("""\033[31m
Avvio SERVER...
\033[0m""")

File_esiste = False

risposta = "n"

if os.path.exists("config_SERVER.txt") and os.path.getsize("config_SERVER.txt") > 0:
    File_esiste = True
    risposta = input("Vuoi usare i dati precedenti? (y/n)")
    if risposta.lower() == "y" or risposta.lower() == "s":
        with open("config_SERVER.txt", "r") as f:
            righe = f.readlines()
            
            righe = [riga.strip() for riga in righe]

            NomeServ = righe[0]
            porta = righe[1]
            indirizzo = righe[2]
            Alg = righe[3]

if risposta.lower() == "n" or File_esiste == False:
    porta = input("Scegliere porta di rete per la comunicazione: ")
    
    stop_anim = False
    A = True
    B = True
    C = True
    while A:
        risposta1 = input("Vuoi selezionare un ip specifico? (y/n): ")
        if risposta1.lower() == "y" or risposta1.lower() == "s":
            indirizzo = input("Inserisci l'ip interno alla rete su cui ascoltare (192.168.1.x): ")
            A = False
        elif risposta1.lower() == "n":
            A = False
        else:
            print("Non hai selezionato nessuna delle opzioni possibili! (y/n)")

    while B:
        risposta = input("Vuoi scegliere un nome? (y/n): ")
        if risposta.lower() == "y" or risposta.lower() == "s":
            NomeServ = input("Inserisci il Nome: ")
            B = False
        elif risposta.lower() == "n":
            B = False
        else:
            print("Non hai selezionato nessuna delle opzioni possibili! (y/n)")
            
    while C:
        risposta = input("Scegli l'algoritmo di cifratura |\033[34m Cesare, Xor, Cesare+Xor \033[0m|: ")
        if risposta.lower() == "cesare":
            Alg = "cesare"
            C = False
        elif risposta.lower() == "xor":
            Alg = "xor"
            C = False
        elif risposta.lower() == "cesare+xor":
            Alg = "cesare+xor"
            C = False
        else:
            print("Non hai selezionato nessuna delle opzioni possibili! |\033[34m Cesare, Xor, Cesare+Xor \033[0m|")
            
    risposta = input("Vuoi memorizzare questi dati e sovrascrivere i precedenti? ")
    if risposta.lower() == "y" or risposta.lower() == "s":
        with open("config_SERVER.txt", "w") as f:
            f.write(f"{NomeServ}\n")
            f.write(f"{porta}\n")
            f.write(f"{indirizzo}\n")
            f.write(f"{Alg}\n")
    else:
        print("I dati non sono stati sovrascritti. ")

password = input("Scegli una password per la crittografia (Obbligatorio): ")
chiave = crea_chiave(char, codice, chiave, password)
print("La tua chiave di crittografia è: \033[93;40m", chiave, "\033[0m")
    
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((indirizzo, int(porta)))
server.listen(1)

print(f"\033[34m Server in ascolto sulla porta {porta}... \033")

conn, indirizzo_client = server.accept()
print(f"\033[32m Connessione stabilita con {indirizzo_client}! \033[0m")

conn.send(NomeServ.encode())
data = conn.recv(1024)
NomeCli = data.decode()

threading.Thread(target=ricevi, args=(conn,), daemon=True).start()

loop = asyncio.get_event_loop()
loop.run_until_complete(invia_async(conn))
