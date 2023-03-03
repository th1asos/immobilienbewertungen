import streamlit as st
import sqlite3
import pandas as pd
import pages.functions.mietpreisspiegel
import numpy as np
from streamlit_folium import folium_static
#from folium.plugins import Draw
import folium
import requests
import json
# import locale
# Streamlit App initialisieren
st.set_page_config(page_title="OpenStreetMap Geocoding", page_icon=":earth_americas:")
        
def tabellendaten():
    # Abfrage der Daten und Tabelle anlegen
    # Die COALESCE-Funktion wird verwendet, um den Wert von objekt_beschreibung durch einen leeren String zu ersetzen, wenn er NULL ist, da sonst Probleme bei Filterung von Einträgen mit Wert NULL
    cursor.execute("SELECT object_id, eigenkapitalrendite, plz, stadt, strasse, bundesland, staat, object_typ, object_art, baujahr, qm, kaltmiete, raeume, preis, courtage, wertgutachtenkosten, renovierungskosten, umbaukosten, verwaltungskosten_pro_jahr, instandhaltungskosten_pro_jahr_qm, eigenkapital, mietspiegelmiete_pro_qm, transaktionsart,  titel, objekt_beschreibung, ausstattung_beschreibung, umgebungsbeschreibung, sonstige_beschreibung, ausstattung, heizungsart, befeuerungsart, effizienzklasse, endenergieverbrauch, baujahr_heizung FROM immo_data ORDER BY eigenkapitalrendite DESC")
    data = cursor.fetchall()

    col_names=['Objekt-ID', 'Eigenkapitalrendite', 'PLZ', 'Ort', 'Strasse', 'Bundesland', 'Staat', 'Objekt-Typ', 'Objekt-Art', 'Baujahr', 'qm', 'Kaltmiete', 'Zimmer', 'Preis', 'Courtage', 'Wertgutachtenkosten', 'Renovierungskosten', 'Umbaukosten', 'Verwaltungskosten', 'Instandhaltungskosten', 'Eigenkapital', 'Mietspiegelmiete je qm', 'Transaktionsart', 'Titel', 'Objektbeschreibung', 'Ausstattungsbeschreibung', 'Umgebung', 'Sonstiges', 'Ausstattung', 'Heizungsart', 'Befeuerungsart', 'Effizienzklasse', 'Endenergieverbrauch', 'Baujahr Heizung']

    df = pd.DataFrame(data, columns=col_names)

    return df

def lies_von_db(tabelle, spalte, objekt_id):
    #st.write(tabelle, spalte, objekt_id)
    cursor.execute("SELECT {} FROM {} WHERE object_id = ?".format(spalte, tabelle), (objekt_id,))
    value = cursor.fetchone()[0]
    return value


def sidebar(object_id, titel, ort, object_typ, baujahr, wohnflaeche, zimmer, kaufpreis, nettomieteinnahmen, eigenkapitalrendite):
    global df
    st.sidebar.write(f"Objekt-ID: {st.session_state['object_id']}")
    st.sidebar.write('https://www.immonet.de/angebot/' + object_id)
    st.sidebar.write(":red[",titel,"]")
    st.sidebar.write(object_typ, " in ",ort)
    st.sidebar.write("Kaufpreis: ", kaufpreis)
    st.sidebar.write("Zimmer: ", zimmer)
    st.sidebar.write("Baujahr: ", baujahr)
    st.sidebar.write("Wohnfläche: ", wohnflaeche)
    st.sidebar.write("Nettomieteinnahmen p.a.: ", round(nettomieteinnahmen,2)) 
    st.sidebar.write("EK-Rendite: ", round(eigenkapitalrendite,2))

def update_table(id, tabellenname, spaltenname, value):
    cursor.execute(f"UPDATE {tabellenname} SET {spaltenname} = ? WHERE object_id = ?", (value, id))
    #st.write(id, value, spaltenname)
    conn.commit()
    
#####################
# Beschreibung
#####################
def beschreibung(objekt_beschreibung, ausstattung_beschreibung, umgebungsbeschreibung, sonstige_beschreibung, ausstattung, heizungsart, befeuerungsart, effizienzklasse, endenergieverbrauch, baujahr_heizung, plz, stadt, strasse, bundesland, staat):
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Objekt', 'Adresse', 'Ausstattung', 'Umgebung', 'Sonstiges', 'Energie'])
    with tab1:
        if objekt_beschreibung is not None:
            st.subheader("Objektbeschreibung")
            st.write(objekt_beschreibung)
    with tab2:
        if stadt is not None:
            st.subheader("Adresse")
            st.write(strasse)
            st.write(plz, stadt) 
            st.write(bundesland, '(',staat,')')     

        # OpenStreetMap API-URL
        url = 'https://nominatim.openstreetmap.org/search'

        # Benutzereingabe sammeln
        query = strasse,' ', plz, ' ', stadt

        # GET-Anfrage an OpenStreetMap senden
        if query:
            params = {'q': query, 'format': 'json'}
            response = requests.get(url, params=params)
            data = json.loads(response.text)
            
            # Erste Ergebnisposition auswählen
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            
            # Streamlit-Karte erstellen und Koordinaten hinzufügen
            m = folium.Map(location=[lat, lon], zoom_start=13)
            #Draw(export=True).add_to(m)
            tooltip = "Koordinaten: {}, {}".format(lat, lon)
            folium.Marker([lat, lon], tooltip=tooltip).add_to(m)
            folium_static(m)

    with tab3:
        if ausstattung_beschreibung is not None or ausstattung is not None:
            st.subheader("Ausstattung")
            if ausstattung is not None:
                st.write(ausstattung)
            if ausstattung_beschreibung is not None:
                st.write(ausstattung_beschreibung)
    with tab4:
        if umgebungsbeschreibung is not None:
            st.subheader("Umgebung")
            st.write(umgebungsbeschreibung)
    with tab5:
        if sonstige_beschreibung is not None:
            st.subheader("Sonstiges")
            st.write(sonstige_beschreibung)
    with tab6:
        if heizungsart is not None or befeuerungsart is not None or effizienzklasse is not None or endenergieverbrauch is not None or baujahr_heizung is not None:
            st.subheader("Energieverbrauch")
            st.write("Heizungsart:", heizungsart)
            st.write("Befeuerungsart:", befeuerungsart)
            st.write("Effizienzklasse:", effizienzklasse)
            st.write("Energieverbrauch:", endenergieverbrauch)
            st.write("Baujahr der Heizung:", baujahr_heizung)
    
