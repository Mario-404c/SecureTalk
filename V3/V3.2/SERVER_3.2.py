import time
import os
import socket
import threading
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio
from modules import encryption, network, selection

session = PromptSession()
alfabeto = "<|b'0#c)d_e$@&61fg!=£hi*j5:klmçùn]2?op^qrs(tuàv,wx+yz7 A+BC.8DèEF;3GHIJaLM[NOòPQéR4>STU-èV*WìX9YZ"

# ----------------- SCRIPT PRINCIPALE -----------------
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
            Alg = righe[2]
            print("Nome: ", NomeServ, " porta: ", porta, "Algoritmo utilizzato: ", Alg)

if risposta.lower() == "n" or File_esiste == False:
    porta = input("Scegliere porta di rete per la comunicazione: ")
    
    stop_anim = False

    NomeServ = selection.seleziona_nome()
            
    Alg = selection.seleziona_alg()
            
    selection.memorizza(NomeServ, porta, Alg)

password = input("Scegli una password per la crittografia (Obbligatorio): ")
chiave = encryption.crea_chiave(password)
print("La tua chiave di crittografia è: \033[93;40m", chiave, "\033[0m")
    
print("Selezionare un opzione: ")
print("Ascolto: 1")
print("Ascolto + Broadcast: 2")

scelta = input()
stop_broadcast = threading.Event() 

if scelta == "2":
    t_broadcast = threading.Thread(
        target=network.presenza_broadcast,
        args=(porta, NomeServ, stop_broadcast),
        daemon=True
    )
    t_broadcast.start()
    print("Broadcast avviato, in attesa di un client...")
    
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", int(porta)))
server.listen(1)

A = True
while A:
    print(f"\033[34m Server in ascolto sulla porta {porta}... \033[0m")
    conn, indirizzo_client = server.accept()
    data = conn.recv(1024)
    NomeCli = data.decode()
    time.sleep(0.1)
    print(f" Richiesta di connessione da parte di: {indirizzo_client}, con nome: {NomeCli}")
    D = True
    while D:
        print("Accettare? y/n")
        risposta = input()
        if(risposta.lower() == "y" or risposta.lower() == "s"):
            mess = "ACCEPTED"
            conn.send(mess.encode())
            print(f"\033[32m Connessione stabilita con {indirizzo_client}! \033[0m")
            stop_broadcast.set()
            D = False
            A = False
        elif(risposta.lower() == "n"):
            mess = "REFUSED"
            conn.send(mess.encode())
            
            input(f"\033[31m Connessione rifiutata, attendo input... \033[0m")
            
            os.system("cls" if os.name == "nt" else "clear")
            D = False
        else:
            os.system("cls" if os.name == "nt" else "clear")
            print("Non hai selezionato nessuna delle opzioni possibili!")
        

conn.send(NomeServ.encode())

threading.Thread(target=network.ricevi, args=(conn, NomeCli, Alg, chiave, alfabeto), daemon=True).start()

loop = asyncio.get_event_loop()
loop.run_until_complete(network.invia_async(conn, Alg, chiave, alfabeto, session))