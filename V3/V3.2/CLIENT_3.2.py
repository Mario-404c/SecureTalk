import socket
import time
import threading
import os, struct
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from modules import encryption, network, selection

NomeCli = "Client"

CHUNK = 4096
alfabeto = "<|b'0#c)d_e$@&61fg!=£hi*j5:klmçùn]2?op^qrs(tuàv,wx+yz7 A+BC.8DèEF;3GHIJaLM[NOòPQéR4>STU-èV*WìX9YZ"
session = PromptSession()

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
            indirizzo, porta = network.ascolta_broadcast()
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
            
            indirizzo = selection.seleziona_ip()
        
        NomeCli = selection.seleziona_nome()
        
        Alg = selection.seleziona_alg()
                
        selection.memorizza()
                
    password = input("Scegli una password per la crittografia (Obbligatorio): ")
    chiave = encryption.crea_chiave(password)
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

threading.Thread(target=network.ricevi, args=(client, NomeServ, Alg, chiave, alfabeto), daemon=True).start() 
network.invia(client, Alg, chiave, alfabeto, session) 