#####################
# Basisdaten
#####################
def basisdaten(object_id, baujahr_alt, wohnflaeche_alt, ort_alt, plz_alt, strasse_alt, object_typ_alt):
    st.header("Basisdaten")

    if object_typ_alt=="Wohnung":
        index=0
    elif object_typ_alt=="Haus":
        index=1
    else:
        index=2
        
    col1, col2, col3=st.columns(3)
    with col1:
        object_typ = st.selectbox("Immobilientyp", ["Wohnung", "Haus", "Mietwohnhaus"], index=index)
        if object_typ != object_typ_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'object_typ', object_typ)
    with col2:
        baujahr = st.number_input("Baujahr", value=baujahr_alt, step=1)
        if baujahr != baujahr_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'baujahr', baujahr)
    with col3:
        erwerbsdatum = st.date_input("Erwerbsdatum")
    col1, col2=st.columns(2)
    with col1:
        anzahl_wohnungen = st.number_input(":green[Anzahl Wohnungen]", min_value=1, value=1, step=1)
    with col2:
        anzahl_pkw_stellplaetze = st.number_input(":green[Anzahl PKW Stellplätze / Garagen]", min_value=0, step=1)
    if anzahl_wohnungen > 1:
        st.warning('Achtung: Programm funktioniert noch nicht für mehr als 1 Wohnung', icon="⚠️")
    col1, col2=st.columns(2)
    with col1:
        wohnflaeche = st.number_input(":green[Gesamte Wohnfläche in m2]", value=wohnflaeche_alt, min_value=0.0, step=0.01)
        if wohnflaeche != wohnflaeche_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'qm', wohnflaeche)
    with col2:
        grundstuecksflaeche = st.number_input("Grundstücksfläche in m2", min_value=0.0, value=wohnflaeche)
            
    col1, col2, col3=st.columns(3)
    with col1:
        strasse = st.text_input("Straße", value=strasse_alt, placeholder="Straße")
        if strasse != strasse_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'strasse', strasse)
    with col2:
        plz = st.text_input("Postleitzahl", value=plz_alt, placeholder="Postleitzahl")
        if plz != plz_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'plz', plz)
    with col3:
        ort = st.text_input("Ort", value=ort_alt, placeholder="Ort")
        if ort != ort_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'stadt', ort)
        
    return anzahl_wohnungen, anzahl_pkw_stellplaetze, wohnflaeche, grundstuecksflaeche, object_typ

