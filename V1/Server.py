#SERVER: Server e client funzionano allo stesso modo

import socket
import threading
import os, struct

NomeServ = "Server"

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
                print("Connessione chiusa dal client")
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

                print(f"{NomeCli} ha inviato una foto salvata come ricevuta_{filename}")
            else:
                print(NomeCli, ": ", data.decode())
        except Exception as e:
            print("Errore ricezione:", e)
            break

def invia(conn):
    while True:
        mess = input()
        if mess == "<<IMG>>":
            print("Scrivi il nome del file da mandare: ")
            FILEPATH = input()
            filesize = os.path.getsize(FILEPATH)
            filename = os.path.basename(FILEPATH)

            # invio comando
            conn.send("<<IMG>>".encode())

            # header semplice: "nomefile|dimensione"
            header = f"{filename}|{filesize}".encode()
            hdr_len = struct.pack('!I', len(header))  # 4 byte con lunghezza header

            # invio header
            conn.sendall(hdr_len)
            conn.sendall(header)

            # invio file
            with open(FILEPATH, "rb") as f:
                while True:
                    chunk = f.read(CHUNK)
                    if not chunk:
                        break
                    conn.sendall(chunk)

            print("Foto inviata!")
        else:
            conn.send(mess.encode())

indirizzo = "0.0.0.0"
print("Scegliere porta di rete per la comunicazione: ")
porta = input()
print("porta scelta: ", porta)
A = True
B = True
while A == True:
    print("Vuoi selezionare un ip specifico o rimanere in ascolto di tutti i dispositivi sulla rete? (Y/N): ")
    risposta = input()
    if risposta == "Y" or "y":
        print("Inserisci l'ip interno alla rete su cui ascoltare (192.168.1.x): ")
        indirizzo = input()
        A = False
    elif risposta == "N" or "n":
        A = False
    else:
        print("Non hai inserito nessuna delle opzioni possibili! (Y/N)")

while B == True:
    print("Vuoi scegliere un nome? (Y/N): ")
    risposta = input()
    if risposta == "Y" or "y":
        print("Inserisci il Nome: ")
        NomeServ = input()
        B = False
    elif risposta == "N" or "n":
        B = False
    else:
        print("Non hai inserito nessuna delle opzioni possibili! (Y/N)")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((indirizzo, int(porta)))

server.listen(1)
print("server in ascolto sulla porta ", porta, "...")
conn, addr = server.accept()
print(f"connessione stabilita con {addr}")

conn.send(NomeServ.encode())
data = conn.recv(1024)
NomeCli = data.decode()

threading.Thread(target=ricevi, args=(conn,)).start()
threading.Thread(target=invia, args=(conn,)).start()