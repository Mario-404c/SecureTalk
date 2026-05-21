import socket
import time
import threading
import os, struct
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

NomeCli = "Client"

CHUNK = 4096
alfabeto = "<|b'0#c)d_e$@&61fg!=£hi*j5:klmçùn]2?op^qrs(tuàv,wx+yz7 A+BC.8DèEF;3GHIJaLM[NOòPQéR4>STU-èV*WìX9YZ"
session = PromptSession()

#          -----------------------------INIZIO FUNZIONI CRITTOGRAFIA-----------------------------

def crea_chiave(password):
    chiave = ""
    for c in password:
        char = c
        codice = ord(char)
        chiave = chiave + str(codice)
    chiave = (int(chiave) / 2) * 4
    chiave = int(chiave)
    return str(chiave)

#       --Cesare--

def cripta_cesare(mess, chiave, alfabeto):

    while len(chiave) < len(mess):
        if len(str(chiave)) > len(mess):
            chiave = chiave
        else:
            chiave = chiave + chiave

    i = 0
    chiper = ""
    for c in mess:
        posizA = alfabeto.index(c)
        posizB = int(chiave[i])
        newposizA = (posizA + posizB) % 97
        chiper = str(chiper) + str(alfabeto[newposizA])
        i = i + 1
    return chiper

def decripta_cesare(chiper, chiave, alfabeto):
    i = 0
    frasedecrypt = ""
    
    while len(chiave) < len(chiper):
        if len(str(chiave)) > len(chiper):
            chiave = chiave
        else:
            chiave = chiave + chiave

    for c in chiper:
        posizA = alfabeto.index(c)
        posizB = int(chiave[i])
        newposizA = (posizA - posizB) % 97
        frasedecrypt = str(frasedecrypt) + str(alfabeto[newposizA])
        i = i + 1
    return frasedecrypt
#       --Cesare--
#         --xor--

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

#         --xor--
#           -----------------------------FINE FUNZIONI CRITTOGRAFIA-----------------------------

#         -----------------------------INIZIO FUNZIONI INVIA E RICEVI-----------------------------
def ascolta_broadcast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 44929))
    server_trovati = []
    print("In ascolto per server...")
    E = True
    while E == True:
        data, addr = sock.recvfrom(1024)
        messaggio = data.decode()
        
        # il server manda "SERVER|NomeServ|porta"
        parti = messaggio.split("|")
        if parti[0] == "SERVER":
            nomeServ = parti[1]
            porta = parti[2]
            ip = addr[0]
            
            if not any(s["ip"] == ip for s in server_trovati):
                    server_trovati.append({"nome": nomeServ, "ip": ip, "porta": porta})
                    
        time.sleep(3)
        if server_trovati:
            os.system("cls" if os.name == "nt" else "clear")
            print("Server trovati:")
            for i, s in enumerate(server_trovati):
                print(f"  {i+1}. {s['nome']} — {s['ip']}:{s['porta']}")
            print("r: ricarica | <numero>: carica i dati del server selezionato")
            risposta = input()
            if(risposta == "r"):
             os.system("cls" if os.name == "nt" else "clear")
            elif(risposta.isdigit() == True):
                if(int(risposta)>0 and int(risposta) <= len(server_trovati)):
                    while True:
                        print(f"Hai selezionato {server_trovati[int(risposta)-1]['nome']} con ip: {server_trovati[int(risposta)-1]['ip']} e porta: {server_trovati[int(risposta)-1]['porta']}")
                        print("Confemri? y/n")
                        ris = input()
                        if(ris.lower() == "y" or ris.lower() == "s"):
                            E = False
                            break
                        elif(ris.lower() == "n"):
                            input("Attendo input per tornare alla ricerca...")
                            break
                        else:
                            print("Non hai selezionato nessuna delle opzioni possibili")
    sock.close()
    return ip, porta