#####################
# Mieterliste
#####################
def mieterliste(anzahl_wohnungen, monatsmiete_pro_einheit_alt, mietspiegelmiete_pro_m2_alt, wohnflaeche_alt, zimmer_alt, baujahr):
    # Create table
    monatsmiete_gesamt = 0
    miete_pro_m2 = 0
    
    st.header("Mieterliste")

    for i in range(anzahl_wohnungen):
        st.write("Wohnung", i+1)
        col1, col2, col3 = st.columns(3)
        with col1:
            wohnung = st.text_input(f"Bezeichnung Wohnung {i+1}:", placeholder="z. B. Erdgeschoss Links")
        with col2:
            mieter = st.text_input(f"Mieter {i+1}:", placeholder="Name des Mieters")
        with col3:
            wohnflaeche_in_m2 = st.number_input(f":green[Wohnfläche in m2 {i+1}:]", value=wohnflaeche_alt)
            if wohnflaeche_in_m2 != wohnflaeche_alt:
                update_table(st.session_state['object_id'], 'immo_data', 'qm', wohnflaeche_in_m2)
            
        #st.write("Miete:",monatsmiete_pro_einheit_alt)
        col1, col2 = st.columns(2)
        with col1:
            #st.write("Monatsmiete pro Einheit: ", monatsmiete_pro_einheit_alt)
            monatsmiete_pro_einheit = st.number_input(f":green[Monatsmiete pro Einheit {i+1}:]", value=monatsmiete_pro_einheit_alt)
            if monatsmiete_pro_einheit != monatsmiete_pro_einheit_alt:
                update_table(st.session_state['object_id'], 'immo_data', 'kaltmiete', monatsmiete_pro_einheit)
        
        if wohnflaeche_in_m2 > 0 and monatsmiete_pro_einheit > 0:
            miete_pro_qm = monatsmiete_pro_einheit/wohnflaeche_in_m2
        else:
            miete_pro_qm = 0
        with col2:
            miete_pro_m2_neu = st.number_input(f":blue[Miete pro m2 {i+1}:]", value=miete_pro_qm)
            if miete_pro_m2_neu != miete_pro_m2:
                monatsmiete_pro_einheit = miete_pro_m2_neu * wohnflaeche_in_m2
                update_table(st.session_state['object_id'], 'immo_data', 'kaltmiete', monatsmiete_pro_einheit)
        monatsmiete_gesamt=monatsmiete_gesamt+monatsmiete_pro_einheit
        
        if miete_pro_m2 > 0 and mietspiegelmiete_pro_m2 is not None:
            delta_mietspiegel=round(100*(mietspiegelmiete_pro_m2/miete_pro_m2-1),2)
        else:
            delta_mietspiegel=0
            
        st.write("Siehe: https://www.miet-check.de/mietpreis-plz/"+plz)
        with col1:
            # convert the ort to lowercase
            #abfrage_ort = ort.lower()
            abfrage_ort = ort
            
            # Ermittel neue Mietspiegelmiete, da Daten geändert wurden
            if wohnflaeche_alt != wohnflaeche_in_m2 or zimmer_alt != zimmer:
                #mietspiegelmiete = ermittel_mietspiegelmiete(abfrage_ort, baujahr, wohnflaeche_alt, zimmer_alt)
                mietspiegelmiete = pages.functions.mietpreisspiegel.mietspiegelpreis(qm=wohnflaeche,zimmer=zimmer, plz=plz)
            else:
                mietspiegelmiete = mietspiegelmiete_pro_m2_alt

            mietspiegelmiete_pro_m2 = st.number_input(f"Mietspiegelmiete pro m2 {i+1}:", value=mietspiegelmiete, step=0.1)
    
    
        with col2:
            delta_mietspiegel_zur_ist_miete_in_prozent = st.number_input(f":blue[Delta Mietspiegel zur Ist-Miete in % {i+1}:]", delta_mietspiegel, disabled=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            mietbeginn = st.date_input(f"Mietbeginn {i+1}:")
        with col2:
            letzte_mieterhoehung = st.date_input(f"Letzte Mieterhöhung {i+1}:")
        #grundlage_mieterhoehung_{i+1} = st.selectbox("Immobilientyp {i+1}", ["ETW", "Mietwohnhaus"])
        with col3:
            grundlage_mieterhoehung_i = st.selectbox(f"Grundlage Mieterhöhung {i+1}", ["leer", "Mietspiegel (§ 558)", "Modernisierung (§ 559)"], help="Zum Thema Mieterhöhung gibt es ein weiteres Buch von Goldwein mit dem Titel :green[Vermietung & Mietererhöhung]. ")

    return monatsmiete_gesamt, mietspiegelmiete_pro_m2

#####################
# PKW Stellplätze
#####################
def stellplaetze(anzahl_pkw_stellplaetze):
    # Create table
    monatsmiete_stellplaetze_gesamt = 0
    st.header("PKW Stellplätze")

    col1, col2, col3 = st.columns(3)
    for i in range(anzahl_pkw_stellplaetze):
        with col1:
            stellplatz_name = st.text_input(f"Bezeichnung Stellplatz {i+1}:")
        with col2:
            mieter_stellplatz = st.text_input(f"Stellplatzmieter {i+1}:")
        with col3:
            monatsmiete_pro_stellplatz = st.number_input(f":green[Monatsmiete pro Stellplatz {i+1}:]", step=1)
        monatsmiete_stellplaetze_gesamt=monatsmiete_stellplaetze_gesamt+monatsmiete_pro_stellplatz

    return monatsmiete_stellplaetze_gesamt
#####################
# Einmalige Kosten beim Kauf
#####################
def kaufnebenkosten(kaufpreis, kaufpreis_kalk_alt, bundesland_alt, courtage_alt, notar_prozentangabe, wertgutachtenkosten_alt, renovierungskosten_alt, umbaukosten_alt):
    st.header("Einmalige Kosten beim Kauf")
    st.subheader("Kaufnebenkosten")
    st.write("Kaufpreis Kalk Alt: ", kaufpreis_kalk_alt)
    col1, col2 = st.columns(2)
    with col1:
        kaufpreis = st.number_input(":green[Kaufpreis]", value=kaufpreis, disabled=True)
#         if kaufpreis != kaufpreis_alt:
#                 update_table(st.session_state['object_id'], 'immo_data', 'preis', kaufpreis)
    with col2:
        if kaufpreis_kalk_alt == None:
            kaufpreis_kalk_alt = kaufpreis
        kaufpreis_tmp = int(round((kaufpreis * 0.9),0))
        kaufpreis_kalk = st.number_input(":green[Kalkulations-Kaufpreis] Vorschlag: "+str(kaufpreis_tmp), value=kaufpreis_kalk_alt, step=1000.0)
        if kaufpreis_kalk != kaufpreis_kalk_alt:
                update_table(st.session_state['object_id'], 'immo_data_kalk', 'preis', kaufpreis_kalk)
    
    with col1:
        bundesland = st.selectbox(":green[Grunderwerbssteuer (Prozent)]",
                                            [bundesland_alt, "Brandenburg",
                                             "Schleswig-Holstein",
                                             "Thüringen",
                                              "Saarland",
                                              "Nordrhein-Westfalen",
                                             "Berlin",
                                              "Hessen",
                                               "Mecklenburg-Vorpommern",
                                             "Hamburg",
                                             "Bayern"
                                              "Sachsen",
                                             "Sonstige Bundesländer"])
    if bundesland != bundesland_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'bundesland', bundesland)

    if bundesland  in ["Schleswig-Holstein", "Brandenburg", "Thüringen", "Saarland", "Nordrhein-Westfalen"] :
        grunderwerbssteuer_betrag = kaufpreis_kalk * 0.065
    elif bundesland in ["Berlin", "Hessen", "Mecklenburg-Vorpommern"]:
        grunderwerbssteuer_betrag = kaufpreis_kalk * 0.06
    elif bundesland == "Hamburg ":
        grunderwerbssteuer_betrag = kaufpreis_kalk * 0.055
    elif bundesland in ["Bayern", "Sachsen"]:
        grunderwerbssteuer_betrag = kaufpreis_kalk * 0.035
    else:
        grunderwerbssteuer_betrag = kaufpreis_kalk * 0.05
    with col2:
        grunderwerbssteuerkosten = st.number_input(":blue[Grunderwerbssteuer (Betrag):]", grunderwerbssteuer_betrag, disabled=True)
    with col1:
        notar_prozent = st.number_input(":green[Notar (Prozent)]", value=notar_prozentangabe, step=0.1)
    notar_betrag = kaufpreis_kalk * (notar_prozent / 100)
    with col2:
        notarkosten = st.number_input(":blue[Notar (Betrag):]", notar_betrag)
    with col1:
        maklerprovision_prozent = st.number_input(":green[Maklerprovision (Prozent)]", value=courtage_alt)
        if maklerprovision_prozent != courtage_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'courtage', maklerprovision_prozent/100)
    maklerprovision_betrag = kaufpreis_kalk * (maklerprovision_prozent / 100)
    with col2:
        maklerkosten = st.number_input(":blue[Maklerprovision (Betrag):]",maklerprovision_betrag)

    kosten_wertgutachten = st.number_input("Kosten Wertgutachten", value=wertgutachtenkosten_alt, step=100.0)
    if kosten_wertgutachten != wertgutachtenkosten_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'wertgutachtenkosten', kosten_wertgutachten)

    st.subheader("Herrichtungskosten")
    col1, col2=st.columns(2)
    with col1:
        renovierungskosten = st.number_input("Renovierungskosten", value=renovierungskosten_alt, help="Bad: 10.000€, Fenster pro qm: 400€, Fenster pro lfm: 800€ » grob 1.000€ pro Fenster, Rollladen pro lfm: 250€, Haustüre: 1.500€ » mit Einbau: 2.000€, Innentüre: 100€ » mit Einbau: 150€, Fliesen (mit Material): 70€ / qm, Parkett (mit Material): 60€ / qm, Teppich (mit Material): 30€ / qm. Laminat (mit Material): 30€ / qm. Tapezieren (mit Anstrich): 8€ / qm, Verputzen: 15€ / qm, Handwerkerstunden: 40–50 € pro Stunde von einem qualifizierten Handwerkerbetrieb", step=100.0)
        if renovierungskosten != renovierungskosten_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'renovierungskosten', renovierungskosten)
    with col2:
        umbaukosten = st.number_input("Umbaukosten", value=umbaukosten_alt, step=100.0)
        if umbaukosten != umbaukosten_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'umbaukosten', umbaukosten)

    summe_kaufnebenkosten = grunderwerbssteuerkosten + notarkosten + maklerkosten + kosten_wertgutachten
    summe_herrichtungskosten = renovierungskosten + umbaukosten
    erweiterte_anschaffungskosten = kaufpreis_kalk + summe_kaufnebenkosten + summe_herrichtungskosten

    df = pd.DataFrame([
        ["Kalkulations-Kaufpreis", kaufpreis_kalk],
        ["Summe Kaufnebenkosten", summe_kaufnebenkosten],
        ["Summe Herrichtungskosten", summe_herrichtungskosten],
        ["Erweiterte Anschaffungskosten", erweiterte_anschaffungskosten]
    ], columns=["Art", "Kosten"])

    with st.expander("Erweiterte Anschaffungskosten"):
        st.table(df)
    
    return erweiterte_anschaffungskosten

