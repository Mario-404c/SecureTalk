import time
import socket
import os, struct
from .encryption import * 
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio

# ----------------- FUNZIONI SOCKET -----------------

async def ricevi(reader, writer, NomeCli, Alg, chiave, alfabeto, gpg, password):
    while True:
        try:
            if Alg == "gpg":
                data = await reader.read(65535)
            else:
                data = await reader.read(1024)
                
            if not data:
                print("Connessione chiusa dal server")
                break
            
            else:
                chiper = data.decode()
                if Alg == "cesare":
                    chiaro = decripta_cesare(chiper, chiave, alfabeto)
                elif Alg == "xor":
                    chiaro = decripta_Xor(chiper, chiave)
                elif Alg.lower() =="pgp":
                    risultato = gpg.decrypt(chiper, passphrase=password)
                    if risultato.ok:
                        chiaro = risultato.data.decode('utf-8')
                    else:
                        print("Errore nella decrittazione del messaggio: ", risultato.status)
                    
                print(NomeCli, ": ", chiaro)
                
        except Exception as e:
            print("Errore ricezione:", e)
            break

async def invia_async(reader, writer, Alg, chiave, gpg_sessione, fingerprint_client, alfabeto, session):
    with patch_stdout():  
        while True:
            try:
                chiaro = await session.prompt_async("Tu: ")
            except (EOFError, KeyboardInterrupt):
                print("\nChiusura invio richiesta dall'utente")
                break
            if Alg == "cesare":
                chiper = cripta_cesare(chiaro, chiave, alfabeto)
            elif Alg == "xor":
                chiper = cripta_Xor(chiaro, chiave)
            elif Alg.lower() =="pgp":
                risultato = gpg_sessione.encrypt(chiaro, recipients=[fingerprint_client], always_trust=True)
                if risultato.ok:
                    chiper = str(risultato)
                else:
                    print("Errore nella cifratura del messaggio: ", risultato.status)
                    continue
            writer.write(chiper.encode())
            await writer.drain()
