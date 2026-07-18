import time
# -----------------  FUNZIONI SECELTA -----------------

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
    NomeServ = "Server"
    while B:
        risposta = input("Vuoi scegliere un \033[1m nome \033[0m ? (y/n): ")
        if risposta.lower() == "y" or risposta.lower() == "s":
            NomeServ = input("Inserisci il \033[1m nome \033[0m: ")
            B = False
        elif risposta.lower() == "n":
            B = False
        else:
            print("Non hai selezionato nessuna delle opzioni possibili! (y/n)")
            
    return NomeServ

def seleziona_alg():
    C = True
    while C:
        risposta = input("Scegli la crittografia |\033[34m Cesare, Xor, pgp \033[0m|: ")
        if risposta.lower() == "cesare":
            Alg = "cesare"
            C = False
        elif risposta.lower() == "xor":
            Alg = "xor"
            C = False
        elif risposta.lower() == "pgp":
            Alg = "pgp"
            C = False
        else:
            print("Non hai selezionato nessuna delle opzioni possibili! |\033[34m Cesare, Xor, pgp \033[0m|")
    return Alg

def memorizza(Nome, porta, Alg, fingerprint):
    risposta = input("Vuoi memorizzare questi dati e sovrascrivere i precedenti? ")
    if risposta.lower() == "y" or risposta.lower() == "s":
        with open("config.txt", "w") as f:
            f.write(f"{Nome}\n")
            f.write(f"{porta}\n")
            f.write(f"{Alg}\n")
            f.write(f"{time.time()}\n")
            if(fingerprint == None):
                f.write("")
            else:
                f.write(f"{fingerprint}")
    else:
        print("I dati non sono stati sovrascritti. ")
        
def memorizza_no_conferma(Nome, porta, Alg, fingerprint):
    with open("config.txt", "w") as f:
        f.write(f"{Nome}\n")
        f.write(f"{porta}\n")
        f.write(f"{Alg}\n")
        f.write(f"{time.time()}\n")
        if(fingerprint == None):
                f.write("")
        else:
            f.write(f"{fingerprint}")