#####################
# Bewirtschaftungskosten
#####################
def bewirtschaftungskosten(anzahl_wohnungen, wohnflaeche, verwaltungskosten_alt, instandhaltungskosten_alt):
    st.header("Bewirtschaftungskosten umlagefähig")
    with st.expander("Hinweise"):
        st.info('**Umlagefähig:** :orange[Abfallentsorgung, Abwasser/Trinkwasser, Entwässerung, Hausstrom (z. B. Flurlicht), Wohngebäudeversicherung, Heizkosten (Zentralheizung), Hausreinigung, Wartungsarbeiten am Fahrstuhl, Gartenpflege, Schornsteinpfleger)]', icon="ℹ️")
        st.info('**Nicht umlagefähig:** :orange[Verwaltungskosten, Kontogebühren, Wartung, Instandhaltungsrücklagen (Reparaturen und Renovierungen im Gemeinschaftseigentum, wie z.B. die Erneuerung der Fassade oder die Neueindeckung des Daches])', icon="ℹ️")
    
    col1, col2 = st.columns(2)
    with col1:
        verwaltungskosten_pro_wohnung =  st.number_input(f":green[Verwaltungskosten pro Wohnung p. a.:]", value=verwaltungskosten_alt, step=1.0, help="Verwaltungskosten ca. 40% vom Hausgeld")
        if verwaltungskosten_pro_wohnung != verwaltungskosten_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'verwaltungskosten_pro_jahr', verwaltungskosten_pro_wohnung)
    with col2:
        gesamtverwaltungskosten  =  st.number_input(f":blue[Gesamtverwaltungskosten p. a.:]", value=anzahl_wohnungen * verwaltungskosten_pro_wohnung, step=1.0, disabled=False)
        if gesamtverwaltungskosten/anzahl_wohnungen !=  verwaltungskosten_pro_wohnung:
            update_table(st.session_state['object_id'], 'immo_data', 'verwaltungskosten_pro_jahr', gesamtverwaltungskosten / anzahl_wohnungen)
    with col1:
        instandhaltungskosten = st.number_input(f":green[Instandhaltungskosten pro qm p. a.:]", value=instandhaltungskosten_alt, step=1.0, help="Instandhaltungskosten ca. 60% vom Hausgeld")
        if instandhaltungskosten != instandhaltungskosten_alt:
            update_table(st.session_state['object_id'], 'immo_data', 'instandhaltungskosten_pro_jahr_qm', instandhaltungskosten)
    with col2:
        gesamtinstandhaltungskosten = st.number_input(f":blue[Gesamtinstandhaltungskosten p. a.:]", disabled=False, value= instandhaltungskosten*wohnflaeche)
        if gesamtinstandhaltungskosten/wohnflaeche !=  instandhaltungskosten:
            update_table(st.session_state['object_id'], 'immo_data', 'instandhaltungskosten_pro_jahr_qm', gesamtinstandhaltungskosten/wohnflaeche)
            
    bewirtschaftungskosten_pro_jahr = round((gesamtverwaltungskosten+gesamtinstandhaltungskosten),2)
    st.write('Bewirtschaftungskosten p. a.', bewirtschaftungskosten_pro_jahr)
    return bewirtschaftungskosten_pro_jahr

