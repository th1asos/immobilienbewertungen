'''
sortby=19 -> sortieren nach Aktualität
sortby=0 -> sortieren nach Top-Immo
parentcat=1 -> Wohnung
parentcat=2 -> Haus
marketingtype=1 -> kaufen
marketingtype=2 -> mieten
marketingtype=6 -> Zwangsversteigerung
locationname -> Ort
'''
import streamlit as st
import re
import bs4
import requests
import json
import sqlite3
import datetime
import time

def hauptprogramm(url, headers, umkreissuche):
    response = requests.get(url, headers=headers)
    html_file = response.text

    soup = bs4.BeautifulSoup(html_file, 'html.parser')
     
    # Suche nach den Schlüsselwörtern ohne beautifulsoup
    compiler = re.compile(r'broker_id":(.*?),"object_area":(.*?),"object_city":(.*?),"object_currency":(.*?),"object_features":(.*?),"object_federalstate":(.*?),"object_gok":(.*?),"object_is_special":(.*?),"object_label":(.*?),"object_marketingtype":(.*?),"object_objekt_nutzungsart":(.*?),"object_objekt_zustand":(.*?),"object_objektart_sub":(.*?),"object_price":(.*?),"object_rooms":(.*?),"object_listingtype":(.*?),"app_server')
    # Finde alle Daten
    data = re.findall(compiler, html_file)

    naechste_seite=""
    #naechste_seite = soup.find('a', {'class': 'col-sm-3 col-xs-1 pull-right text-right'})['href']
    if soup.find('a', {'class': 'col-sm-3 col-xs-1 pull-right text-right'}) is not None:
        naechste_seite = soup.find('a', {'class': 'col-sm-3 col-xs-1 pull-right text-right'})['href']
    if naechste_seite:
        url_neu = 'https://www.immonet.de' + naechste_seite
    else:
        url_neu = ""
    if data:  
        waehrung = data[0][3]
        object_gok = data[0][6]
        
        baualterkategorie = data[0][8]
        zustand = data[0][11]

        # Entferne die eckigen Klammern
        waehrung = waehrung[1:-1]
        object_gok = object_gok[1:-1]
        baualterkategorie = baualterkategorie[1:-1]
        zustand = zustand[1:-1]

        # Teile den String an den Kommas auf
        waehrung_values = waehrung.split(',')
        
        object_gok_values = object_gok.split(',')
        baualterkategorie_values = baualterkategorie.split(',')
        zustand_values = zustand.split(',')
        
        # Iteriere durch die Werte und gebe sie aus
        # Variablen initialisieren
        anbieter_id = None
        strasse = None
        plz = None
        stadt = None
        bundesland = None
        staat = None
        object_typ = None
        object_art = None
        baujahr = None
        qm = None
        raeume = None
        balkon = None
        heizungsart = None
        kueche = None
        garten = None
        ausstattung = None
        effizienzklasse = None
        endenergieverbrauch = None
        befeuerungsart = None
        baujahr_heizung = None
        titel = None
        ausstattung_beschreibung = None
        umgebungsbeschreibung = None
        sonstige_beschreibung = None
        objekt_beschreibung = None
        transaktionsart = None
        preis = None
        courtage = None
        kaltmiete = None
        vorauszahlende_betriebskosten = None
        vorauszahlende_heizkosten = None
        hausgeld = None
        ruecklagen = None
        vermietet_seit = None
        letzte_mieterhöhung = None
        #object_id = None
        
        
        for i in range(1, len(object_gok_values)):
            
            #time.sleep(10)
            # Anführungszeichen entfernen
            object_gok_values[i] = object_gok_values[i].strip('"')
            
            object_id=[]
            element = soup.find('a', {'data-global-object-key': object_gok_values[i]})
            if element is not None and element.has_attr('data-object-id'):
                object_id = element['data-object-id']
            #object_id = soup.find('a', {'data-global-object-key': object_gok_values[i]})['data-object-id']
            else:
                continue
            waehrung=waehrung_values[i].strip(']')
            waehrung=waehrung.strip('"')
            baualterkategorie=baualterkategorie_values[i].strip(']')
            baualterkategorie=baualterkategorie.strip('"')

            if len(zustand_values) == 0:
                zustand = None
            else:
                zustand = zustand_values[0].strip(']')
                zustand = zustand.strip('"')    
            
            url_expose="https://www.immonet.de/angebot/" + object_id
            #st.write(url_expose)
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

            response_expose = requests.get(url_expose, headers=headers)
            html_file_expose = response_expose.text

            # Verwende die BeautifulSoup-Bibliothek, um den HTML-Code zu parsen
            soup_expose = bs4.BeautifulSoup(html_file_expose, 'html.parser')

            # Hier finden sich die meisten Daten (da in Javascript-Variable, funktioniert beautifulsoup nicht, daher normal parsen
            try:
                json_string_orig = re.search(r'JSON.parse\((.*?)\);', html_file_expose).group(1)
            except AttributeError:
                continue # Falls Expose nicht mehr vorhanden, dann nächsten Wert der Schleife lesen
            
            json_string = json_string_orig[1:-1]

            # Zeichen ersetzen, die Pobleme bereiten
            json_string = json_string.replace('\\\\"', "'") # lösche Doppelte Anführungszeichen
            json_string = json_string.replace('\\', '')
            json_string = json_string.replace('', '')
            json_string = json_string.replace('m²', 'qm')
            
           # Lese den json-Teil als JSON ein
            #data = json.loads(json_string)
            try:
                data = json.loads(json_string, strict=False)
            except json.JSONDecodeError:
                #print("Fehler im JSON-String")
                st.warning("Fehler im JSON-String", icon="⚠️")
                st.write(json_string_orig)
                st.write(json_string)
                pass
     
            if 'area' in data:
                qm = data['area']
            else:
                qm= None
            if 'zip' in data:
                plz = data['zip']
            else:
                plz = None        
            if 'objectcat' in data:
                object_typ = data['objectcat']
            if 'pers' in data:
                anbieter_id = data['pers']
            if 'rooms' in data:
                raeume = data['rooms']
            if 'buildyear' in data:
                baujahr = data['buildyear']
            if 'fed' in data:
                bundesland = data['fed']
            if 'city' in data:
                stadt = data['city']
            if 'obtyp' in data:
                object_art = data['obtyp']
            if 'balcn' in data:
                balkon = data['balcn']
            if 'heatr' in data:
                heizungsart = data['heatr']
            if 'title' in data:
                titel = data['title']
            try:
                preis = data['price']
            except KeyError:
                preis = None
            except TypeError:
                preis = None
           
            if 'kitch' in data:
                kueche = data['kitch']
            if 'marketingtype' in data:
                transaktionsart = data['marketingtype']
            
            if 'gardn' in data:
                garten = data['gardn']
            if 'state' in data:
                staat  = data['state']

            # Finde den Tag, der die Strasse enthält
            strasse_tag = soup_expose.find('p', {'class': 'text-100 pull-left'})
            if strasse_tag: # Prüfe, ob der Tag existiert
                strasse = strasse_tag.text.split('\n')[1].strip() # Wenn ja, extrahiere den Text
            else:
                strasse = None  # Wenn nein, setze den Wert auf None
                
            # Suche nach dem Element mit der ID "courtageValue"
            courtage_element = soup_expose.find(id="courtageValue")
            courtage_text = courtage_element.text
            courtage = re.sub(r'\s+', '', courtage_text) # Entferne alle Leerzeichen und Zeilenumbrüche
            courtage = courtage.replace("%", "") # Entferne Prozentzeichen

            # regulärer Ausdruck, um den Zahlwert zu extrahieren
            pattern = r"(\d+[,.]\d+)"

            # Suche nach dem regulären Ausdruck im Text
            match = re.search(pattern, courtage_text)

            # Wenn eine Übereinstimmung gefunden wurde, schreibe den Zahlwert in die neue Variable
            if match:
                courtage = float(match.group(1).replace(",", "."))
            else:
                courtage = 0.0
            
            #st.write(courtage_text, courtage)

            # Finde den Wert der Effizienzklasse
            effizienzklasse_element = soup_expose.find('div', {'id': 'efficiencyValue'})
            effizienzklasse=[]
            if effizienzklasse_element:
                effizienzklasse = effizienzklasse_element.text
            else:
                effizienzklasse = None

            # Finde den Endenergieverbrauch
            energy_value_element = soup_expose.find('div', {'id': 'energyValue'})
            energy_value=[]
            if energy_value_element:
                energy_value = energy_value_element.text
                endenergieverbrauch = re.findall(r'\d+', energy_value)[0] # Verwende einen regulären Ausdruck, um den Endenergieverbrauch zu extrahieren
            else:
                endenergieverbrauch = None

            # Finde den Wert der Befeuerungsart
            heater_supplier_value_element = soup_expose.find('div', {'id': 'heaterSupplierValue'})
            heater_supplier_value=[]
            if heater_supplier_value_element:
                heater_supplier_value = heater_supplier_value_element.text
                befeuerungsart = re.sub('\s+', '', heater_supplier_value) # Entferne alle Leerzeichen
            else:
                befeuerungsart = None

            # Baujahr Heizung
            year_build_element = soup_expose.find(id="yearBuildByPassValue")
            baujahr_heizung=[]
            if year_build_element:
                baujahr_heizung = re.findall(r'\d+', year_build_element.text)[0] # Extraktion des Baujahrs
            else:
                baujahr_heizung = None

            # Ausstattung
            features = soup_expose.find_all(attrs={"id": re.compile("featureId_")})
            features_list=[]
            for feature in features:
                features_list.append(feature.text.strip())
            if features_list:
                ausstattung = ', '.join(features_list) # Speichere den Text in einer einzigen Variablen
            else:
                ausstattung = None
            

            # Objektbeschreibung
            ausstattung_div = soup_expose.find('div', {'id': 'ausstattung'})
            if ausstattung_div is not None:
                ausstattung_beschreibung = re.sub(r'\s+', ' ', ausstattung_div.text).strip() # Entferne alle tags und Leerzeichen vor und hinter dem Text
            else:
                ausstattung_beschreibung = None

            # Laufende Kosten
            text = None
            
            if soup_expose.find('p', {'id': 'objectDescription'}) is not None:
                text = soup_expose.find('p', {'id': 'objectDescription'}).text
                if re.search(r'Kaltmiete: Euro (\d+[.,]\d+)', text):
                    kaltmiete = re.search(r'Kaltmiete: Euro (\d+[.,]\d+)', text).group(1)
                    kaltmiete = kaltmiete.replace(',', '.')
                    #st.write('Kaltmiete: ', kaltmiete, object_id)
                else:
                    kaltmiete=""
                if text:
                    objekt_beschreibung = text
                else:
                    objekt_beschreibung = ""
                    
            
                if re.search(r'Vorauszahlende Betriebskosten: Euro (\d+[.,]\d+)', text):
                    vorauszahlende_betriebskosten = re.search(r'Vorauszahlende Betriebskosten: Euro (\d+[.,]\d+)', text).group(1)
                else:
                    vorauszahlende_betriebskosten = None

                if re.search(r'Vorauszahlende Heizkosten: Euro (\d+[.,]\d+)', text):
                    vorauszahlende_heizkosten = re.search(r'Vorauszahlende Heizkosten: Euro (\d+[.,]\d+)', text).group(1)
                else:
                    vorauszahlende_heizkosten = None

                if re.search(r'Hausgeld: Euro (\d+[.,]\d+)', text):
                    hausgeld = re.search(r'Hausgeld: Euro (\d+[.,]\d+)', text).group(1)
                else:
                    hausgeld = None

                if re.search(r'Rücklagen: Euro (\d+[.,]\d+)', text):
                    ruecklagen = re.search(r'Rücklagen: Euro (\d+[.,]\d+)', text).group(1)
                else:
                    ruecklagen = None
                    
                if re.search(r'vermietet seit: (\d+[.,]\d+[.,]\d+)', text):
                    vermietet_seit = re.search(r'vermietet seit: (\d+[.,]\d+[.,]\d+)', text).group(1)
                else:
                    vermietet_seit = None

                if re.search(r'Letzte Mieterhöhung: (\d+[.,]\d+[.,]\d+)', text):
                    letzte_mieterhöhung = re.search(r'Letzte Mieterhöhung: (\d+[.,]\d+[.,]\d+)', text).group(1)
                else:
                    letzte_mieterhöhung = None
            else:
                    kaltmiete = None
           
            # Beschreibung der Umgebung
            location_description = soup_expose.find('p', {'id': 'locationDescription'})
            if location_description is not None:
                umgebungsbeschreibung = re.sub(r'<.*?>', '', str(location_description))

            # Sonstige Beschreibung
            other_description = soup_expose.find(id="otherDescription")
            if other_description is not None:
                sonstige_beschreibung = re.sub(r'<.*?>', '', str(other_description))
            
            if stadt != ort and umkreissuche == False:
                st.success('Daten geladen!')
                st.stop()
            else:
                st.write(url_expose)

            sql = "SELECT * FROM immo_data WHERE object_id = ?"
            cursor.execute(sql, (object_id,))
            result = cursor.fetchone()
            
            if result:
                sql = "UPDATE immo_data SET letztes_update = ?, anbieter_id = ?, strasse = ?, plz = ?, stadt = ?, bundesland = ?, staat = ?, object_typ = ?, object_art = ?, baujahr = ?, qm = ?, raeume = ?, balkon = ?, heizungsart = ?, kueche = ?, garten = ?, ausstattung = ?, baualterkategorie = ?, zustand = ?, effizienzklasse = ?, endenergieverbrauch = ?, befeuerungsart = ?, baujahr_heizung = ?, titel = ?, ausstattung_beschreibung = ?, umgebungsbeschreibung = ?, sonstige_beschreibung = ?, objekt_beschreibung = ?, transaktionsart = ?, preis = ?, waehrung = ?, courtage = ?, kaltmiete = ?, vorauszahlende_betriebskosten = ?, vorauszahlende_heizkosten = ?, hausgeld = ?, ruecklagen = ?, vermietet_seit = ?, letzte_mieterhöhung = ? WHERE object_id = ?"
                cursor.execute(sql, (datetime.date.today(), anbieter_id, strasse, plz, stadt, bundesland, staat, object_typ, object_art, baujahr, qm, raeume, balkon, heizungsart, kueche, garten, ausstattung, baualterkategorie, zustand, effizienzklasse, endenergieverbrauch, befeuerungsart, baujahr_heizung, titel, ausstattung_beschreibung, umgebungsbeschreibung, sonstige_beschreibung, objekt_beschreibung, transaktionsart, preis, waehrung, courtage, kaltmiete, vorauszahlende_betriebskosten, vorauszahlende_heizkosten, hausgeld, ruecklagen, vermietet_seit, letzte_mieterhöhung, object_id))
            else:    
                sql = 'INSERT INTO immo_data (letztes_update, anbieter_id, strasse, plz, stadt, bundesland, staat, object_typ, object_art, baujahr, qm, raeume, balkon, heizungsart, kueche, garten, ausstattung, baualterkategorie, zustand, effizienzklasse, endenergieverbrauch, befeuerungsart, baujahr_heizung, titel, ausstattung_beschreibung, umgebungsbeschreibung, sonstige_beschreibung, objekt_beschreibung, transaktionsart, preis, waehrung, courtage, kaltmiete, vorauszahlende_betriebskosten, vorauszahlende_heizkosten, hausgeld, ruecklagen, vermietet_seit, letzte_mieterhöhung, object_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                cursor.execute(sql, (datetime.date.today(), anbieter_id, strasse, plz, stadt, bundesland, staat, object_typ, object_art, baujahr, qm, raeume, balkon, heizungsart, kueche, garten, ausstattung, baualterkategorie, zustand, effizienzklasse, endenergieverbrauch, befeuerungsart, baujahr_heizung, titel, ausstattung_beschreibung, umgebungsbeschreibung, sonstige_beschreibung, objekt_beschreibung, transaktionsart, preis, waehrung, courtage, kaltmiete, vorauszahlende_betriebskosten, vorauszahlende_heizkosten, hausgeld, ruecklagen, vermietet_seit, letzte_mieterhöhung, object_id))
            conn.commit()
        #print()
        st.write(url_neu)    
        return (url_neu)

