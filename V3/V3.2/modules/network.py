import time
import socket
import os, struct
from .encryption import * 
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio

CHUNK = 4096
# ----------------- FUNZIONI SOCKET -----------------
def presenza_broadcast(porta, nomeServ, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    messaggio = f"SERVER|{nomeServ}|{porta}".encode()
    
    while not stop_event.is_set():
        sock.sendto(messaggio, ("<broadcast>", 44929))
        time.sleep(3)
    
    sock.close()

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
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def ricevi(conn, NomeCli, Alg, chiave, alfabeto):
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
                print(f"{NomeCli} ha inviato una foto salvata come ricevuta_{filename}")
            else:
                chiper = data.decode()
                if Alg == "cesare":
                    frasedecry = decripta_cesare(chiper, chiave, alfabeto)
                elif Alg == "xor":
                    frasedecry = decripta_Xor(chiper, chiave)
                    
                print(NomeCli, ": ", frasedecry)
                
        except Exception as e:
            print("Errore ricezione:", e)
            break

async def invia_async(client, Alg, chiave, alfabeto, session):
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
                    messcry = cripta_cesare(mess, chiave, alfabeto)
                elif Alg == "xor":
                    messcry = cripta_Xor(mess, chiave)
                client.send(messcry.encode())

def invia(client, Alg, chiave, alfabeto, session):
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