#####################
# Einnahmen
#####################
def einnahmen(monatsmiete_wohnungen_gesamt, monatsmiete_stellplätze_gesamt, bewirtschaftungskosten_pro_jahr, mietspiegelmiete_pro_m2, wohnflaeche):
    st.header("Einnahmen")
    
    if monatsmiete_wohnungen_gesamt > 0:
        miete = monatsmiete_wohnungen_gesamt
    else:
        miete = mietspiegelmiete_pro_m2 * wohnflaeche
    col1, col2 = st.columns(2)
    with col1:
        monatsmiete_wohnungen_gesamt =  st.number_input(f":blue[Nettomieteinnahmen Wohnungen:]", miete, disabled=True)
    with col2:
        if monatsmiete_stellplätze_gesamt > 0:
            monatsmiete_stellplaetze_gesamt =  st.number_input(f":blue[Nettomieteinnahmen Stellplätze:]", monatsmiete_stellplätze_gesamt, disabled=True)
    monatsmiete_gesamt = monatsmiete_wohnungen_gesamt + monatsmiete_stellplätze_gesamt
    with col1:
        nettomieteinnahmen = st.number_input(f":blue[Gesamte Nettomieteinnahmen:]", monatsmiete_gesamt, disabled=True)
    with col2:
        nettomieteinnahmen_jahr = st.number_input(f":blue[Gesamte Nettomieteinnahmen Jahr:]", monatsmiete_gesamt * 12, disabled=True)
    nettomieteinnahmen_nach_bewirtschaftungskosten = st.number_input(f":blue[Nettomieteinnahmen nach Bewirtschaftungskosten:]", nettomieteinnahmen_jahr - bewirtschaftungskosten_pro_jahr, disabled=True)
    
    return(nettomieteinnahmen_nach_bewirtschaftungskosten)

#####################
# Steuern
#####################
def steuern(grundstuecksflaeche, erweiterte_anschaffungskosten):
    st.header("Steuern")
    col1, col2 = st.columns(2)
    with col1:
        bodenrichtwert_pro_qm =  st.number_input(f"Bodenrichtwert pro qm:", step=1, help="Zum Thema Steuern gibt es ein weiteres Buch von Goldwein mit dem Titel :green[Steuerleitfaden für Immobilieninvestoren: Der ultimative Steuerratgeber] ")
    with col2:
        anteiliger_bodenwert  =  st.number_input(f":blue[Anteiliger Bodenwert:]", disabled=True, help="Wichtiger Hinweis! Bei einer Investition in eine einzelne Eigentumswohnung müssen Sie in Feld I 16 den Bodenwert mit dem Miteigentumsanteil der Eigentumswohnung am Gemeinschaftseigentum multiplizieren. Es wird dazu auf die Ausführungen in Abschnitt IV. 5. d) des Buches verwiesen.", value=bodenrichtwert_pro_qm*grundstuecksflaeche)
    anteil_anschaffungskosten =  st.number_input(f":blue[Anteil Anschaffungskosten Gebäude (AfA-Basis):]", disabled=True, value=erweiterte_anschaffungskosten-anteiliger_bodenwert, help="Erweiterte Anschaffungskosten abzüglich anteiliger Bodenwert")