def recvall(sock, n):
    """Legge esattamente n byte dalla socket"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def ricevi(conn):
    global NomeServ
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
                    frasedecry = decripta_cesare(chiper, chiave, alfabeto)
                elif Alg == "xor":
                    frasedecry = decripta_Xor(chiper, chiave)
                print(NomeServ, ": ", frasedecry)
        except Exception as e:
            print("Errore ricezione:", e)
            break

def invia(client):
    with patch_stdout():
        while True:
            try:
                mess = session.prompt("Tu: ")
            except (EOFError, KeyboardInterrupt):
                break

            if mess == "<<IMG>>":
                print("Scrivi il nome del file da mandare: ")
                FILEPATH = input()
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
                    chiper = cripta_cesare(mess, chiave, alfabeto)
                elif Alg == "xor":
                    chiper = cripta_Xor(mess, chiave)
                client.send(chiper.encode())
#         -----------------  FUNZIONI SECELTA -----------------

def seleziona_ip():
    A = True
    while A == True:
        indirizzo = input("Inserisci l'ip interno alla rete su cui ascoltare (x.x.x.x): ")
        risposta = input("Questi dati sono corretti? (y/n)")
        if risposta.lower() == "y" or risposta.lower() == "s":
            A = False
        elif risposta.lower() == "n":
            A = True
        else:
            print("Non hai selezionato nessuna delle opzioni possibili! (y/n)")
    return indirizzo

def seleziona_nome():
    B = True
    while B:
        risposta = input("Vuoi scegliere un nome? (y/n): ")
        if risposta.lower() == "y" or risposta.lower() == "s":
            NomeCli = input("Inserisci il Nome: ")
            B = False
        elif risposta.lower() == "n":
            B = False
        else:
            print("Non hai selezionato nessuna delle opzioni possibili! (y/n)")
    return NomeCli

def seleziona_alg():
    C = True
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
    return Alg

def memorizza():
    risposta = input("Vuoi memorizzare questi dati e sovrascrivere i precedenti? (y/n)")
    if risposta.lower() == "y" or risposta.lower() == "s":
        with open("config_CLIENT.txt", "w") as f:
            f.write(f"{NomeCli}\n")
            f.write(f"{porta}\n")
            f.write(f"{indirizzo}\n")
            f.write(f"{Alg}\n")
    else:
        print("I dati non sono stati sovrascritti. ")
# -----------------------------INIZIO SCRIPT-----------------------------
print("""\033[31m
Avvio CLIENT...
\033[0m""")
A = True
while A == True:

    while True:
        print("Vuoi trovare dispositivi sulla rete? y/n")
        risposta = input()
        if(risposta.lower() == "y" or risposta.lower() == "s"):
            Broadcast = True
            indirizzo, porta = ascolta_broadcast()
            break
        elif(risposta.lower() == "n"):
            Broadcast = False
            break
        else:
            os.system("cls" if os.name == "nt" else "clear")
            print("Non hai inserito nessuna delle opzioni possibili!")
        
        

    File_esiste = False
    risposta = "n"

    if os.path.exists("config_CLIENT.txt") and os.path.getsize("config_CLIENT.txt") > 0:
        File_esiste = True
        risposta = input("Vuoi usare i dati precedenti? (y/n)")
        if risposta.lower() == "y" or risposta.lower() == "s":
            with open("config_CLIENT.txt", "r") as f:
                righe = f.readlines()
                
                righe = [riga.strip() for riga in righe]

                NomeCli = righe[0]
                if(Broadcast == False):
                    porta = righe[1]
                    indirizzo = righe[2]
                Alg = righe[3]
                
                print("Nome: ", NomeCli, " porta: ", porta, " Indirizzo: ", indirizzo, "Algoritmo utilizzato: ", Alg)

    if risposta.lower() == "n" or File_esiste == False:
        
        if(Broadcast == False):
            porta = input("Scegliere porta di rete per la comunicazione: ")
            
            indirizzo = seleziona_ip()
        
        NomeCli = seleziona_nome()
        
        Alg = seleziona_alg()
                
        memorizza()
                
    password = input("Scegli una password per la crittografia (Obbligatorio): ")
    chiave = crea_chiave(password)
    print("La tua chiave di crittografia è: \033[93;40m", chiave, "\033[0m")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((indirizzo, int(porta)))
        print(f"\033[32m Connessione stabilita con {indirizzo}! \033[0m")
    except ConnectionRefusedError:
        print("\033[31m Errore! Connessione rifiutata! \033[0m")
        exit()
    except ConnectionResetError:
        print("\033[31m Errore! La connessione è stata cambiata! \033[0m")
        exit()
    except TimeoutError:
        print("\033[31m Tempo scaduto, connessione chiusa! \033[0m")
        exit()

    client.send(NomeCli.encode())
    data = client.recv(1024)
    risposta = data.decode()  

    if(risposta == "ACCEPTED"):
        print(f"\033[32m Connessione accettata da {indirizzo}! \033[0m")
        A = False
    elif(risposta == "REFUSED"):
        print(f"\033[31m Connessione rifiutata da {indirizzo}! \033[0m")
        client.close()
        input(f"Attendo input per continuare la ricerca... ")
        os.system("cls" if os.name == "nt" else "clear")

data = client.recv(1024)
NomeServ = data.decode()  

threading.Thread(target=ricevi, args=(client,), daemon=True).start() 
invia(client) 