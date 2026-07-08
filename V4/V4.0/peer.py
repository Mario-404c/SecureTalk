import time
import json
import os
import socket
import threading
import tempfile
import gnupg
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio
from modules import encryption, network, selection, gossip

session = PromptSession()
alfabeto = "<|b'0#c)d_e$@&61fg!=£hi*j5:klmçùn]2?op^qrs(tuàv,wx+yz7 A+BC.8DèEF;3GHIJaLM[NOòPQéR4>STU-èV*WìX9YZ"
gpg = gnupg.GPG(gnupghome=os.path.join(os.getcwd(), 'modules\keys'))


async def main():
    fingerprint = None
    File_esiste = False

    nome_pc = socket.gethostname()
    ip_personale = socket.gethostbyname(nome_pc)                                # Ip in LAN

    risposta = "n"
    richieste_in_attesa = []

    with open("ip_list.json", "r") as f:
        peers = json.load(f)
        
    if os.path.exists("config.txt") and os.path.getsize("config.txt") > 0:
        File_esiste = True
        risposta = input("Vuoi usare i dati precedenti? (y/n)")
        if risposta.lower() == "y" or risposta.lower() == "s":
            with open("config.txt", "r") as f:
                righe = f.readlines()
                        
                righe = [riga.strip() for riga in righe]

                Nome = righe[0]
                porta = int(righe[1])
                Alg = righe[2]
                ultimo_gossip = righe[3]
                if len(righe) > 4 and righe[4]:
                    fingerprint = righe[4]
                else:
                    fingerprint = None
                    
    if risposta.lower() == "n" or File_esiste == False:
        porta = input("Scegliere porta di rete per la comunicazione: ")

        Nome = selection.seleziona_nome()
                
        Alg = selection.seleziona_alg()
                
        selection.memorizza(Nome, porta, Alg, fingerprint)
        
    print("Nome: ", Nome, "ip: ", ip_personale,  " porta: ", porta, "Algoritmo: ", Alg)
    
    password = input("Scegli una password per la crittografia (Obbligatorio): ")
    if Alg == "cesare" or Alg == "xor":
        chiave = encryption.crea_chiave(password)
        print("La tua chiave di crittografia è: \033[93;40m", chiave, "\033[0m")
        chiave_pubblica = ""

    elif Alg == "pgp" and fingerprint == None:
        print("Non hai mai generato una chiave!")
        print("Sto generando la coppia di chiavi... ")
        input_data = gpg.gen_key_input(
            name_real= Nome,
            name_email='Talk@secure.com',
            passphrase=password,
            key_type='RSA',
            key_length=4096,
            )
        key = gpg.gen_key(input_data)
        fingerprint = key.fingerprint
        chiave_pubblica = gpg.export_keys(key.fingerprint)
        print("Fingerprint della tua nuova chiave: \n", fingerprint)
        ris = await asyncio.to_thread(
            input, "Vuoi visualizzare la tua chiave pubblica? | y/n \n"
        )
        if ris.lower() == "y":
            print(chiave_pubblica)
        chiave = 0
        
        selection.memorizza_no_conferma(Nome, porta, Alg, fingerprint)
    elif Alg == "pgp":
        ris = await asyncio.to_thread(
            input, f"Hai già una coppia di chiavi, con fingerprint: \n {fingerprint} \n Vuoi utilizzare questa? | y/n "
        )
        if ris == "n":
            password = await asyncio.to_thread(
                input, "Inserisci una nuova password per la crittografia: "
            )
            print("Sto generando la coppia di chiavi... ")
            input_data = gpg.gen_key_input(
                    name_real= Nome,
                    name_email='Talk@secure.com',
                    passphrase=password,
                    key_type='RSA',
                    key_length=2048,                                # 2048 per test veloce, 4096 in produzione
                )
            key = gpg.gen_key(input_data)
            fingerprint = key.fingerprint
            chiave_pubblica = gpg.export_keys(key.fingerprint)
            print("Fingerprint della tua nuova chiave: \n", fingerprint)
            ris = await asyncio.to_thread(
                input, "Vuoi visualizzare la tua chiave pubblica? | y/n \n"
            )
            if ris.lower() == "y":
                print(chiave_pubblica)     
            chiave = 0
            selection.memorizza_no_conferma(Nome, porta, Alg, fingerprint)
        else: 
            chiave_pubblica = gpg.export_keys(fingerprint)
            chiave = 0
            
    io_mancante = True
    for p in peers:
        if p["ip"] == ip_personale and p["porta"] == porta:
            io_mancante = False
    if io_mancante == True:
        me = {
        "ip": ip_personale,
        "nome": Nome,
        "porta": porta,
        "timestamp": time.time(),
        "stato": "online"
        }
        peers.append(me)

    asyncio.create_task(gossip.gossip(peers, ip_personale))
    task_server = asyncio.create_task(gossip.ascolto(porta, peers, richieste_in_attesa, chiave, chiave_pubblica, gpg, fingerprint, password, alfabeto, session))
    asyncio.create_task(gossip.ceck_unreachable(peers))
    
    A = True
    while A:
        ris = await asyncio.to_thread(input, "1: Visualizza tutti i peer online sulla rete | 2: Inserisci l'indirizzo:porta di un peer per contattarlo | 3: Attendi che qualcuno ti contatti")
        
        if ris == "1":
            online = gossip.lista_peers("online", peers)
            for o in online:
                print(o["nome"], " ip: ", o["ip"], "Porta: ", o["porta"])
        
        if ris == "2":
            ip_destinazione = await asyncio.to_thread(input, "Inserisci ip: ")
            porta_destinazione = await asyncio.to_thread(input, "inserisci porta: ")
            
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip_destinazione, int(porta_destinazione)), timeout=3
                )
                
                writer.write("CHAT_REQUEST".encode())               # Richiesta chat | Client --> Server
                await writer.drain()
                print(f"Richiesta chat inviata con successo a {ip_destinazione}, attendo conferma...")

                data = await reader.read(1024)
                if(data.decode() == "OK_CHAT"):                     # Ricezione risposta | Client <-- Server

                    writer.write(Nome.encode())
                    await writer.drain()                            # Invio Nome | Client --> Server

                    data = await reader.read(1024)                  # Invio Nome | Client <-- Server
                    Nome_server = data.decode()
                    print("Stai parlando con: ", Nome_server)

                    data = await reader.read(1024)                  # Ricezione esito | Client <-- Server
                    esito = data.decode()

                    if esito == "ACCEPTED":
                        print(f"Connessione accettata da {Nome_server}, ({ip_destinazione}:{porta_destinazione})")
                        
                        writer.write(Alg.encode())                  # Invio Alg | Client --> Server
                        await writer.drain()
                        
                        data = await reader.read(1024)          # Ricezione esito | Client <-- Server
                        if(data.decode() == "ALG_MISMATCH"):
                            print(f"Algoritmo incompatibile con {Nome_server}, connessione chiusa")
                            writer.close()
                            await writer.wait_closed()
                            return
                        
                        gpg_sessione = None
                        fingerprint_server = None

                        if (Alg.lower() == "pgp" and data.decode() == "OK_PGP"):
                            print(f"Algoritmo compatibile con {Nome_server}!")
                            print("Avvio lo scambio di chiavi pubbliche...")
                            
                            dati = chiave_pubblica.encode('utf-8')
                            writer.write(len(dati).to_bytes(4, 'big') + dati)
                            await writer.drain()
                                                    # Scambio chiavi
                            lunghezza_bytes = await reader.readexactly(4)
                            lunghezza = int.from_bytes(lunghezza_bytes, 'big')
                            chiave_pubblica_server = (await reader.readexactly(lunghezza)).decode('utf-8')

                            cartella_temp = tempfile.TemporaryDirectory()
                            gpg_sessione = gnupg.GPG(gnupghome=cartella_temp.name)
                            risultato_import = gpg_sessione.import_keys(chiave_pubblica_server)
                            fingerprint_server = risultato_import.fingerprints[0]

                        asyncio.create_task(network.ricevi(reader, writer, Nome_server, Alg, chiave, alfabeto, gpg, password))
                        await network.invia_async(reader, writer, Alg, chiave, gpg_sessione, fingerprint_server, alfabeto, session)
                        A = False
                    elif esito == "REFUSED":
                        print(f"Connessione rifiutata da {ip_destinazione}:{porta_destinazione}")
                        
                else:
                    print(f"Connessione rifiutata da {ip_destinazione}:{porta_destinazione}")
                    
            except (ConnectionRefusedError, ConnectionResetError, asyncio.TimeoutError, OSError):
                print("Errore nella connessione, peer inesistente/irraggiungibile")
                peers_ref = {(p["ip"], p["porta"]): p for p in peers}
                peers_ref[ip_destinazione, porta_destinazione]["stato"] = "unreachable"
            
            
            
        frase = f"In ascolto sulla porta {porta} "
        if ris == "3":
            Contatto = False
            while(Contatto == False):
                if richieste_in_attesa:                             # True se la lista non è vuota
                    os.system("cls" if os.name == "nt" else "clear")
                    richiesta_dal_menu = richieste_in_attesa[0]
                    testo = "Richiesta di connessione da parte di:" + str(richiesta_dal_menu["indirizzo_client"]) + "con nome: " + str(richiesta_dal_menu["nome"])
                    risposta = await asyncio.to_thread(input, str(testo))
                    B = True
                    while B:
                        risposta = await asyncio.to_thread(
                            input, "Accettare? | y/n\n"
                        )
                        if(risposta.lower() == "y" or risposta.lower() == "s"):
                            print("\033[32m Connessione stabilita con ", richiesta_dal_menu["indirizzo_client"],"! \033[0m")
                            richiesta_dal_menu["decisione"] = "ACCETTATA"
                            A = False
                            B = False
                            Contatto = True
                            
                        elif(risposta.lower() == "n"):
                            richiesta_dal_menu["decisione"] = "RIFIUTATA"
                            B = False
                            input(f"\033[31m Connessione rifiutata, attendo input... \033[0m")
                            
                            os.system("cls" if os.name == "nt" else "clear")
                        else:
                            os.system("cls" if os.name == "nt" else "clear")
                            print("Non hai selezionato nessuna delle opzioni possibili!")
                else:
                    os.system("cls" if os.name == "nt" else "clear")
                    frase = frase + "."
                    print(frase)
                    await asyncio.sleep(2)
                
    await task_server
    
asyncio.run(main())