#####################
# Renditeberechnungen
#####################
def anuitaeten_rechner(erweiterte_anschaffungskosten, nettomieteinnahmen_nach_bewirtschaftungskosten, eigenkapital_alt, laufzeit_alt, zinssatz_alt):
    st.subheader("Annuitätenrechner Kredit")
    
    col1, col2 = st.columns(2)
    with col1:
        erweiterte_anschaffungskosten =  st.number_input(f":blue[Erweiterte Anschaffungskosten: ]", disabled=True, value=erweiterte_anschaffungskosten)
    with col2:
        st.number_input(f":blue[Jährliche Nettomieteinnahmen:] ", disabled=True, value=nettomieteinnahmen_nach_bewirtschaftungskosten)
    with col1:
        if eigenkapital_alt > erweiterte_anschaffungskosten:
            eigenkapital_alt = erweiterte_anschaffungskosten
        #eigenkapital = st.slider("Eigenkapital", 0.0, erweiterte_anschaffungskosten, float(eigenkapital_alt))
        eigenkapital =  st.number_input(f":green[Eigenkapital: ]", value=eigenkapital_alt, min_value=0.0, max_value=erweiterte_anschaffungskosten, disabled=False, step=10000.0)
        if eigenkapital != eigenkapital_alt:
                update_table(st.session_state['object_id'], 'immo_data', 'eigenkapital', eigenkapital)
    with col2:
        kredit =  st.number_input(f":blue[Kredit:] ", disabled=True, value=erweiterte_anschaffungskosten-eigenkapital)
    with col1:
        zinssatz_nominal =  st.number_input(f":green[Zinssatz:] ", disabled=False, min_value=0.0, value=zinssatz_alt, step=0.1)
        #zinssatz_nominal = st.slider("Zinssatz", min_value=0.0, max_value=10.0, value=zinssatz_alt)
    with col2:
        #Laufzeit =  st.number_input(f":green[Laufzeit:]", disabled=False, min_value=1, value=laufzeit_alt, step=1)
        Laufzeit = st.slider("Laufzeit", min_value=1, max_value=30, value=laufzeit_alt)
    
    Zinssatz = zinssatz_nominal / 100
    monatliche_nettomieteinahmen = nettomieteinnahmen_nach_bewirtschaftungskosten / 12
    Fremdkapital = erweiterte_anschaffungskosten - eigenkapital  # Fremdkapital (Kredit)
    data=[]
    
    # Monatliche Kreditrate berechnen
    if Laufzeit > 0 and Zinssatz > 0:
        Kreditrate = Fremdkapital * (Zinssatz / 12) / (1 - (1 + Zinssatz / 12) ** (-Laufzeit * 12))

        # Berechnungen für jeden Monat
        jahrliche_eigenkapitalrendite = 0
        gesamte_eigenkapitalrendite = 0
        gesamte_tilgung = 0
        gesamte_zinsen = 0
        gesamte_kreditrate = 0

        for Monat in range(1, Laufzeit * 12 + 1):
            Zinsen = Fremdkapital * Zinssatz / 12
            Tilgung = Kreditrate - Zinsen
            Fremdkapital = Fremdkapital - Tilgung
            
            #Eigenkapitalrendite = (Mieteinnahmen - Zinsen) / (Fremdkapital + 20000)
            if eigenkapital > 0:
                Eigenkapitalrendite = (monatliche_nettomieteinahmen - Zinsen) * 100 * 12/ eigenkapital
            else:
                Eigenkapitalrendite = 0
            eigenkapital += Tilgung
            
            # Durchschnittliche jährliche Eigenkapitalrendite berechnen
            if Monat % 12 == 0:
                jahrliche_eigenkapitalrendite = jahrliche_eigenkapitalrendite + Eigenkapitalrendite
                #print("Durchschnittliche jährliche Eigenkapitalrendite für Jahr", int(Monat / 12), ":", jahrliche_eigenkapitalrendite / 12)
                jahrliche_eigenkapitalrendite = 0
            
            # Gesamte Eigenkapitalrendite berechnen
            gesamte_eigenkapitalrendite = gesamte_eigenkapitalrendite + Eigenkapitalrendite
            gesamte_tilgung = gesamte_tilgung + Tilgung
            gesamte_zinsen += Zinsen
            gesamte_kreditrate +=Kreditrate
            data.append([Monat, Tilgung, Zinsen, Kreditrate, Eigenkapitalrendite, eigenkapital, monatliche_nettomieteinahmen - Zinsen])

        df = pd.DataFrame(data, columns=['Monat', 'Tilgung', 'Zinsen', 'Kreditrate', 'Eigenkapitalrendite', 'Eigenkapital', 'Monatlicher Gewinn'])

        with st.expander("Zeige Annuitätenplan an"):
            st.write(df)

            # Gesamte Eigenkapitalrendite ausgeben
        eigenkapitalrendite_neu = gesamte_eigenkapitalrendite / (Laufzeit * 12)
        st.write("Gesamte Tilgung: ", round(gesamte_tilgung,2))
        st.write("\+ Gesamte Zinsen: ", round(gesamte_zinsen,2))
        st.write("= Gesamte Kreditrate: ", round(gesamte_kreditrate,2))
        st.write("\+ Zu Beginn eingebrachtes EK: ", round(eigenkapital_alt,2))
        st.write("= Gesamte Kosten (EK + Kreditrate): ", round((gesamte_kreditrate + eigenkapital_alt),2))
        st.write("Gesamte Eigenkapitalrendite:", round(eigenkapitalrendite_neu,2))
        return eigenkapitalrendite_neu