st.header("Immobilien importieren")

dbname = 'immo.db'
conn = sqlite3.connect(dbname)
cursor = conn.cursor()

marketingtype='1'
ort = st.text_input("Gebe den gewünschten Ort ein: ", placeholder="Ort")

col1, col2,col3, col4=st.columns(4)
with col1:
    art = st.radio("Wähle aus: ", ('Haus', 'Wohnung'))
    if art =='Haus':
        parentcat='2'
    else:
        parentcat = '1'
with col2:   
    typ = st.radio(" Wähle aus:", ('kaufen', 'mieten', 'Zwangsversteigerung'))
    if typ == 'kaufen':
        marketingtype='1'
    elif typ == 'mieten':
        marketingtype='2'
    elif typ == 'Zwangsversteigerung':
        marketingtype='6'    
with col3:    
    sort = st.radio("Sortierung nach:", ('Aktualität', 'Top-Immo'))    
    if sort == 'Aktualität':
        sortby='19'
    else:
        sortby='0'
with col4:
    umkreissuche = st.checkbox("Umkreissuche an")

# URL der Seite
if ort:
    url = 'https://www.immonet.de/immobiliensuche/sel.do?&sortby=' + sortby + '&suchart=1&objecttype=1&marketingtype=' + marketingtype +'&parentcat=' + parentcat +'&locationname=' + ort
    #url = 'https://www.immonet.de/immobiliensuche/sel.do?marketingtype=1&city=82317&parentcat=1&suchart=1&objecttype=1&listsize=27&pageoffset=1&sortby=19'
    #url = 'https://www.immonet.de/immobiliensuche/sel.do?pageoffset=1&objecttype=1&listsize=26&locationname=Mitte%2C+M%C3%BClheim&acid=&actype=&district=10954&ajaxIsRadiusActive=true&sortby=19&suchart=2&radius=0&pcatmtypes=1_1&pCatMTypeStoragefield=&parentcat=1&marketingtype=1&fromprice=&toprice=&fromarea=&toarea=&fromplotarea=&toplotarea=&fromrooms=&torooms=&objectcat=-1&wbs=-1&fromyear=&toyear=&fulltext=&absenden=Ergebnisse+anzeigen'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Referer': 'https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=1&parentcat=1&locationname=' + ort
    }
if st.button("Jetzt importieren"):
    if ort == '':
        st.warning('Bitte einen Ort eingeben.')
        st.stop()
    url_neu=hauptprogramm(url, headers, umkreissuche)       

    while url_neu:
        url_neu=hauptprogramm(url_neu, headers, umkreissuche)

    st.success('Daten geladen!')
# Schließe Datenbankverbindung
conn.close()
