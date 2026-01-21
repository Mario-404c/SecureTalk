#CLIENT: Server e client funzionano allo stesso modo

import socket
import threading
import os, struct
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

NomeCli = "Client"

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
                print(NomeServ, ": ", frasedecry)
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

#                    -----------------------------INIZIO SCRIPT-----------------------------
A = True
B = True

print("""\033[31m
██████╗ ██╗      █████╗  ██████╗██╗  ██╗██████╗  ██████╗ ██╗  ██╗
██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝
██████╔╝██║     ███████║██║     █████╔╝ ██████╔╝██║   ██║ ╚███╔╝ 
██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██╔══██╗██║   ██║ ██╔██╗ 
██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██████╔╝╚██████╔╝██╔╝ ██╗
╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
\033[0m""")

while A == True:
    print("Inserisci l'ip del server: ")
    indirizzo = input()

    print("Inserisci la porta su cui comunicare: ")
    port = input()

    print("Ip: ", indirizzo, " Porta: ", port)
    print("Questi dati sono corretti? (Y/N)")
    ris = input()
    if ris.lower() == "y":
        A = False
    elif ris.lower() == "n":
        pass
    else:
        print("Non hai inserito nessuna delle due risposte accettate (Y/N)!")
        pass

while B == True:
    print("Vuoi scegliere un nome? (Y/N): ")
    risposta = input()
    if risposta.lower() == "y":
        print("Inserisci il Nome: ")
        NomeCli = input()
        B = False
    elif risposta.lower() == "n":
        B = False
    else:
        print("Non hai inserito nessuna delle opzioni possibili! (Y/N)")

print("Scegli una password per la crittografia (Obbligatorio): ")
password = input()
chiave = crea_chiave(char, codice, chiave, password)
print("La tua chiave di crittografia è: ", chiave)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((indirizzo, int(port)))
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
NomeServ = data.decode()

threading.Thread(target=ricevi, args=(client,)).start()
threading.Thread(target=invia, args=(client,)).start()