#st.write('Objekt-ID ', {st.session_state['object_id']})
#object_id = {st.session_state['object_id']}
if 'object_id' not in st.session_state:
    st.session_state['object_id'] = 'leer'
#st.write('Objekt-ID ', {st.session_state['object_id']})
# Parameter
NOTAR_PROZENTANGABE = 2.0
LAUFZEIT = 10
ZINSSATZ = 3.5

#object_id = ''
plz = ''
ort = ''
strasse = ''
bundesland = 'Schleswig-Holstein'
object_typ = ''
object_art = ''
baujahr = 0
wohnflaeche = 0.001
monatsmiete_pro_einheit = 0.0
zimmer = 0.0
kaufpreis = 0.0
courtage = 0.0
wertgutachtenkosten = 0.0
renovierungskosten = 0.0
umbaukosten = 0.0
verwaltungskosten = 0.0
instandhaltungskosten = 0.0
mietspiegelmiete_pro_m2 = 0.0
eigenkapitalrendite = 0.0
eigenkapital = 0.0


# Verbindung zur Datenbank herstellen
dbname = 'immo.db'
conn = sqlite3.connect(dbname)
cursor = conn.cursor()

df = tabellendaten()

if st.button("Leeres Objekt anlegen"):
    # Erstelle eine Liste aller vorhandenen Objekt-IDs
    existing_ids = df['object_id'].tolist()
    # Erstelle einen Vorgabewert, der nicht in der Liste vorhanden ist
    i = 1
    while True:
        new_object_default = 'M' + str(i)
        if new_object_default not in existing_ids:
            break
        i += 1
    object_id = new_object_default
    st.session_state['object_id'] = new_object_default
    st.write("Leeres Objekt: ", object_id, " wurde angelegt!")
    cursor.execute(f"INSERT INTO immo_data (object_id, stadt, plz, baujahr, preis, courtage, kaltmiete) VALUES (?, ?, ?, ?, ?, ?, ?)", (object_id,'Neuer Ort', '00000',0,0.0,0,0))
    conn.commit()
    df = tabellendaten()

# Abfrage der Transaktionsart
cursor.execute("SELECT DISTINCT transaktionsart FROM immo_data")
transaktionsart_data = cursor.fetchall()
transaktionsart_list = [x[0] for x in transaktionsart_data]

# Abfrage Objekttyp
cursor.execute("SELECT DISTINCT object_typ FROM immo_data")
object_typ_data = cursor.fetchall()
object_typ_list = [x[0] for x in object_typ_data]


# Erstelle einen Text-Eingabebereich
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    transaktionsart_search_term = st.selectbox('Transaktionsart', ['Alle'] + transaktionsart_list)
with col2:
    object_typ_search_term = st.selectbox('Objekttyp', ['Alle'] + object_typ_list)
with col3:
    plz_search_term = st.text_input('PLZ')
with col4:
    city_search_term = st.text_input('Ort')
with col5:
    object_search_term = st.text_input('Objektbeschreibung', placeholder='z. B. Erbpacht')
    
if transaktionsart_search_term == 'Alle' and object_typ_search_term == 'Alle':
    filtered_df = df[(df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))& (df['Objektbeschreibung'].str.contains(object_search_term, case=False))]
elif transaktionsart_search_term != 'Alle' and object_typ_search_term == 'Alle':
    filtered_df = df[((df['Transaktionsart'].str.contains(transaktionsart_search_term)) & df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))& (df['Objektbeschreibung'].str.contains(object_search_term, case=False))]
elif transaktionsart_search_term == 'Alle' and object_typ_search_term != 'Alle':
    filtered_df = df[(df['Objekt-Typ'].str.contains(object_typ_search_term)) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False)) & (df['Objektbeschreibung'].str.contains(object_search_term, case=False))]
else:
    filtered_df = df[((df['Transaktionsart'].str.contains(transaktionsart_search_term)) & (df['Objekt-Typ'].str.contains(object_typ_search_term)) & df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))& (df['Objektbeschreibung'].str.contains(object_search_term, case=False))]
#filtered_df = df
    



# Zeige die gefilterte Datenbank an
selected_object = st.dataframe(filtered_df, width=800)
#col1, col2 = st.columns(2)
#with col1:
object_id = st.session_state['object_id']

