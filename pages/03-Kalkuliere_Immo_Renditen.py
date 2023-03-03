import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd
import pages.functions.mietpreisspiegel

def sql_statement (id, date, tabellenname, wertgutachten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite):
    cursor.execute(f"SELECT object_id FROM {tabellenname} WHERE object_id = ?", (id,))
    result = cursor.fetchone()
    if result is not None:
        cursor.execute(f"UPDATE {tabellenname} SET wertgutachtenkosten = ?, renovierungskosten = ?, umbaukosten = ?, verwaltungskosten_pro_jahr = ?, instandhaltungskosten_pro_jahr_qm = ?, mietspiegelmiete_pro_qm = ?, eigenkapital = ?, eigenkapitalrendite = ?, letztes_update = ? WHERE object_id = ?", (wertgutachten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite, date, id))
        conn.commit()
    else:
        cursor.execute(f"INSERT INTO {tabellenname} (object_id, wertgutachtenkosten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite, letztes_update) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, wertgutachten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite, date))
        conn.commit()
    try:
        conn.commit()
    except sqlite3.OperationalError as e:
        #print("Es ist ein Fehler aufgetreten:", e)
        st.warning(e, icon="⚠️")

def sql_statement_kalk (id, date, tabellenname, wertgutachten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite):
    cursor.execute(f"SELECT object_id FROM {tabellenname} WHERE object_id = ?", (id,))
    result = cursor.fetchone()
    if result is not None:
        cursor.execute(f"UPDATE {tabellenname} SET wertgutachtenkosten = ?, renovierungskosten = ?, umbaukosten = ?, verwaltungskosten_pro_jahr = ?, instandhaltungskosten_pro_jahr_qm = ?, mietspiegelmiete_pro_qm = ?, eigenkapital = ?, eigenkapitalrendite = ?, letztes_update = ? WHERE object_id = ?", (wertgutachten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite, date, id))
        conn.commit()
    else:
        cursor.execute(f"INSERT INTO {tabellenname} (object_id, wertgutachtenkosten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite, letztes_update) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, wertgutachten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite, date))
        conn.commit()
    try:
        conn.commit()
    except sqlite3.OperationalError as e:
        #print("Es ist ein Fehler aufgetreten:", e)
        st.warning(e, icon="⚠️")
        
def clean_courtage(courtage_tmp):
    # String extrahieren
    # check if the variable is a string
    if isinstance(courtage_tmp, str):
        courtage = courtage_tmp.split('%')[0]
    else:
        courtage = courtage_tmp

    # Courtage von String nach Nummer konvertieren
    if (isinstance(courtage, int) or isinstance(courtage, float)):
        print("courtage is a number")
    # check if the variable is a string
    elif isinstance(courtage, str):
        # try to convert the string to float
        try:
            courtage = float(courtage.replace(',', '.'))
            #print("courtage is a number")
        except ValueError:
            #print("courtage is not a number")
            courtage=0.0
    else:
        #print("courtage is a string")
        courtage=0.0
        
    return courtage

def ermittel_grunderwerbssteuer(kaufpreis, bundesland):    
    # Grunderwerbssteuer
    if bundesland  in ["Schleswig-Holstein", "Brandenburg", "Thüringen", "Saarland", "Nordrhein-Westfalen"] :
        grunderwerbssteuer_betrag = kaufpreis * 0.065
    elif bundesland in ["Berlin", "Hessen", "Mecklenburg-Vorpommern"]:
        grunderwerbssteuer_betrag = kaufpreis * 0.06
    elif bundesland == "Hamburg ":
        grunderwerbssteuer_betrag = kaufpreis * 0.055
    elif bundesland in ["Bayern", "Sachsen"]:
        grunderwerbssteuer_betrag = kaufpreis * 0.035
    else:
        grunderwerbssteuer_betrag = kaufpreis * 0.05          
    return grunderwerbssteuer_betrag

def anuitaeten_rechner(erweiterte_anschaffungskosten, nettomieteinnahmen_nach_bewirtschaftungskosten, ZINSSATZ, EIGENKAPITAL, LAUFZEIT):
    monatliche_nettomieteinahmen = nettomieteinnahmen_nach_bewirtschaftungskosten / 12
    fremdkapital = erweiterte_anschaffungskosten - EIGENKAPITAL  # Fremdkapital (Kredit)
    data=[]
    
    # Monatliche Kreditrate berechnen
    if LAUFZEIT > 0 and ZINSSATZ > 0:
        kreditrate = fremdkapital * (ZINSSATZ / 12) / (1 - (1 + ZINSSATZ / 12) ** (-LAUFZEIT * 12))

        # Berechnungen für jeden Monat
        jahrliche_eigenkapitalrendite = 0
        gesamte_eigenkapitalrendite = 0

        for monat in range(1, LAUFZEIT * 12 + 1):
            zinsen = fremdkapital * ZINSSATZ / 12
            tilgung = kreditrate - zinsen
            fremdkapital = fremdkapital - tilgung
            
            #Eigenkapitalrendite = (Mieteinnahmen - Zinsen) / (Fremdkapital + 20000)
            eigenkapitalrendite = (monatliche_nettomieteinahmen - zinsen) * 100 * 12/ EIGENKAPITAL
            EIGENKAPITAL += tilgung
            
            # Durchschnittliche jährliche Eigenkapitalrendite berechnen
            if monat % 12 == 0:
                jahrliche_eigenkapitalrendite = jahrliche_eigenkapitalrendite + eigenkapitalrendite
                #print("Durchschnittliche jährliche Eigenkapitalrendite für Jahr", int(monat / 12), ":", jahrliche_eigenkapitalrendite / 12)
                jahrliche_eigenkapitalrendite = 0
            
            # Gesamte Eigenkapitalrendite berechnen
            gesamte_eigenkapitalrendite = gesamte_eigenkapitalrendite + eigenkapitalrendite
    eigenkapitalrendite = gesamte_eigenkapitalrendite / (LAUFZEIT * 12)
    
    return eigenkapitalrendite

def input_parameter():
    st.header("Parameterwerte definieren")
    
    st.subheader("Mieteinnahmen")
    max_mietaufschlag = st.number_input("Max. Mietaufschlag", help="Maximaler Mietaufschlag auf die aktuelle Kaltmiete in Prozent, wenn Objekt bereits vermietet und Mietspiegelmiete > aktuelle Kaltmiete des Objekts",min_value=0.0, max_value=16.0, value=10.0, step=1.0)
    max_mietaufschlag_prozent = max_mietaufschlag / 100
    
    st.subheader("Kaufnebenkosten")
    col1, col2=st.columns(2)
    with col1:
        notar_prozent = st.number_input("Notar Prozentsatz", value=2.0, step=0.1)
    with col2:
        wertgutachten_prozent = st.number_input("Wertgutachten Prozentsatz", help="Kurzgutachten ca. 0,2%, umfassendes Gutachten ca. 0,4%", value=0.2, step=0.1)
    notar_prozentsatz = notar_prozent / 100
    wertgutachten_prozentsatz = wertgutachten_prozent / 100
    
    st.subheader("Herrichtungskosten")
    col1, col2=st.columns(2)
    with col1:
        renovierungskosten_prozent = st.number_input("Renovierungskosten Prozentsatz", value=5, step=1)
    with col2:
        umbaukosten_prozent = st.number_input("Umbaukosten Prozentsatz", value=5, step=1)
    renovierungskosten_prozentsatz = renovierungskosten_prozent / 100
    umbaukosten_prozentsatz = umbaukosten_prozent / 100
    
    st.subheader("Bewirtschafftungskosten")
    col1, col2=st.columns(2)
    with col1:
        verwaltungskosten_pro_jahr = st.number_input("Verwaltungskosten pro Jahr", value=260, step=1)
    with col2:
        instandhaltungskosten_pro_jahr_pro_qm = st.number_input("Instandhaltungskosten p.a. je m²", value=18.0, step=0.1)
    
    st.subheader("Rendite-Kennziffern")
    col1, col2, col3=st.columns(3)
    with col1:
        zins = st.number_input("Zinssatz für Bankkredit", value=3.5)
    with col2:
        laufzeit = st.number_input("Laufzeit für Bankkredit", value=10, step=1)
    with col3:
        eigenkapital_prozent = st.number_input("EK % von Erweiterten AK", value=33, step=1)
    zinssatz = zins / 100
    eigenkapital_prozentsatz = eigenkapital_prozent  / 100
     
    return notar_prozentsatz, wertgutachten_prozentsatz, renovierungskosten_prozentsatz, umbaukosten_prozentsatz, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_pro_qm, zinssatz, eigenkapital_prozentsatz, laufzeit, max_mietaufschlag_prozent
    
#####################################
# Hauptteil
#####################################
#ABFRAGE_ORT='Kellenhusen'

# Verbindung zur Datenbank herstellen
dbname = 'immo.db'
conn = sqlite3.connect(dbname)
cursor = conn.cursor()

st.title("Renditerechner")

NOTAR_PROZENTSATZ, WERTGUTACHTEN_PROZENTSATZ,RENOVIERUNGSKOSTEN_PROZENTSATZ, UMBAUKOSTEN_PROZENTSATZ, VERWALTUNGSKOSTEN_PRO_JAHR, INSTANDHALTUNGSKOSTEN_PRO_JAHR_QM, ZINSSATZ, EIGENKAPITALPROZENTSATZ, LAUFZEIT, MAX_MIETAUFSCHLAG=input_parameter()

if st.button("Jetzt berechnen"):
    
    rendite_liste = []
    data_new=[]
    counter=0
    
    # Abfrage der Daten
    #cursor.execute("SELECT object_id, plz, stadt, bundesland, object_typ, object_art, baujahr, qm, raeume, preis, courtage FROM immo_data WHERE stadt=?", (ABFRAGE_ORT,))
    cursor.execute("SELECT object_id, plz, stadt, bundesland, object_typ, object_art, baujahr, qm, raeume, preis, courtage, kaltmiete FROM immo_data WHERE eigenkapitalrendite IS NULL")
    data = cursor.fetchall()
    
    with st.spinner('Berechne Daten'):

        # Kopieren der Daten in eine weitere Liste

        for row in data:
            object_id = row[0]
            plz = row[1]
            stadt = row[2]
            bundesland = row[3]
            immobilientyp = row[4] # Wohnung/Haus
            object_art = row[5]
            baujahr = row[6]
            wohnflaeche = row[7]
            zimmer = row[8]
            kaufpreis = row[9]
            #st.write("Objekt: ",object_id)
            #courtage = clean_courtage(row[10])
            courtage = row[10]
            kaltmiete = row[11]
            
            
            if wohnflaeche is not None and kaufpreis is not None:
                counter+=1
                # Kaufnebenkosten
                grunderwerbssteuer = ermittel_grunderwerbssteuer(kaufpreis, bundesland)
                notargebuehr = kaufpreis * NOTAR_PROZENTSATZ
                maklerkaution = kaufpreis * courtage / 100
                wertgutachten = kaufpreis * WERTGUTACHTEN_PROZENTSATZ
                
                #Herrichtungskosten
                renovierungskosten = kaufpreis * RENOVIERUNGSKOSTEN_PROZENTSATZ
                umbaukosten = kaufpreis * UMBAUKOSTEN_PROZENTSATZ
                
                # Erweiterte Anschaffungskosten
                summe_kaufnebenkosten = grunderwerbssteuer + notargebuehr + maklerkaution + wertgutachten
                summe_herrichtungskosten = renovierungskosten + umbaukosten
                erweiterte_anschaffungskosten = kaufpreis + summe_kaufnebenkosten + summe_herrichtungskosten
                
                # Bewirtschafftungskosten
                bewirtschaftungskosten = VERWALTUNGSKOSTEN_PRO_JAHR + INSTANDHALTUNGSKOSTEN_PRO_JAHR_QM * wohnflaeche
                
                # Nettomieteinnahmen
                mietspiegelmiete_pro_qm = pages.functions.mietpreisspiegel.mietspiegelpreis(qm=wohnflaeche,zimmer=zimmer, plz=plz)
                mietspiegelmieteinnahmen_monat = wohnflaeche * mietspiegelmiete_pro_qm
                
                if kaltmiete is not None:
                    if kaltmiete =="" or kaltmiete == 0:
                        kaltmiete = 0.0
                    else:
                        #st.write("Kaltmiete: ", kaltmiete, object_id)
                        kaltmiete = float(kaltmiete)
                        prozentsatz = (mietspiegelmieteinnahmen_monat - kaltmiete) / kaltmiete
                        if prozentsatz > 0 and prozentsatz < MAX_MIETAUFSCHLAG:
                            mietspiegelmieteinnahmen_monat = kaltmiete * (1+prozentsatz)
                        elif prozentsatz > 0 and prozentsatz > MAX_MIETAUFSCHLAG:
                            mietspiegelmieteinnahmen_monat = kaltmiete * (1+MAX_MIETAUFSCHLAG )
                else:
                    kaltmiete = 0.0
                    #st.write("Kaltmiete: ", kaltmiete, " Max. Mietaufschlag: ", 1+MAX_MIETAUFSCHLAG, " Mietspiegeleinnahmen-Monat: ", mietspiegelmieteinnahmen_monat, " Mietspiegelmiete Monat ", mietspiegelmiete_pro_qm*wohnflaeche)
                mietspiegelmieteinnahmen_jahr = mietspiegelmieteinnahmen_monat * 12
                nettomieteinnahmen_nach_bewirtschaftungskosten = mietspiegelmieteinnahmen_jahr - bewirtschaftungskosten
                
                
                # Renditeberechnung
                eigenkapital = erweiterte_anschaffungskosten * EIGENKAPITALPROZENTSATZ
                eigenkapitalrendite = anuitaeten_rechner(erweiterte_anschaffungskosten, nettomieteinnahmen_nach_bewirtschaftungskosten, ZINSSATZ, eigenkapital, LAUFZEIT)
                
                #print(object_id, eigenkapitalrendite)
                # DB Parameter
                TABELLENNAME='immo_data'
                TABELLENNAME_KALK='immo_data_kalk'
                
                date = datetime.now() # Get the current date
                datum_formatiert = date.strftime("%Y-%m-%d")
                
                # kopiere eigenkapitalrendite zur Liste
                data_new.append(row + (eigenkapitalrendite,))
                
                sql_statement (object_id, datum_formatiert, TABELLENNAME, wertgutachten, renovierungskosten, umbaukosten, VERWALTUNGSKOSTEN_PRO_JAHR, INSTANDHALTUNGSKOSTEN_PRO_JAHR_QM, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite)
                sql_statement (object_id, datum_formatiert, TABELLENNAME_KALK, wertgutachten, renovierungskosten, umbaukosten, VERWALTUNGSKOSTEN_PRO_JAHR, INSTANDHALTUNGSKOSTEN_PRO_JAHR_QM, mietspiegelmiete_pro_qm, eigenkapital, eigenkapitalrendite)
                                
    #             st.write("Grunderwerbssteuer: ", grunderwerbssteuer)
    #             st.write("Notargebühr: ", notargebuehr)
    #             st.write("Maklergebühr: ", maklerkaution)
    #             st.write("Wertgutachten: ", wertgutachten)
    #             st.write("EK: ", eigenkapital)
    #             st.write("Nettomieteinnahmen: ", nettomieteinnahmen_nach_bewirtschaftungskosten)
    #             st.write("Summe Kaufnebenkosten: ", summe_kaufnebenkosten)
    #             st.write("Summe Herrichtungskosten: ", summe_herrichtungskosten)
    #             st.write("Erweiterte AK: ", erweiterte_anschaffungskosten)
    #             st.write("EK-Prozentsatz: ", EIGENKAPITALPROZENTSATZ)
    #             st.write("Mietspiegelmieteinnahmen :", mietspiegelmieteinnahmen_jahr)
    #             st.write("Mietspiegelmiete: ", mietspiegelmiete_pro_qm)
    #             st.write("Wohnfläche: ", wohnflaeche)
   
    #st.write(data_new)
    st.write("Rendite für ", counter, " Objekte berechnet")
    # Ausgabe der Daten in einer Tabelle
    data_df = pd.DataFrame(data_new, columns=['object_id', 'plz', 'stadt', 'bundesland', 'object_typ', 'object_art', 'baujahr', 'qm', 'raeume', 'preis', 'courtage', 'kaltmiete', 'eigenkapitalrendite'])
    data_df.sort_values(by='eigenkapitalrendite', ascending=False, inplace=True)
    st.dataframe(data_df)
    
    conn.close()
