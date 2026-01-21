#CLIENT: Server e client funzionano allo stesso modo

import socket
import threading
import os, struct

NomeCli = "Client"

CHUNK = 4096

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
                print(NomeServ, ": ", data.decode())
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
            client.send(mess.encode())

A = True
B = True
while A == True:
    print("Inserisci l'ip del server: ")
    indirizzo = input()

    print("Inserisci la porta su cui comunicare: ")
    port = input()

    print("Ip: ", indirizzo, " Porta: ", port)
    print("Questi dati sono corretti? (Y/N)")
    ris = input()
    if ris == "Y" or "y":
        A = False
    elif ris == "N" or "n":
        pass
    else:
        print("Non hai inserito nessuna delle due risposte accettate (Y/N)!")
        pass

while B == True:
    print("Vuoi scegliere un nome? (Y/N): ")
    risposta = input()
    if risposta == "Y" or "y":
        print("Inserisci il Nome: ")
        NomeCli = input()
        B = False
    elif risposta == "N" or "n":
        B = False
    else:
        print("Non hai inserito nessuna delle opzioni possibili! (Y/N)")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((indirizzo, int(port)))
    print("Connessione riuscita con: ", indirizzo)
except ConnectionRefusedError:
    print("Errore! Connessione rifiutata!")
    exit()
except ConnectionResetError:
    print("Errore! La connessione è stata cambiata!")
    exit()
except TimeoutError:
    print("Tempo scaduto, connessione chiusa!")
    exit()

client.send(NomeCli.encode())
data = client.recv(1024)
NomeServ = data.decode()

threading.Thread(target=ricevi, args=(client,)).start()
threading.Thread(target=invia, args=(client,)).start()