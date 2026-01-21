#SERVER: Server e client funzionano allo stesso modo
import time
import socket
import threading
import os, struct
import errno
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

NomeServ = "Server"

CHUNK = 4096

#          -----------------------------INIZIO FUNZIONI CRITTOGRAFIA-----------------------------
i = 0 
frasedecrypt = ""
Frasecrypt = ""
char = ''
codice = ""
chiave = ""

def crea_chiave(char, codice, chiave, password):
    for c in password:
        char = c
        codice = ord(char)
        chiave = chiave + str(codice)
    chiave = (int(chiave) / 2) * 4
    chiave = int(chiave)
    return str(chiave)

def cripta(mess, chiave, Frasecrypt, i):
    alfabeto = "ab'c)de@fg!hij:klmn]?op^qrs(tuv,wxyz A+BC#DEF;GHIJ<LM[NOèPQR>STU-VWXYZ"

    while len(chiave) < len(mess):
        if len(str(chiave)) > len(mess):
            chiave = chiave
        else:
            chiave = chiave + chiave

    i = 0
    for c in mess:
        posizA = alfabeto.index(c)
        posizB = int(chiave[i])
        newposizA = (posizA + posizB) % 70
        Frasecrypt = str(Frasecrypt) + str(alfabeto[newposizA])
        i = i + 1
    return Frasecrypt

def decripta(Frasecrypt, chiave, i, frasedecrypt):
    i = 0
    alfabeto = "ab'c)de@fg!hij:klmn]?op^qrs(tuv,wxyz A+BC#DEF;GHIJ<LM[NOèPQR>STU-VWXYZ"

    while len(chiave) < len(Frasecrypt):
        if len(str(chiave)) > len(Frasecrypt):
            chiave = chiave
        else:
            chiave = chiave + chiave

    for c in Frasecrypt:
        posizA = alfabeto.index(c)
        posizB = int(chiave[i])
        newposizA = (posizA - posizB) % 70
        frasedecrypt = str(frasedecrypt) + str(alfabeto[newposizA])
        i = i + 1
    return frasedecrypt
#           -----------------------------FINE FUNZIONI CRITTOGRAFIA-----------------------------

#         -----------------------------INIZIO FUNZIONI INVIA E RICEVI-----------------------------

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
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("Connessione chiusa dal server")
                break
            elif data.decode() == "<<IMG>>":
                # 1) leggo 4 byte che dicono quanto è lungo l'header
                raw_hdr_len = recvall(conn, 4)
                hdr_len = struct.unpack('!I', raw_hdr_len)[0]

                # 2) leggo l'header (nome file + dimensione)
                header_bytes = recvall(conn, hdr_len)
                header_str = header_bytes.decode()
                filename, filesize = header_str.split('|')  # separiamo nome e dimensione
                filesize = int(filesize)

                # 3) ricevo il file
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
                Frasecrypt = data.decode()
                frasedecry = decripta(Frasecrypt, chiave, i, frasedecrypt)
                print(NomeCli, ": ", frasedecry)
        except Exception as e:
            print("Errore ricezione:", e)
            break

def invia(client):
    while True:
        
        mess = input()
        if mess == "<<IMG>>":
            print("Scrivi il nome del file da mandare: ")
            FILEPATH = input()
            client.send("<<IMG>>".encode())
            filesize = os.path.getsize(FILEPATH)
            filename = os.path.basename(FILEPATH)

            # header semplice: "nomefile|dimensione"
            header = f"{filename}|{filesize}".encode()
            hdr_len = struct.pack('!I', len(header))  # 4 byte con lunghezza header

            # invio header
            client.sendall(hdr_len)
            client.sendall(header)

            # invio file
            with open(FILEPATH, "rb") as f:
                while True:
                    chunk = f.read(CHUNK)
                    if not chunk:
                        break
                    client.sendall(chunk)

            print("Foto inviata!")
        else:
            messcry = cripta(mess, chiave, Frasecrypt, i)
            client.send(messcry.encode())

def animazione_caricamento():
    global stop_anim
    while stop_anim == False:
        print(f"\033[34m Server in ascolto sulla porta {porta}... -- \033[0m", end="\r")
        time.sleep(0.5)
        print(f"\033[34m Server in ascolto sulla porta {porta}... \ \033[0m", end="\r")
        time.sleep(0.5)
        print(f"\033[34m Server in ascolto sulla porta {porta}... | \033[0m", end="\r")
        time.sleep(0.5)
        print(f"\033[34m Server in ascolto sulla porta {porta}... / \033[0m", end="\r")
        time.sleep(0.5)
    
#                    -----------------------------INIZIO SCRIPT-----------------------------

indirizzo = "0.0.0.0"
print("""\033[31m
██████╗ ██╗      █████╗  ██████╗██╗  ██╗██████╗  ██████╗ ██╗  ██╗
██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝
██████╔╝██║     ███████║██║     █████╔╝ ██████╔╝██║   ██║ ╚███╔╝ 
██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██╔══██╗██║   ██║ ██╔██╗ 
██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██████╔╝╚██████╔╝██╔╝ ██╗
╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
\033[0m""")
print("Scegliere porta di rete per la comunicazione: ")
porta = input()
print("porta scelta: ", porta)
A = True
B = True
stop_anim = False
while A == True:
    print("Vuoi selezionare un ip specifico o rimanere in ascolto di tutti i dispositivi sulla rete? (Y/N): ")
    risposta1 = input()
    if risposta1.lower() == "y":
        print("Inserisci l'ip interno alla rete su cui ascoltare (192.168.1.x): ")
        indirizzo = input()
        A = False
    elif risposta1.lower() == "n":
        A = False
    else:
        print("Non hai inserito nessuna delle opzioni possibili! (Y/N)")

while B == True:
    print("Vuoi scegliere un nome? (Y/N): ")
    risposta = input()
    if risposta.lower() == "y":
        print("Inserisci il Nome: ")
        NomeServ = input()
        B = False
    elif risposta.lower() == "n":
        B = False
    else:
        print("Non hai inserito nessuna delle opzioni possibili! (Y/N)")
    
print("Scegli una password per la crittografia (Obbligatorio): ")
password = input()
chiave = crea_chiave(char, codice, chiave, password)
print("La tua chiave di crittografia è: ", chiave)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((indirizzo, int(porta)))

server.listen(1)
threading.Thread(target=animazione_caricamento).start()

conn, indirizzo = server.accept()
stop_anim = True

print(f"\033[32m Connessione stabilita con {indirizzo}! \033[0m")
    
conn.send(NomeServ.encode())
data = conn.recv(1024)
NomeCli = data.decode()

threading.Thread(target=ricevi, args=(conn,)).start()
threading.Thread(target=invia, args=(conn,)).start()