st.write("Objekt: ", object_id)
selected_object = st.selectbox('Wähle ein Objekt aus', filtered_df['Objekt-ID'])
if selected_object is not None:
    selected_object_data = filtered_df[filtered_df['Objekt-ID'] == selected_object]
    st.session_state['object_id'] = selected_object_data['Objekt-ID'].values[0]
    plz = selected_object_data['PLZ'].values[0]
    ort = selected_object_data['Ort'].values[0]
    strasse = selected_object_data['Strasse'].values[0]
    bundesland = selected_object_data['Bundesland'].values[0]
    staat = selected_object_data['Staat'].values[0]
    object_typ = selected_object_data['Objekt-Typ'].values[0]
    object_art = selected_object_data['Objekt-Art'].values[0]
    baujahr = int(selected_object_data['Baujahr'].values[0])
    wohnflaeche = selected_object_data['qm'].values[0]
    monatsmiete_pro_einheit = selected_object_data['Kaltmiete'].values[0]
    zimmer = selected_object_data['Zimmer'].values[0]
    kaufpreis = selected_object_data['Preis'].values[0]
    kaufpreis_kalk = lies_von_db('immo_data_kalk', 'preis', str(object_id))

    courtage = selected_object_data['Courtage'].values[0]
    wertgutachtenkosten = float(selected_object_data['Wertgutachtenkosten'].values[0])
    renovierungskosten = float(selected_object_data['Renovierungskosten'].values[0])
    umbaukosten = float(selected_object_data['Umbaukosten'].values[0])
    verwaltungskosten = float(selected_object_data['Verwaltungskosten'].values[0])
    instandhaltungskosten = float(selected_object_data['Instandhaltungskosten'].values[0])
    mietspiegelmiete_pro_m2 = float(selected_object_data['Mietspiegelmiete je qm'].values[0])
    eigenkapitalrendite = selected_object_data['Eigenkapitalrendite'].values[0]
    eigenkapital = selected_object_data['Eigenkapital'].values[0]
    titel  = selected_object_data['Titel'].values[0]
    objekt_beschreibung = selected_object_data['Objektbeschreibung'].values[0]
    ausstattung_beschreibung = selected_object_data['Ausstattungsbeschreibung'].values[0]
    umgebungsbeschreibung = selected_object_data['Umgebung'].values[0]
    sonstige_beschreibung = selected_object_data['Sonstiges'].values[0]
    ausstattung = selected_object_data['Ausstattung'].values[0]
    heizungsart = selected_object_data['Heizungsart'].values[0]
    befeuerungsart = selected_object_data['Befeuerungsart'].values[0]
    effizienzklasse = selected_object_data['Effizienzklasse'].values[0]
    endenergieverbrauch = selected_object_data['Endenergieverbrauch'].values[0]
    baujahr_heizung = selected_object_data['Baujahr Heizung'].values[0]

if monatsmiete_pro_einheit is None or monatsmiete_pro_einheit == "":
    monatsmiete_pro_einheit = 0.0
else:
    try:
        monatsmiete_pro_einheit = float(monatsmiete_pro_einheit)
    except ValueError:
        monatsmiete_pro_einheit = 0.0

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(['Basis', 'Mieter', 'Kaufnebenkosten', 'Bewirtschaftungskosten', 'Einnahmen', 'Steuern', 'Annuitäten', 'Beschreibung'])
if st.session_state['object_id'] !='leer':
    with tab1:    
        anzahl_wohnungen, anzahl_pkw_stellplaetze, wohnflaeche, grundstuecksflaeche, object_typ=basisdaten(st.session_state['object_id'], baujahr, wohnflaeche, ort, plz, strasse, object_typ)
    with tab2:
        monatsmiete_wohnungen_gesamt, mietspiegelmiete_pro_m2=mieterliste(anzahl_wohnungen, monatsmiete_pro_einheit, mietspiegelmiete_pro_m2, wohnflaeche, zimmer, baujahr)
        if anzahl_pkw_stellplaetze > 0:
            monatsmiete_stellplätze_gesamt=stellplaetze(anzahl_pkw_stellplaetze)
        else:
            monatsmiete_stellplätze_gesamt = 0
    with tab3:        
        erweiterte_anschaffungskosten=kaufnebenkosten(kaufpreis, kaufpreis_kalk, bundesland, courtage, NOTAR_PROZENTANGABE, wertgutachtenkosten, renovierungskosten, umbaukosten)
    with tab4:
        bewirtschaftungskosten_pro_jahr=bewirtschaftungskosten(anzahl_wohnungen, wohnflaeche, verwaltungskosten, instandhaltungskosten)
    with tab5:
        nettomieteinnahmen_nach_bewirtschaftungskosten=einnahmen(monatsmiete_wohnungen_gesamt, monatsmiete_stellplätze_gesamt, bewirtschaftungskosten_pro_jahr, mietspiegelmiete_pro_m2, wohnflaeche)
    with tab6:
        steuern(grundstuecksflaeche, erweiterte_anschaffungskosten)
    with tab7:
        eigenkapitalrendite = anuitaeten_rechner(erweiterte_anschaffungskosten, nettomieteinnahmen_nach_bewirtschaftungskosten, eigenkapital, LAUFZEIT, ZINSSATZ)
    with tab8:
        beschreibung(objekt_beschreibung, ausstattung_beschreibung, umgebungsbeschreibung, sonstige_beschreibung, ausstattung, heizungsart, befeuerungsart, effizienzklasse, endenergieverbrauch, baujahr_heizung, plz, ort, strasse, bundesland, staat)
    sidebar(object_id, titel, ort, object_typ, baujahr, wohnflaeche, zimmer, kaufpreis, nettomieteinnahmen_nach_bewirtschaftungskosten, eigenkapitalrendite)

conn.close()