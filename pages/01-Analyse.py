import streamlit as st
import sqlite3
import pandas as pd
import pages.functions.mietpreisspiegel
import numpy as np
from streamlit_folium import folium_static
import folium
import requests
import json
import time
import datetime

st.set_page_config(page_title="Immobilienbewertung", page_icon=":house_with_garden:")

def datei_upload(aktenzeichen, spalte, datei):

    try:
        bytes_data = datei.read()
        dateiname = datei.name
        
        # Überprüfen, ob die Datei ein PDF ist (optional)
        if not dateiname.lower().endswith('.pdf'):
            st.error("Es werden nur PDF-Dokumente akzeptiert.")
        else:              
            update_table(aktenzeichen, 'dokumente', spalte, bytes_data)
            conn.commit()
            st.success(f"Die Datei '{dateiname}' wurde erfolgreich hochgeladen.")
    except Exception as e:
        st.error("Beim Hochladen der Datei ist ein Fehler aufgetreten.")
        st.error(str(e))

def sidebar(aktenzeichen, eigenkapitalrendite_aus_vermietung, rendite_aus_immobilienhandel, erweiterte_anschaffungskosten):
    titel = read_value(aktenzeichen, 'basisdaten', 'titel')
    verkehrswert = read_value(aktenzeichen, 'schaetzwerte', 'verkehrswert')
    max_gebotspreis = read_value(aktenzeichen, 'kaufkosten', 'max_gebotspreis')
    #marktwert_nach_aufwertung = read_value(aktenzeichen, 'renditen', 'marktwert_nach_aufwertung')
    if max_gebotspreis == None:
        max_gebotspreis = 0.0
    
#     if marktwert_nach_aufwertung == None:
#         marktwert_nach_aufwertung = 0.0
    st.sidebar.write("Aktenzeichen: ", aktenzeichen)
    st.sidebar.write(":green[",titel,"]")
    st.sidebar.write("Verkehrswert laut Gutachten: ", verkehrswert)
    st.sidebar.write("Max. Gebotspreis: ", max_gebotspreis)
    st.sidebar.write("Erweiterte Anschaffungskosten: ", round(erweiterte_anschaffungskosten,2))
    #st.sidebar.write("Marktwert nach aufwertung: ", round(marktwert_nach_aufwertung,2))
    st.sidebar.write("EK-Rendite aus Vermietung: ", round(eigenkapitalrendite_aus_vermietung,2))
    st.sidebar.write("Rendite aus Immobilienverkauf: ", round(rendite_aus_immobilienhandel,2))
    st.sidebar.write("Gesamtrendite: ", round(eigenkapitalrendite_aus_vermietung + rendite_aus_immobilienhandel,2))
    
def update_table(aktenzeichen, tabellenname, spaltenname, value):
    cursor.execute(f"SELECT COUNT(*) FROM {tabellenname} WHERE aktenzeichen = ?", (aktenzeichen,))
    result = cursor.fetchone()[0]
    
    if result > 0:
        cursor.execute(f"UPDATE {tabellenname} SET {spaltenname} = ? WHERE aktenzeichen = ?", (value, aktenzeichen))
    else:
        cursor.execute(f"INSERT INTO {tabellenname} (aktenzeichen, {spaltenname}) VALUES (?, ?)", (aktenzeichen, value))   
    conn.commit()

def read_value(aktenzeichen, tabellenname, spaltenname):
    cursor.execute("SELECT {} FROM {} WHERE aktenzeichen = ?".format(spaltenname, tabellenname), (aktenzeichen,))
    result = cursor.fetchone()
    if result is not None:
        value = result[0]
        return value
    else:
        return None

def objekt():
    #st.header("Objekt auswählen, anlegen oder löschen")
    tab1, tab2, tab3 = st.tabs(['Objekt auswählen', 'Objekt anlegen', 'Objekt löschen'])
    
    with tab1:
        aktenzeichen = objekt_auswählen()
    
    with tab2:
        objekt_anlegen()
    
    return aktenzeichen
    
def objekt_auswählen():       
    cursor.execute("SELECT aktenzeichen, amtsgericht, versteigerungsdatum, titel, strasse, plz, ort, bundesland, objekt_art, baujahr, qm_wohnung, qm_grundstueck, anzahl_zimmer FROM basisdaten ORDER BY versteigerungsdatum ASC")
    data = cursor.fetchall()

    col_names=['Aktenzeichen', 'Amtsgericht', 'Versteigerungsdatum', 'Titel', 'Strasse', 'PLZ', 'Ort', 'Bundesland', 'Objekt-Art', 'Baujahr', 'QM Wohnung', 'QM Grundstück', ' Anzahl Zimmer']

    df = pd.DataFrame(data, columns=col_names)

    # Erstelle den Filter
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Abfrage Objekttyp
        cursor.execute("SELECT DISTINCT objekt_art FROM basisdaten")
        object_art_data = cursor.fetchall()
        object_art_list = [x[0] for x in object_art_data]
        object_art_search_term = st.selectbox('Objektart', ['Alle'] + object_art_list)
    with col2:
        plz_search_term = st.text_input('PLZ')
    with col3:
        city_search_term = st.text_input('Ort')
    with col4:
        date_option = st.selectbox('Versteigerungsdatum', ['Zukünftige', 'Vergangene', 'Alle'])
        
#     if object_art_search_term == 'Alle':
#         filtered_df = df[(df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]    
#     elif object_art_search_term != 'Alle':
#         filtered_df = df[(df['Objekt-Art'].str.contains(object_art_search_term)) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
#     else:
#         filtered_df = df[((df['Objekt-Art'].str.contains(object_art_search_term)) & df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
        
    if object_art_search_term == 'Alle' and date_option == 'Alle':
        filtered_df = df[(df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
    elif object_art_search_term != 'Alle' and date_option == 'Alle':
        filtered_df = df[(df['Objekt-Art'].str.contains(object_art_search_term)) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
    elif object_art_search_term == 'Alle' and date_option == 'Zukünftige':
        today = datetime.date.today()
        df['Versteigerungsdatum'] = pd.to_datetime(df['Versteigerungsdatum']).dt.date
        filtered_df = df[(df['Versteigerungsdatum'] > today) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
    elif object_art_search_term == 'Alle' and date_option == 'Vergangene':
        today = datetime.date.today()
        df['Versteigerungsdatum'] = pd.to_datetime(df['Versteigerungsdatum']).dt.date
        filtered_df = df[(df['Versteigerungsdatum'] < today) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
    elif object_art_search_term != 'Alle' and date_option == 'Zukünftige':
        today = datetime.date.today()
        df['Versteigerungsdatum'] = pd.to_datetime(df['Versteigerungsdatum']).dt.date
        filtered_df = df[(df['Objekt-Art'].str.contains(object_art_search_term)) & (df['Versteigerungsdatum'] > today) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
    elif object_art_search_term != 'Alle' and date_option == 'Vergangene':
        today = datetime.date.today()
        df['Versteigerungsdatum'] = pd.to_datetime(df['Versteigerungsdatum']).dt.date
        filtered_df = df[(df['Objekt-Art'].str.contains(object_art_search_term)) & (df['Versteigerungsdatum'] < today) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
    else:
        today = datetime.date.today()
        df['Versteigerungsdatum'] = pd.to_datetime(df['Versteigerungsdatum']).dt.date
        filtered_df = df[((df['Objekt-Art'].str.contains(object_art_search_term)) & (df['Versteigerungsdatum'] > today)) & (df['Ort'].str.contains(city_search_term, case=False)) & (df['PLZ'].str.contains(plz_search_term, case=False))]
        
    # Zeige die gefilterte Datenbank an
    selected_object = st.dataframe(filtered_df, width=1200)
    selected_object = st.selectbox('Wähle ein Objekt aus', filtered_df['Aktenzeichen'])
    
    aktenzeichen = None  # Standardwert für aktenzeichen
    
    if selected_object is not None:
        selected_object_data = filtered_df[filtered_df['Aktenzeichen'] == selected_object]
        aktenzeichen = selected_object_data['Aktenzeichen'].values[0]
      
    return aktenzeichen
            
def objekt_anlegen():
    aktenzeichen = None
    amtsgericht = None
    titel = None
    verkehrswert = None
    objekt_art = None
    strasse = None
    plz = None
    ort = None
    bundesland = None
    url = None
    
    col1, col2, col3 = st.columns(3)
    with col1:
        aktenzeichen = st.text_input("Aktenzeichen", placeholder="Aktenzeichen")
          
    with col2:
        versteigerungsdatum = st.date_input("Versteigerungstermin")
        
    with col3:
        cursor.execute("SELECT DISTINCT amtsgericht FROM amtsgerichte ORDER BY amtsgericht")
        amtsgericht_data = cursor.fetchall()
        amtsgericht_list = [x[0] for x in amtsgericht_data]
        amtsgericht = st.selectbox('Amtsgericht', amtsgericht_list)
           
    with col1:
        titel = st.text_input("Titel", placeholder="Titel")
        
    with col2:
        verkehrswert = st.number_input("Verkehrswert")
      
    with col3:
        objekt_art = st.text_input("Objektart")        
        
    with col1:
        strasse = st.text_input("Straße und Hausnummer des Objekts")
          
    with col2:
        plz = st.text_input("Postleitzahl")
          
    with col3:
        ort = st.text_input("Ort", placeholder="Ort")
        
    with col1:        
        # Abfrage Objekttyp
        cursor.execute("SELECT bundesland, steuersatz FROM grunderwerbssteuersaetze")
        bundeslaender = cursor.fetchall()
        bundeslaender_dict = {x[0]: x[1] for x in bundeslaender}
        bundesland = st.selectbox("Bundesland", list(bundeslaender_dict.keys()))

    with col2:
        url = st.text_input("URL", placeholder="URL")

    if st.button("Objekt anlegen!"):
        update_table(aktenzeichen, 'basisdaten', 'aktenzeichen', aktenzeichen)
        update_table(aktenzeichen, 'bewirtschaftungskosten', 'aktenzeichen', aktenzeichen)
        update_table(aktenzeichen, 'kaufkosten', 'aktenzeichen', aktenzeichen)
        update_table(aktenzeichen, 'mieteinnahmen', 'aktenzeichen', aktenzeichen)
        update_table(aktenzeichen, 'objektbeschreibung', 'aktenzeichen', aktenzeichen)
        update_table(aktenzeichen, 'renditen', 'aktenzeichen', aktenzeichen)
        update_table(aktenzeichen, 'steuern', 'aktenzeichen', aktenzeichen)
        update_table(aktenzeichen, 'basisdaten', 'versteigerungsdatum', versteigerungsdatum)
        update_table(aktenzeichen, 'basisdaten', 'amtsgericht', amtsgericht)
        update_table(aktenzeichen, 'basisdaten', 'titel', titel)
        update_table(aktenzeichen, 'schaetzwerte', 'verkehrswert', verkehrswert)
        update_table(aktenzeichen, 'basisdaten', 'objekt_art', objekt_art)
        update_table(aktenzeichen, 'basisdaten', 'strasse', strasse)
        update_table(aktenzeichen, 'basisdaten', 'plz', plz)
        update_table(aktenzeichen, 'basisdaten', 'ort', ort)
        update_table(aktenzeichen, 'basisdaten', 'bundesland', bundesland)
        update_table(aktenzeichen, 'kaufkosten', 'grunderwerbssteuer_prozent', bundeslaender_dict[bundesland])
        update_table(aktenzeichen, 'basisdaten', 'url', url)
        st.write("Daten wurden gespeichert")
        time.sleep(2)
        st.experimental_rerun()
        
def basis(aktenzeichen):
    st.write("Aktenzeichen:", aktenzeichen) 
    col1, col2, col3 = st.columns(3)
    with col1:
        aktenzeichen = st.text_input("Aktenzeichen", value = aktenzeichen, disabled = True)
        
    with col2:
        amtsgericht = read_value(aktenzeichen, 'basisdaten', 'amtsgericht')
        #amtsgericht = st.text_input("Amtsgericht", value = amtsgericht)
        cursor.execute("SELECT DISTINCT amtsgericht FROM amtsgerichte ORDER BY amtsgericht")
        amtsgericht_data = cursor.fetchall()
        amtsgericht_list = [x[0] for x in amtsgericht_data]
        amtsgericht_list.insert(0, amtsgericht)  # Hinzufügen des vorhandenen Amtsgerichts am Anfang der Liste
        amtsgericht = st.selectbox('Amtsgericht', amtsgericht_list)
    
    with col3:
        versteigerungsdatum = read_value(aktenzeichen, 'basisdaten', 'versteigerungsdatum')
        #versteigerungsdatum = st.date_input("Versteigerungsdatum", value = versteigerungsdatum)
        jahr, monat, tag = versteigerungsdatum.split("-")
        jahr = int(jahr)
        monat = int(monat)
        tag = int(tag)
        versteigerungsdatum = st.date_input("Versteigerungsdatum", datetime.date(jahr, monat, tag))
    
    with col1:
        baujahr = read_value(aktenzeichen, 'basisdaten', 'baujahr')
        if baujahr == None:
            baujahr = 0
        baujahr = st.text_input("Baujahr", value=baujahr)
    
    with col2:
        wohnflaeche = read_value(aktenzeichen, 'basisdaten', 'qm_wohnung')
        if wohnflaeche == None:
            wohnflaeche = 0.0
        wohnflaeche = st.number_input("Wohnfläche", value=wohnflaeche, step=1.0)
    
    with col3:
        grundstuecksflaeche = read_value(aktenzeichen, 'basisdaten', 'qm_grundstueck')
        if grundstuecksflaeche == None:
            grundstuecksflaeche = 0.0
        grundstuecksflaeche = st.number_input("Grundstücksfläche", value=grundstuecksflaeche, step=1.0)
     
    with col1:
        anzahl_zimmer = read_value(aktenzeichen, 'basisdaten', 'anzahl_zimmer')
        if anzahl_zimmer == None:
            anzahl_zimmer = 0.0
        anzahl_zimmer = st.text_input("Anzahl der Zimmer", value=anzahl_zimmer)
        
    with col2:
        objekt_art = read_value(aktenzeichen, 'basisdaten', 'objekt_art')
        objekt_art = st.text_input("Objektart", value=objekt_art, placeholder="Einfamilienhaus")
        
    with col3:
        # Abfrage Objekttyp       
        bundesland  = read_value(aktenzeichen, 'basisdaten', 'bundesland')
        
        # Erstelle Auswahl-Menu. Falls das Bundesland bereits in der Liste vorhanden ist, entferne es und stelle es an 1. Stelle
        cursor.execute("SELECT bundesland, steuersatz FROM grunderwerbssteuersaetze")
        bundeslaender = cursor.fetchall()
        bundeslaender_dict = {x[0]: x[1] for x in bundeslaender}
        if bundesland in bundeslaender_dict:
            steuersatz = bundeslaender_dict.pop(bundesland)
            updated_dict = {bundesland: steuersatz}
            updated_dict.update(bundeslaender_dict)
            bundeslaender_dict = updated_dict
        bundesland = st.selectbox("Bundesland:", list(bundeslaender_dict.keys()))
        
    with col1:
        strasse  = read_value(aktenzeichen, 'basisdaten', 'strasse')
        strasse = st.text_input("Straße", value=strasse)
        
    with col2:
        plz  = read_value(aktenzeichen, 'basisdaten', 'plz')
        plz = st.text_input("Postleitzahl", value=plz)
        
    with col3:
        ort  = read_value(aktenzeichen, 'basisdaten', 'ort')
        ort = st.text_input("Ort", value=ort)
        
    besteht_erbbaurecht = read_value(aktenzeichen, 'erbbaurecht', 'besteht_erbbaurecht')
    besteht_erbbaurecht = st.checkbox("Besteht ein Erbbaurecht?", value = besteht_erbbaurecht or 0.0)
    
    if besteht_erbbaurecht == 1:
        col1, col2, col3 = st.columns(3)
        with col1:            
            ablaufdatum = read_value(aktenzeichen, 'erbbaurecht', 'ablaufdatum')
            if ablaufdatum:
                jahr, monat, tag = ablaufdatum.split("-")
                jahr = int(jahr)
                monat = int(monat)
                tag = int(tag)
                ablaufdatum = st.date_input("Ablauf des Erbbaurechts", datetime.date(jahr, monat, tag))
            else:
                ablaufdatum = st.date_input("Ablauf des Erbbaurechts")

        with col2:
            erbbauzins = read_value(aktenzeichen, 'erbbaurecht', 'erbbauzins')
            erbbauzins =  st.number_input("Erbbauzins p.a.", value=erbbauzins or 0.0)
            
        with col3:
            entschaedigung_prozent = read_value(aktenzeichen, 'erbbaurecht', 'entschaedigung_prozent')
            if entschaedigung_prozent is not None:
                entschaedigung_prozent = entschaedigung_prozent * 100
            entschaedigung_prozent =  st.number_input("Entschädigung bei Zeitablauf in %", value=entschaedigung_prozent  or 0.0) / 100
        
    else:
        ablaufdatum = None
        erbbauzins = None
        entschaedigung_prozent = None
        
    url  = read_value(aktenzeichen, 'basisdaten', 'url')
    url = st.text_input("URL", value=url or '')
    if url:
        st.write(url)
    
    versteigerungsgrund = read_value(aktenzeichen, 'basisdaten', 'versteigerungsgrund')
    versteigerungsgrund = st.text_input("Versteigerungsgrund", value=versteigerungsgrund or '')
    
        
    if st.button("Daten speichern"):
        update_table(aktenzeichen, 'basisdaten', 'baujahr', baujahr)
        update_table(aktenzeichen, 'basisdaten', 'qm_wohnung', wohnflaeche)
        update_table(aktenzeichen, 'basisdaten', 'qm_grundstueck', grundstuecksflaeche)
        update_table(aktenzeichen, 'basisdaten', 'anzahl_zimmer', anzahl_zimmer)
        update_table(aktenzeichen, 'basisdaten', 'objekt_art', objekt_art)
        update_table(aktenzeichen, 'basisdaten', 'bundesland', bundesland)
        update_table(aktenzeichen, 'basisdaten', 'strasse', strasse)
        update_table(aktenzeichen, 'basisdaten', 'plz', plz)
        update_table(aktenzeichen, 'basisdaten', 'ort', ort)
        update_table(aktenzeichen, 'kaufkosten', 'grunderwerbssteuer_prozent', bundeslaender_dict[bundesland])
        update_table(aktenzeichen, 'basisdaten', 'url', url)
        update_table(aktenzeichen, 'basisdaten', 'versteigerungsgrund', versteigerungsgrund)
        update_table(aktenzeichen, 'erbbaurecht', 'besteht_erbbaurecht', besteht_erbbaurecht)
        update_table(aktenzeichen, 'erbbaurecht', 'ablaufdatum', ablaufdatum)
        update_table(aktenzeichen, 'erbbaurecht', 'erbbauzins', erbbauzins)
        update_table(aktenzeichen, 'erbbaurecht', 'entschaedigung_prozent', entschaedigung_prozent)
        st.write("Daten wurden gespeichert")
        
def erweiterte_anschaffungskosten(aktenzeichen):
    st.subheader("Anschaffungskosten")
    col1, col2 = st.columns(2)
    
    with col1:
        verkehrswert = read_value(aktenzeichen, 'schaetzwerte', 'verkehrswert')
#         if verkehrswert == None:
#             verkehrswert = 0.0
        verkehrswert = st.number_input("Verkehrswert laut Gutachten", value=verkehrswert or 0.0, step = 10000.0)
        
    with col2:
        max_gebotspreis= read_value(aktenzeichen, 'kaufkosten', 'max_gebotspreis')
#         if max_gebotspreis == None:
#             max_gebotspreis = 0.0
        max_gebotspreis = st.number_input("Max. Gebotspreis", value=max_gebotspreis or 0.0, step = 1000.0)
        
    with col1:
        bundesland = read_value(aktenzeichen, 'basisdaten', 'bundesland')
        if bundesland == None:
            bundesland = 'Hamburg'
            
        grunderwerbssteuer_prozent = read_value(aktenzeichen, 'kaufkosten', 'grunderwerbssteuer_prozent')
        if grunderwerbssteuer_prozent == None:
            grunderwerbssteuer_prozent = 0.0
        #st.write("Bundesland:", bundesland)
        grunderwerbssteuer_prozent = st.number_input("Grunderwerbssteuer Prozent ("+bundesland+")", value=grunderwerbssteuer_prozent * 100, disabled=True)
        
    with col2:
        grunderwerbssteuer_betrag = st.number_input("Grunderwerbssteuer Betrag", value=grunderwerbssteuer_prozent / 100 * max_gebotspreis, disabled=True)
        
    with col1:
        zuschlagskosten_prozent = read_value(aktenzeichen, 'kaufkosten', 'zuschlagskosten_prozent')
        if zuschlagskosten_prozent == None:
            zuschlagskosten_prozent = 0.02
        zuschlagskosten_prozent = st.number_input("Zuschlagskosten Prozent", value=zuschlagskosten_prozent * 100, help = "(Zuschlagskosten = Gerichtskosten 1,5%,  Grundbuchkosten ca. 0,5%", step=0.1)
        
    with col2:
        zuschlagskosten_betrag = st.number_input("Zuschlagskosten Betrag", value=zuschlagskosten_prozent / 100 * max_gebotspreis, disabled=True)
        
    with col1:
        zinskosten_prozent_fuer_zuschlag = st.number_input("Zinskosten für den Zuschlag in Prozent", value=4.0, help = "4% Zinsen auf das Meistgebot für die Zeit vom Zuschlag bis zum Verteilungstermin (ca. 6-8 Wochen)", step=0.1)
    
    with col2:
        # 4% Zinsen auf das Meistgebot für die Zeit vom Zuschlag bis zum Verteilungstermin (ca. 6-8 Wochen)
        # kalkuliere mit 50 Tagen
        zinsen_tage = 50
        zinskosten_betrag_fuer_zuschlag = st.number_input("Zinskosten für den Zuschlag", value=zinskosten_prozent_fuer_zuschlag * zinsen_tage * max_gebotspreis/ (100 * 365), disabled=True, help = "Kalkulation erfolgt für 50 Tage Zinsen nach Verteilungstermin")
        
    with col1:
        bankkredit = read_value(aktenzeichen, 'renditen', 'bankkredit')
        notarkosten_prozent = read_value(aktenzeichen, 'kaufkosten', 'notarkosten_prozent')
        if notarkosten_prozent == None or notarkosten_prozent == 0:
            notarkosten_prozent = 0.015 # Default-Wert
        if bankkredit == None:
            bankkredit = 0
        if bankkredit == 0: # es wird kein Kredit aufgenommen           
            notarkosten_prozent = 0.0
            maxvalue = 0.0
        else:
            maxvalue = 5.0
        
        notarkosten_prozent = st.number_input("Notarkosten Prozent", value=notarkosten_prozent * 100, min_value = 0.0, max_value = maxvalue, help = "(1,5%-2%, wenn Hypothek ins Grundbuch eingetragen wird", step=0.1)
        
    with col2:
        notarkosten_betrag = st.number_input("Notarkosten Betrag", value=notarkosten_prozent / 100 * max_gebotspreis, disabled=True)
        
    st.subheader("Aufwertungskosten")
    col1, col2 = st.columns(2)
    with col1:   
        renovierungskosten = read_value(aktenzeichen, 'kaufkosten', 'renovierungskosten')
#         if renovierungskosten == None:
#             renovierungskosten = 0.0
        renovierungskosten = st.number_input("Renovierungskosten", value=renovierungskosten or 0.0, min_value = 0.0, step=1000.0)
    
    with col2:
        umbaukosten = read_value(aktenzeichen, 'kaufkosten', 'umbaukosten')
#         if umbaukosten == None:
#             umbaukosten = 0.0
        umbaukosten = st.number_input("Umbaukosten", value=umbaukosten or 0.0, min_value = 0.0, step=1000.0)
    st.caption("Siehe Menupunkt :green[Beschreibung -> Objektbeschreibung -> Mängel, Schäden, baulicher Zustand]")
    
    st.subheader("Gesamte Kaufnebenkosten")
    erweiterte_anschaffungskosten = max_gebotspreis + grunderwerbssteuer_betrag + zuschlagskosten_betrag + round(zinskosten_betrag_fuer_zuschlag,2) + notarkosten_betrag + renovierungskosten + umbaukosten
    st.write("Die gesamten Anschaffungskosten belaufen sich auf ", erweiterte_anschaffungskosten, " Euro")
    
    if st.button("Daten speichern "):
        update_table(aktenzeichen, 'schaetzwerte', 'verkehrswert', verkehrswert)
        update_table(aktenzeichen, 'kaufkosten', 'max_gebotspreis', max_gebotspreis)
        update_table(aktenzeichen, 'kaufkosten', 'grunderwerbssteuer_prozent', grunderwerbssteuer_prozent/100)
        update_table(aktenzeichen, 'kaufkosten', 'zuschlagskosten_prozent', zuschlagskosten_prozent/100)
        update_table(aktenzeichen, 'kaufkosten', 'notarkosten_prozent', notarkosten_prozent/100)
        update_table(aktenzeichen, 'kaufkosten', 'renovierungskosten', renovierungskosten)
        update_table(aktenzeichen, 'kaufkosten', 'umbaukosten', umbaukosten)
        st.write("Daten wurden gespeichert")
        
    return erweiterte_anschaffungskosten
        
def mietgewinn(aktenzeichen):
    tab1, tab2, tab3 = st.tabs(['Mieteinnahmen', 'Bewirtschaftungskosten', 'Nettomieteinnahmen'])
    
    with tab1:
        st.subheader("Mieteinnahmen")
        qm_wohnung = read_value(aktenzeichen, 'basisdaten', 'qm_wohnung')
        qm_wohnung = st.number_input("Wohnfläche", value=qm_wohnung or 0.0, disabled = True)
        
        marktuebliche_monatsmiete = read_value(aktenzeichen, 'schaetzwerte', 'marktuebliche_monatsmiete')
        if marktuebliche_monatsmiete:
            st.write("Marktübliche Monatsmiete laut Ertragswertrechnung aus Gutachten", marktuebliche_monatsmiete)
        immoscout_miete = read_value(aktenzeichen, 'schaetzwerte', 'immoscout_miete')
        if immoscout_miete:
            st.write("Geschätzte Monatsmiete laut Immobilienscout24", immoscout_miete)
        col1, col2=st.columns(2)         
        
        with col1:
            kaltmiete = read_value(aktenzeichen, 'mieteinnahmen', 'kaltmiete_gesamt')
            kaltmiete = st.number_input("Monatliche Kaltmiete", value=kaltmiete or 0.0, min_value = 0.0, step=100.0, help="In Hamburg dürfen nach der sogenannten „Mietpreisbremse“ bei Neuvermietungen nur Mieten verlangt werden, die maximal 10 Prozent oberhalb der ortsüblichen Vergleichsmiete liegen.")
            
        with col2:
            if qm_wohnung > 0:
                miete_pro_qm = kaltmiete/qm_wohnung
            else:
                miete_pro_qm = 0.0
            miete_pro_qm = st.number_input("Miete je m²", value=miete_pro_qm, disabled=True)
#             kaltmiete = miete_pro_qm * qm_wohnung
#             update_table(aktenzeichen, 'mieteinnahmen', 'kaltmiete_gesamt', kaltmiete)

        if st.button("Mietspiegelmiete ermitteln", help="Siehe: https://www.miet-check.de/mietpreis-plz/23562"):
            anzahl_zimmer = read_value(aktenzeichen, 'basisdaten', 'anzahl_zimmer')
            plz = read_value(aktenzeichen, 'basisdaten', 'plz')
            mietspiegelmiete_pro_qm = pages.functions.mietpreisspiegel.mietspiegelpreis(qm=qm_wohnung,zimmer=anzahl_zimmer, plz=plz)
            update_table(aktenzeichen, 'mieteinnahmen', 'mietspiegelmiete_pro_qm', mietspiegelmiete_pro_qm)
            
        col1, col2 = st.columns(2)
        
        with col1:
            mietspiegelmiete_pro_qm = read_value(aktenzeichen, 'mieteinnahmen', 'mietspiegelmiete_pro_qm')
#             if mietspiegelmiete_pro_qm == None:
#                 anzahl_zimmer = read_value(aktenzeichen, 'basisdaten', 'anzahl_zimmer')
#                 plz = read_value(aktenzeichen, 'basisdaten', 'plz')
                
            mietspiegelmiete_pro_qm = st.number_input("Mietspiegelmiete pro m²", value=mietspiegelmiete_pro_qm or 0.0, min_value = 0.0, step=1.0, help="Siehe: https://www.miet-check.de/mietpreis-plz/23562")
            
        with col2:
            mietspiegelmiete = st.number_input("Mietspiegelmiete Wohnung", value=mietspiegelmiete_pro_qm * qm_wohnung, disabled=True)
            
        if st.button(" Daten speichern "):
            update_table(aktenzeichen, 'mieteinnahmen', 'kaltmiete_gesamt', kaltmiete)
            update_table(aktenzeichen, 'mieteinnahmen', 'mietspiegelmiete_pro_qm', mietspiegelmiete_pro_qm)
            st.write("Daten wurden gespeichert")
        
    with tab2:
        st.subheader("Bewirtschaftungskosten (nicht umlagefähig)")

        with st.expander("Hinweise"):
            st.info('**Umlagefähig:** :orange[Abfallentsorgung, Abwasser/Trinkwasser, Entwässerung, Hausstrom (z. B. Flurlicht), Wohngebäudeversicherung, Heizkosten (Zentralheizung), Hausreinigung, Wartungsarbeiten am Fahrstuhl, Gartenpflege, Schornsteinpfleger)]', icon="ℹ️")
            st.info('**Nicht umlagefähig:** :orange[Verwaltungskosten, Kontogebühren, Wartung, Instandhaltungsrücklagen (Reparaturen und Renovierungen im Gemeinschaftseigentum, wie z.B. die Erneuerung der Fassade oder die Neueindeckung des Daches])', icon="ℹ️")
            st.info("**Durchschnittliche Bewirtschaftungskosten:** :orange[ca. 18%]", icon="ℹ️")
        col1, col2 = st.columns(2)
        with col1:
            erbbauzins = read_value(aktenzeichen, 'erbbaurecht', 'erbbauzins')
            erbbauzins =  st.number_input("Erbbauzins p.a.:", value=erbbauzins or 0.0, disabled = True)
        
        with col2:
            hausgeld = read_value(aktenzeichen, 'bewirtschaftungskosten', 'hausgeld')
            hausgeld =  st.number_input("Hausgeld pro Monat", value=hausgeld or 0.0, step=1.0, help="Angabe dient hier als Kalkulationsgrundlage für Verwaltungs- und Instandhaltungskosten. Nicht umlagefähig sind ca. 40%")
        
        with col1:
            qm_wohnung = st.number_input("Wohnfläche:", value=qm_wohnung, disabled = True)
        with col2:
            verwaltungskosten_pro_wohnung = read_value(aktenzeichen, 'bewirtschaftungskosten', 'verwaltungskosten_pro_wohnung')
            verwaltungskosten_pro_wohnung =  st.number_input(f":green[Verwaltungskosten pro Wohnung p. a.:]", value=verwaltungskosten_pro_wohnung or 0.0, step=1.0, help="Aus den Wertermittlungsrichtlinien ergibt sich für die Verwaltungskosten eine Spanne von 3 bis 5 Prozent des Rohertrages.")
            
        with col1:
            instandhaltungskosten_pro_qm = read_value(aktenzeichen, 'bewirtschaftungskosten', 'instandhaltungskosten_pro_qm')
            instandhaltungskosten_pro_qm =  st.number_input(f":green[Instandhaltungskosten pro qm p. a.:]", value=instandhaltungskosten_pro_qm or 0.0, step=1.0)

        with col2:
            instandhaltungskosten_gesamt =  st.number_input("Instandhaltungskosten pro Jahr", value=instandhaltungskosten_pro_qm * qm_wohnung, disabled = True)
        
        with col1:
            st.write("Nicht umlagefähige Kosten (Verwaltungs- und Instandhaltungskosten) pro Monat:")
        with col2:
            st.write(round((instandhaltungskosten_gesamt+verwaltungskosten_pro_wohnung)/12,2))
            
        with st.expander("Hinweise"):
            st.info("**Instandhaltungskosten pro Jahr bei Altbauten:** :orange[Wenn kein Hausgeld, aber Herstellungskosten bekannt, (z. B. aus Gutachten), dann Anwendung der Petersschen Formel: **(Herstellungskosten * 1,5) / (80 Jahre * qm)**]")
            st.info("**Instandhaltungskosten pro Jahr bei Immobilien jünger als 22 Jahre:** :orange[10,61 € je qm pro Jahr]")
            st.info("**Instandhaltungskosten pro Jahr bei Immobilien älter als 22 Jahre:** :orange[13,45 € je qm pro Jahr]")
            st.info("**Instandhaltungskosten pro Jahr bei Immobilien älter als 32 Jahre:** :orange[17,18 € je qm pro Jahr]")
        
        col1, col2 = st.columns(2)
        with col1:
            mietausfallwagnis_prozent = read_value(aktenzeichen, 'bewirtschaftungskosten', 'mietausfallwagnis_prozent')
            if mietausfallwagnis_prozent == None:
                mietausfallwagnis_prozent = 0.0
            mietausfallwagnis_prozent =  st.number_input("Mietausfallwagnis in Prozent", value=(mietausfallwagnis_prozent * 100) or 0.0, step=1.0, help="In Prozent vom Rohertrag. 2% in der Stadt, etwas höher auf dem Land")
            
        with col2:
            mietausfallwagnis_betrag =  st.number_input("Mietausfallwagniskosten im Jahr", value=mietausfallwagnis_prozent /100 * kaltmiete * 12, disabled = True)
        
        st.warning("Eigene Anmerkung: Die Mietausfallwagnis erhöhen, wenn a) Immobilie renoviert/saniert werden muss, je nach Umfang und b) wenn Immobilie noch eigengenutzt ist")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Gesamte Bewirtschaftungskosten")
            
        with col2:
            jaehrliche_bewirtschaftungskosten = round(verwaltungskosten_pro_wohnung + instandhaltungskosten_gesamt + mietausfallwagnis_betrag + erbbauzins,2)
            st.write(jaehrliche_bewirtschaftungskosten)
            
        if st.button(" Daten speichern  "):
            update_table(aktenzeichen, 'bewirtschaftungskosten', 'verwaltungskosten_pro_wohnung', verwaltungskosten_pro_wohnung)
            update_table(aktenzeichen, 'bewirtschaftungskosten', 'instandhaltungskosten_pro_qm', instandhaltungskosten_pro_qm)
            update_table(aktenzeichen, 'bewirtschaftungskosten', 'mietausfallwagnis_prozent', mietausfallwagnis_prozent/100)
            #update_table(aktenzeichen, 'erbbaurecht', 'erbbauzins', erbbauzins)
            update_table(aktenzeichen, 'bewirtschaftungskosten', 'hausgeld', hausgeld)
            st.write("Daten wurden gespeichert")
            
    with tab3:
        st.subheader("Nettomieteinnahmen nach Bewirtschaftungskosten")
        jaehrliche_mieteinnahmen = kaltmiete * 12
        
        nettomieteinnahmen = jaehrliche_mieteinnahmen -  jaehrliche_bewirtschaftungskosten
        
        jaehrliche_mieteinnahmen = st.number_input("Jährliche Mieteinnahmen:", value = jaehrliche_mieteinnahmen, disabled = True)
        jaehrliche_bewirtschaftungskosten = st.number_input("Jährliche Bewirtschaftungskosten:", value = jaehrliche_bewirtschaftungskosten, disabled = True)
        nettomieteinnahmen = st.number_input("Nettomieteinnahmen nach Bewirtschaftungskosten", value = nettomieteinnahmen, disabled = True)
        
        return nettomieteinnahmen
    
def steuern(aktenzeichen):
    st.subheader("Steuern")
    
    st.info("Hinweis: Dieser Menupunkt ist noch inaktiv")
    col1, col2 = st.columns(2)
    
    with col1:
        bodenrichtwert_pro_qm = read_value(aktenzeichen, 'steuern', 'bodenrichtwert_pro_qm')
        if bodenrichtwert_pro_qm == None:
            bodenrichtwert_pro_qm = 0.0
        bodenrichtwert_pro_qm =  st.number_input(f"Bodenrichtwert pro qm:", value=bodenrichtwert_pro_qm, step=1.0, help="Zum Thema Steuern gibt es ein weiteres Buch von Goldwein mit dem Titel :green[Steuerleitfaden für Immobilieninvestoren: Der ultimative Steuerratgeber] ")
        
    with col2:
        anteiliger_bodenwert = read_value(aktenzeichen, 'steuern', 'anteiliger_bodenwert')
        if anteiliger_bodenwert == None:
            anteiliger_bodenwert = 0.0
        anteiliger_bodenwert =  st.number_input(f"Anteiliger Bodenwert:", value=anteiliger_bodenwert, step=1.0, disabled = True, help="Wichtiger Hinweis! Bei einer Investition in eine einzelne Eigentumswohnung müssen Sie in Feld I 16 den Bodenwert mit dem Miteigentumsanteil der Eigentumswohnung am Gemeinschaftseigentum multiplizieren. Es wird dazu auf die Ausführungen in Abschnitt IV. 5. d) des Buches verwiesen.")
     
    with col1:
        anteil_anschaffungskosten = read_value(aktenzeichen, 'steuern', 'anteil_anschaffungskosten')
        if anteil_anschaffungskosten == None:
            anteil_anschaffungskosten = 0.0
        anteil_anschaffungskosten =  st.number_input(f"Anteil Anschaffungskosten Gebäude (AfA-Basis):", value=anteil_anschaffungskosten, disabled = True, step=1.0, help="Erweiterte Anschaffungskosten abzüglich anteiliger Bodenwert")
        
    
def renditeberechnung(aktenzeichen, erweiterte_anschaffungskosten, jaehrliche_nettomieteinnahmen):
    
    # Initialisierung
    eigenkapitalrendite_aus_vermietung = 0
    rendite_aus_immobilienhandel = 0
    
    tab1, tab2, tab3 = st.tabs(['Mietrendite', 'Rendite aus Immobilienkauf und -verkauf', 'Gesamtrendite'])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            erweiterte_anschaffungskosten =  st.number_input("Erweiterte Anschaffungskosten", value=erweiterte_anschaffungskosten, disabled = True)
        
        with col2:
            jaehrliche_nettomieteinnahmen =  st.number_input("Jährliche Nettomieteinnahmen", value=jaehrliche_nettomieteinnahmen, disabled = True)
            
        with col1:
            eigenkapital = read_value(aktenzeichen, 'renditen', 'eigenkapital')
            #max_wert= erweiterte_anschaffungskosten
            if eigenkapital == None:
                eigenkapital = 0.0
            if eigenkapital > erweiterte_anschaffungskosten:
                eigenkapital = erweiterte_anschaffungskosten
                
            eigenkapital =  st.number_input("Eigenkapital",  min_value = 0.0, max_value =erweiterte_anschaffungskosten, value = eigenkapital, step=10000.0)
            
        with col2:
            fremdkapital = erweiterte_anschaffungskosten - eigenkapital
            fremdkapital  =  st.number_input("Kredit", value=fremdkapital, disabled = True)           
         
        with st.expander("Hinweise zu den Bauzinsen"):
            st.info("https://www.drklein.de/aktuelle-bauzinsen.html")
            st.info("https://www.finanztip.de/baufinanzierung/hypothekenzinsen/")
            
        col1, col2 = st.columns(2)
        
        with col1:
            kreditzinssatz = read_value(aktenzeichen, 'renditen', 'kreditzinssatz')
            if kreditzinssatz == None:
                kreditzinssatz = 0.0
            kreditzinssatz =  st.number_input("Kreditzinssatz",  min_value = 0.0, value = kreditzinssatz * 100, step=0.1)
            kreditzinssatz = kreditzinssatz / 100
            
        with col2:
            laufzeit = read_value(aktenzeichen, 'renditen', 'laufzeit')
            if laufzeit == None:
                laufzeit = 10
            laufzeit = st.slider("Laufzeit", min_value=0, max_value=30, step = 1, value=laufzeit)
            
        with col1:
            jaehrliche_mietpreissteigerung_prozent = read_value(aktenzeichen, 'renditen', 'jaehrliche_mietpreissteigerung_prozent')
            if jaehrliche_mietpreissteigerung_prozent == None:
                jaehrliche_mietpreissteigerung_prozent = 0.0
            jaehrliche_mietpreissteigerung_prozent =  st.number_input("Jährliche prognostizierte Mietpreissteigerung",  min_value = 0.0, value = jaehrliche_mietpreissteigerung_prozent * 100, step=0.01, help="Entwicklung der Kaltmieten von 1991 bis 2022: https://de.statista.com/statistik/daten/studie/1065/umfrage/verbraucherpreisindex-wohnungsmiete-nebenkosten/ Die jährliche Mietsteigerung beträgt durchschnittlich 2,1 %.")
            jaehrliche_mietpreissteigerung_prozent = jaehrliche_mietpreissteigerung_prozent / 100
        
        with col2:
            st.caption("Mieterhöhungen: Nicht mehr als 20% in 3 Jahren, in Regionen mit angespannten Wohnungsmärkten nicht mehr als 15%, nicht öfter als alle 15 Monate")
            
        # Berechnung der Annuitäten
        monatliche_nettomieteinahmen = jaehrliche_nettomieteinnahmen / 12
        fremdkapital_rest = fremdkapital
        eigenkapital_zuwachs = eigenkapital 
        data=[]
        
        # Monatliche Kreditrate berechnen
        if laufzeit > 0 and kreditzinssatz > 0:
            kreditrate = fremdkapital_rest * (kreditzinssatz / 12) / (1 - (1 + kreditzinssatz / 12) ** (-laufzeit * 12))

            # Berechnungen für jeden Monat
            jahrliche_eigenkapitalrendite = 0
            gesamte_eigenkapitalrendite = 0
            gesamte_tilgung = 0
            gesamte_zinsen = 0
            gesamte_kreditrate = 0

            for monat in range(1, laufzeit * 12 + 1):
                zinsen = fremdkapital_rest * kreditzinssatz / 12
                tilgung = kreditrate - zinsen
                fremdkapital_rest = fremdkapital_rest - tilgung
                
                #Eigenkapitalrendite = (Mieteinnahmen - Zinsen) / (Fremdkapital + 20000)
                if eigenkapital > 0:
                    eigenkapitalrendite = (monatliche_nettomieteinahmen - zinsen) * 100 * 12/ eigenkapital_zuwachs
                else:
                    eigenkapitalrendite = 0
                eigenkapital_zuwachs += tilgung
                
                if (monat) % 15 == 0:
                    # Mieterhöhungen nur alle 15 Monate gesetzlich erlaubt. Mietsteigerung dann 2,1% (jährl. Mietpreissteigerung) /12 (je Monat) * 15 Monate = 2,625%
                    monatliche_nettomieteinahmen = monatliche_nettomieteinahmen *  (1+( jaehrliche_mietpreissteigerung_prozent /12 * 15)) 

                # Durchschnittliche jährliche Eigenkapitalrendite berechnen
                if monat % 12 == 0:
                    jahrliche_eigenkapitalrendite = jahrliche_eigenkapitalrendite + eigenkapitalrendite
                    #print("Durchschnittliche jährliche Eigenkapitalrendite für Jahr", int(Monat / 12), ":", jahrliche_eigenkapitalrendite / 12)
                    jahrliche_eigenkapitalrendite = 0
                
                # Gesamte Eigenkapitalrendite berechnen
                gesamte_eigenkapitalrendite = gesamte_eigenkapitalrendite + eigenkapitalrendite
                gesamte_tilgung = gesamte_tilgung + tilgung
                gesamte_zinsen += zinsen
                gesamte_kreditrate +=kreditrate
                data.append([monat, round(tilgung,2), round(zinsen,2), round(kreditrate,2), round(eigenkapitalrendite,2), round(eigenkapital_zuwachs,2),  round(monatliche_nettomieteinahmen,2), round(monatliche_nettomieteinahmen - zinsen,2)])

            df = pd.DataFrame(data, columns=['Monat', 'Tilgung', 'Zinsen', 'Kreditrate', 'EK-Rendite', 'Eigenkapital', 'Mieteinnahmen',  'Gewinn'])
            st.write("Monatl. Netto-Mieteinnahmen (nach Bewirtschaftungskosten) nach der Laufzeit:", round(monatliche_nettomieteinahmen))

            with st.expander("Zeige Annuitätenplan an"):
                st.write(df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gesamte Eigenkapitalrendite ausgeben            
                st.write("Gesamte Tilgung: ")
                st.write("\+ Gesamte Zinsen: ")
                st.write("= Gesamte Kreditrate: ")
                st.write("\+ Zu Beginn eingebrachtes EK: ")
                st.write("= Gesamte Kosten (EK + Kreditrate): ")
                st.write("Gesamte Eigenkapitalrendite aus Vermietung:")
                
            with col2:
                eigenkapitalrendite_aus_vermietung = gesamte_eigenkapitalrendite / (laufzeit * 12)
                st.write(round(gesamte_tilgung,2))
                st.write(round(gesamte_zinsen,2))
                st.write(round(gesamte_kreditrate,2))
                st.write(round(eigenkapital,2))
                st.write(round((gesamte_kreditrate + eigenkapital),2))
                st.write(round(eigenkapitalrendite_aus_vermietung,2))
                
            # Diese updates müssen hier stehen    
            update_table(aktenzeichen, 'renditen', 'eigenkapital', eigenkapital)
            update_table(aktenzeichen, 'renditen', 'bankkredit', fremdkapital)
            if fremdkapital >0:
                update_table(aktenzeichen, 'kaufkosten', 'notarkosten_prozent', 0.015)
            else:
                update_table(aktenzeichen, 'kaufkosten', 'notarkosten_prozent', 0.0)
        if st.button("Daten speichern   "):                
            update_table(aktenzeichen, 'renditen', 'kreditzinssatz', kreditzinssatz)
            update_table(aktenzeichen, 'renditen', 'laufzeit', laufzeit)
            update_table(aktenzeichen, 'renditen', 'jaehrliche_mietpreissteigerung_prozent', jaehrliche_mietpreissteigerung_prozent)
            
            st.write("Daten gespeichert!")
            
            if fremdkapital > 0:
                # es fallen Notarkosten an
                st.warning("Es fällt ein Kredit an. Die Notarkosten wurden auf 1,5% gesetzt und können in den **Erweiterten Anschaffungskosten** geändert werden")
                time.sleep(5)
                st.experimental_rerun()
            else:
                # es fallen keine Notarkosten an
                update_table(aktenzeichen, 'kaufkosten', 'notarkosten_prozent', 0.0)
                st.info("Es fällt kein Kredit an. Die Notarkosten wurden auf Null gesetzt. ")
                time.sleep(5)
                st.experimental_rerun()
                
    with tab2:
        immowelt_objekt = read_value(aktenzeichen, 'schaetzwerte', 'immowelt_objekt')
        immoscout_objekt = read_value(aktenzeichen, 'schaetzwerte', 'immoscout_objekt')
        
        if immowelt_objekt:
            st.write("Geschätzter Marktwert lauf Immowelt: ", immowelt_objekt)
        if immoscout_objekt:
            st.write("Geschätzter Marktwert lauf Immoscout24: ", immoscout_objekt)
        with st.expander("Allgemeiner Hinweis"):
            st.info("In diesem Abschnitt wird die mögliche Gesamtrendite errechnet. Dazu wird aus dem möglichen Verkaufspreis nach Ende der Laufzeit und den erweiterten Anschaffungskosten eine jährliche Rendite errechnet. Die Renditen aus dem Immobilienhandel und aus der Vermietung werden addiert und ergeben eine Gesamtrendite.")
            
        col1, col2 = st.columns(2)
        
        with col1:
            marktwert_nach_aufwertung = read_value(aktenzeichen, 'renditen', 'marktwert_nach_aufwertung')
            if marktwert_nach_aufwertung == None:
                marktwert_nach_aufwertung = 0.0
            marktwert_nach_aufwertung =  st.number_input("Prognostizierter Marktwert nach Aufwertung",  min_value = 0.0, value = marktwert_nach_aufwertung, step=10000.0)
            
        with col2:
            jaehrliche_marktpreissteigerung_prozent = read_value(aktenzeichen, 'renditen', 'jaehrliche_marktpreissteigerung_prozent')
            if jaehrliche_marktpreissteigerung_prozent == None:
                jaehrliche_marktpreissteigerung_prozent = 0.0
            jaehrliche_marktpreissteigerung_prozent =  st.number_input("Prognostizierte jährliche Marktpreissteigerung in Prozent", value = jaehrliche_marktpreissteigerung_prozent * 100, step=0.1)
            jaehrliche_marktpreissteigerung_prozent = jaehrliche_marktpreissteigerung_prozent / 100
        
        with st.expander("Hinweis zu den Marktpreissteigerungen"):
            st.info("In 2008 (Immobilienkrise) gingen die Preise um 5-10% zurück. Langfristig durchschnittliche Erhöhung um 3,5% pro Jahr, in Wachstumsregionen um 4%. Allerdings (persönliche Meinung) sollten die Immobilienpreise nicht stärker steigen, als die Mieten :green[(**2,1 %**)]. https://de.statista.com/statistik/daten/studie/597304/umfrage/immobilienpreise-alle-baujahre-in-deutschland/. Zudem, zwischen 2016 und 2022 beschleunigte sich der Anstieg auf 7%. ")

        col1, col2 = st.columns(2)   
        with col1:
            st.write("Erweiterte Anschaffungskosten:")
            st.write("Prognostizierter Marktpreis in ", laufzeit, "Jahren")
            st.write("Differenz:")
            #st.write("Jährliche Rendite aus Vermietung:")
            st.write("Jährliche Rendite aus Immobilienhandel:")
            zukuenftiger_vp = round(marktwert_nach_aufwertung * (1+ jaehrliche_marktpreissteigerung_prozent) ** laufzeit,2)
            differenz = round(zukuenftiger_vp - erweiterte_anschaffungskosten,2)
            # Berechnung von Wachstumsraten --> berücksichtigt den Zinseszinseffekt
            if erweiterte_anschaffungskosten > 0 and laufzeit > 0:
                rendite_aus_immobilienhandel= round((((zukuenftiger_vp / erweiterte_anschaffungskosten) ** (1/laufzeit)) - 1 )*100,2)
            # Zinsformel: Z = K * p * t / (100 * 360) --> berücksichtigt nicht den Zinseszinseffekt
            # p = (Z * 100 * 360) / (K * t)
            # p = Z = zukuenftiger_vp - erweiterte_anschaffungskosten 
            #jährliche_rendite_aus_immobilienhandel = (((zukuenftiger_vp - erweiterte_anschaffungskosten) * 100 )/ (erweiterte_anschaffungskosten * Laufzeit)) 
            #st.write("Gesamtrendite:")
            gesamtrendite = round(eigenkapitalrendite_aus_vermietung + rendite_aus_immobilienhandel,2)
            
        with col2:
            st.write(erweiterte_anschaffungskosten)
            st.write(zukuenftiger_vp)
            st.write(differenz)
            #st.write(round(eigenkapitalrendite_aus_vermietung,2))
            st.write(rendite_aus_immobilienhandel)
            #st.write(gesamtrendite)
            
        if st.button("  Daten speichern  "):
            update_table(aktenzeichen, 'renditen', 'marktwert_nach_aufwertung', marktwert_nach_aufwertung)
            update_table(aktenzeichen, 'renditen', 'jaehrliche_marktpreissteigerung_prozent', jaehrliche_marktpreissteigerung_prozent)
            st.write("Daten gespeichert")
            
    with tab3:
        st.subheader("Gesamtrendite")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Jährliche Rendite aus Vermietung")
            st.write("Jährliche Rendite aus dem Verkauf")
            st.write("Jährliche Gesamtrendite")
            
        with col2:
            st.write(round(eigenkapitalrendite_aus_vermietung,2))
            st.write(round(rendite_aus_immobilienhandel,2))
            st.write(round(eigenkapitalrendite_aus_vermietung + rendite_aus_immobilienhandel,2))

    return eigenkapitalrendite_aus_vermietung, rendite_aus_immobilienhandel
        
def beschreibung(aktenzeichen):
    tab1, tab2, tab3, tab4, tab5= st.tabs(['Objektbeschreibung', 'Schätzwerte', 'Allgemeines', 'Abschluss', 'Map'])
    
    with tab1:
        st.subheader("Objektbeschreibung")
        
        with st.expander("Links"):
            st.info("https://geoportal-hamburg.de")
        
        objekt_beschreibung = read_value(aktenzeichen, 'objektbeschreibung', 'objekt_beschreibung')
        if objekt_beschreibung == None:
            objekt_beschreibung = ''
        objekt_beschreibung = st.text_area('Objektbeschreibung',  value=objekt_beschreibung)
        
        ausstattung_beschreibung = read_value(aktenzeichen, 'objektbeschreibung', 'ausstattung_beschreibung')
        if ausstattung_beschreibung == None:
            ausstattung_beschreibung = ''
        ausstattung_beschreibung = st.text_area('Ausstattungsbeschreibung',  value=ausstattung_beschreibung)
        
        besonderheiten= read_value(aktenzeichen, 'objektbeschreibung', 'besonderheiten')
        if besonderheiten == None:
            besonderheiten = ''
        besonderheiten = st.text_area('Besonderheiten',  value=besonderheiten)
        
        maengel= read_value(aktenzeichen, 'objektbeschreibung', 'maengel')
        if maengel == None:
            maengel  = ''
        maengel  = st.text_area('Mängel, Schäden, baulicher Zustand',  value=maengel )
        
        if st.button("   Daten speichern!  "):
            update_table(aktenzeichen, 'objektbeschreibung', 'objekt_beschreibung', objekt_beschreibung)
            update_table(aktenzeichen, 'objektbeschreibung', 'ausstattung_beschreibung', ausstattung_beschreibung)
            update_table(aktenzeichen, 'objektbeschreibung', 'besonderheiten', besonderheiten)
            update_table(aktenzeichen, 'objektbeschreibung', 'maengel', maengel)
            
            st.write("Daten gespeichert")
        
    with tab2:
        st.subheader("Werte aus dem Gutachten")
        st.info("Hinweis: Bei der Ermittlung des Verkehrswerts wird stets der lastenfreie Wert eines Grundstücks ermittelt. Bestehende Rechte aus dem Grundbuch Abteilung II (z. B. Erbbaurecht) bleiben daher in der Regel unberücksichtigt")
        col1, col2 = st.columns(2)
        
        with col1:
            bodenwert = read_value(aktenzeichen, 'schaetzwerte', 'bodenwert')
            if bodenwert == None:
                bodenwert = 0.0
            bodenwert = st.number_input("Bodenwert", value=bodenwert, min_value = 0.0, step=1000.0, help="Der Bodenwert bezieht sich auf den geschätzten Wert des unbebauten Landes einer Immobilie.")
            
        with col2:
            sachwert = read_value(aktenzeichen, 'schaetzwerte', 'sachwert')
            if sachwert == None:
                sachwert = 0.0
            sachwert = st.number_input("Sachwert", value=sachwert, min_value = 0.0, step=100.0, help="Der geschätzte Wert einer Immobilie basierend auf den Baukosten oder Wiederherstellungskosten")
            
        with col1:
            verkehrswert = read_value(aktenzeichen, 'schaetzwerte', 'verkehrswert')
            if verkehrswert == None:
                verkehrswert = 0.0
            verkehrswert = st.number_input("Verkehrswert", value=verkehrswert, min_value = 0.0, step=1000.0, help="Der geschätzte Preis, den man für eine Immobilie beim Verkauf erzielen könnte. Gelegentlich ist hier ein Risikoabschlag abgezogen, z. B. wegen fehlender Innenbesichtigung.")
            
        with col2:
            ertragswert = read_value(aktenzeichen, 'schaetzwerte', 'ertragswert')
            if ertragswert == None:
                ertragswert = 0.0
            ertragswert = st.number_input("Ertragswert", value=ertragswert, min_value = 0.0, step=100.0, help="Der Wert einer Immobilie basierend auf den potenziellen Einnahmen, die durch Vermietung oder Nutzung erzielt werden können")
       
        with col1:
            vergleichswert = read_value(aktenzeichen, 'schaetzwerte', 'vergleichswert')
            vergleichswert = st.number_input("Vergleichswert", value=vergleichswert or 0.0, min_value = 0.0, step=1000.0, help="Wert, der anhand ähnlicher Immobilien in derselben Region ermittelt wird, um eine Einschätzung des Marktwerts der betrachteten Immobilie zu ermöglichen.")
            
        with col2:
            marktuebliche_monatsmiete = read_value(aktenzeichen, 'schaetzwerte', 'marktuebliche_monatsmiete')
            if marktuebliche_monatsmiete == None:
                marktuebliche_monatsmiete = 0.0
            marktuebliche_monatsmiete = st.number_input("Rohertrag", value=marktuebliche_monatsmiete, min_value = 0.0, step=10.0, help = "Marktübliche Monatskaltmiete")
        
        st.subheader("Werte von Drittanbietern")
        immowelt_objekt = read_value(aktenzeichen, 'schaetzwerte', 'immowelt_objekt')
        if immowelt_objekt == None:
            immowelt_objekt = 0.0
        immowelt_objekt = st.number_input("Immowelt Haus", value=immowelt_objekt, min_value = 0.0, step=1000.0)

        col1, col2 = st.columns(2)
        with col1:
            immoscout_objekt = read_value(aktenzeichen, 'schaetzwerte', 'immoscout_objekt')
            if immoscout_objekt == None:
                immoscout_objekt = 0.0
            immoscout_objekt = st.number_input("Immoscout Haus", value=immoscout_objekt, min_value = 0.0, step=1000.0)
            
        with col2:
            immoscout_miete = read_value(aktenzeichen, 'schaetzwerte', 'immoscout_miete')
            if immoscout_miete == None:
                immoscout_miete = 0.0
            immoscout_miete = st.number_input("Immoscout Miete", value=immoscout_miete, min_value = 0.0, step=100.0)
            
        

        if st.button("  Daten speichern!  "):
            update_table(aktenzeichen, 'schaetzwerte', 'immowelt_objekt', immowelt_objekt)
            update_table(aktenzeichen, 'schaetzwerte', 'immoscout_objekt', immoscout_objekt)
            update_table(aktenzeichen, 'schaetzwerte', 'immoscout_miete', immoscout_miete)
            update_table(aktenzeichen, 'schaetzwerte', 'bodenwert', bodenwert)
            update_table(aktenzeichen, 'schaetzwerte', 'sachwert', sachwert)
            update_table(aktenzeichen, 'schaetzwerte', 'verkehrswert', verkehrswert)
            update_table(aktenzeichen, 'schaetzwerte', 'ertragswert', ertragswert)
            update_table(aktenzeichen, 'schaetzwerte', 'vergleichswert', vergleichswert)
            update_table(aktenzeichen, 'schaetzwerte', 'marktuebliche_monatsmiete', marktuebliche_monatsmiete)
            st.write("Daten gespeichert")
            
    with tab3:
        st.subheader("Allgemeines")
        
        #with st.expander("Hinweis zum Erbbaurecht:"):
        besteht_erbbaurecht = read_value(aktenzeichen, 'erbbaurecht', 'besteht_erbbaurecht')
        if besteht_erbbaurecht:
            st.info("Es besteht ein Erbbaurecht: Die Höhe der Entschädigung für das Bauwerk kann vertraglich frei geregelt, auch gänzlich ausgeschlossen werden. Ist keine diesbezügliche Entschädigung vereinbart, so ist der volle Verkehrswert des Gebäude(anteil)s zu entschädigen.")
            
        grundbuch_abteilung2 = read_value(aktenzeichen, 'allgemeines', 'grundbuch_abteilung2')
        if grundbuch_abteilung2 == None:
            grundbuch_abteilung2 = ''
        grundbuch_abteilung2 = st.text_area('Belastungen in Abteilung II',  value=grundbuch_abteilung2)
             
        baulasten = read_value(aktenzeichen, 'allgemeines', 'baulasten')
        if baulasten == None:
            baulasten = ''
        baulasten = st.text_area('Baulasten', value=baulasten, help="rechtliche Verpflichtungen oder Beschränkungen, die auf einem Grundstück oder einer Immobilie lasten, z. B. Bebauungsbeschränkungen oder Nutzungsbeschränkungen)")
        
        nutzungsverhaeltnisse = read_value(aktenzeichen, 'allgemeines', 'nutzungsverhältnisse')
        if nutzungsverhaeltnisse == None:
            nutzungsverhaeltnisse = ''
        nutzungsverhaeltnisse = st.text_area('Nutzungsverhältnisse', value=nutzungsverhaeltnisse, help="Eigengenutzt, vermietet, ...")
        
        erschliessung = read_value(aktenzeichen, 'allgemeines', 'erschliessung')
        if erschliessung == None:
            erschliessung = ''
        erschliessung= st.text_area('Erschließung', value=erschliessung, help="Erschließungsbeiträge, Sielbaubeiträge, ...")
        
        energieausweis = read_value(aktenzeichen, 'allgemeines', 'energieausweis')
        if energieausweis == None:
            energieausweis = ''
        energieausweis= st.text_area('Energieausweis', value=energieausweis)
        
        st.info("Miteigentumsanteil einbauen und berücksichtigen")
        denkmalschutz = read_value(aktenzeichen, 'allgemeines', 'denkmalschutz')
        denkmalschutz = st.checkbox("Besteht Denkmalschutz?", value=denkmalschutz)

        
        if st.button("  Daten speichern!   "):
            update_table(aktenzeichen, 'allgemeines', 'grundbuch_abteilung2', grundbuch_abteilung2)
            update_table(aktenzeichen, 'allgemeines', 'baulasten', baulasten)
            update_table(aktenzeichen, 'allgemeines', 'nutzungsverhältnisse', nutzungsverhaeltnisse)
            update_table(aktenzeichen, 'allgemeines', 'erschliessung', erschliessung)
            update_table(aktenzeichen, 'allgemeines', 'energieausweis', energieausweis)
            update_table(aktenzeichen, 'allgemeines', 'denkmalschutz', denkmalschutz)
            st.write("Daten gespeichert")
            
    with tab4:
        st.subheader("Abschließende Betrachtungen")
        
        termin_aufgehoben = read_value(aktenzeichen, 'abschluss', 'termin_aufgehoben')
        termin_aufgehoben = st.checkbox('Der Termin wurde aufgehoben', value = termin_aufgehoben)
        
        if st.button("   Daten speichern!   "):
            update_table(aktenzeichen, 'abschluss', 'termin_aufgehoben', termin_aufgehoben)
            
    with tab5:
        st.subheader("Karte")
        strasse = read_value(aktenzeichen, 'basisdaten', 'strasse')
        plz = read_value(aktenzeichen, 'basisdaten', 'plz')
        ort = read_value(aktenzeichen, 'basisdaten', 'ort')
        #st.caption(strasse)
        st.caption(strasse + ", " + plz + " "+ ort)  

        # OpenStreetMap API-URL
        url = 'https://nominatim.openstreetmap.org/search'

        # Benutzereingabe sammeln
        query = strasse + ' ' + plz + ' ' + ort
        #st.write("Query:", query)
        # GET-Anfrage an OpenStreetMap senden
        if query:
            params = {'q': query, 'format': 'json'}
            response = requests.get(url, params=params)
            data = json.loads(response.text)
            
            # Erste Ergebnisposition auswählen
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            
            st.write("Breitengrad: ", lat, "Längengrad: ", lon)
            
            # Streamlit-Karte erstellen und Koordinaten hinzufügen
            m = folium.Map(location=[lat, lon], zoom_start=14)
            #Draw(export=True).add_to(m)
            tooltip = "Koordinaten: {}, {}".format(lat, lon)
            folium.Marker([lat, lon], tooltip=tooltip).add_to(m)
            folium_static(m)
            
            #df = pd.DataFrame((lat, lon), columns=['lat', 'lon'])
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=14)
        
def dokumente(aktenzeichen):
    tab1, tab2 = st.tabs(["Upload", "Download"])
    gutachten = read_value(aktenzeichen, 'dokumente', 'gutachten')
    expose = read_value(aktenzeichen, 'dokumente', 'expose')
             
    with tab1:
        st.subheader("Upload von Dokumenten")
        datei_gutachten = st.file_uploader("Gutachten hochladen", accept_multiple_files=False,  type=['pdf'], help='Bisher sind nur pdf-Dateien erlaubt')
        if gutachten is not None:
            st.warning("Achtung: Es existiert bereits ein Gutachten. Dieses wird überschrieben.")
        if datei_gutachten is not None:
            datei_upload(aktenzeichen, 'gutachten', datei_gutachten)
            
        datei_expose = st.file_uploader("Expose hochladen", accept_multiple_files=False,  type=['pdf'], help='Bisher sind nur pdf-Dateien erlaubt')
        if expose is not None:
                st.warning("Achtung: Es existiert bereits ein Expose. Dieses wird überschrieben.")
        if datei_expose is not None:          
            datei_upload(aktenzeichen, 'expose', datei_expose)
            
    with tab2:
        st.subheader("Download von Dokumenten")
        
        dateiname_gutachten = 'Gutachten-' +aktenzeichen + '.pdf'
        if gutachten is not None:
            st.download_button(
            file_name=dateiname_gutachten,
            label=dateiname_gutachten,
            data=gutachten,          
            mime='application/octet-stream')
        
        dateiname_expose =  'Expose-' +aktenzeichen + '.pdf'   
        if expose is not None:
            st.download_button(
            file_name=dateiname_expose,
            label=dateiname_expose,
            data=expose,            
            mime='application/octet-stream')

# Verbindung zur Datenbank herstellen
dbname = 'immo.db'
conn = sqlite3.connect(dbname)
cursor = conn.cursor()

# Struktur aufbauen
#tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(['Objekt', 'Basis', 'Erweiterte Anschaffungskosten', 'Mietgewinn', 'Steuern', 'Renditen', 'Beschreibung', 'Dokumente'])
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Objekt', 'Basis', 'Erweiterte Anschaffungskosten', 'Mietgewinn', 'Steuern', 'Renditen', 'Beschreibung'])

with tab1:
    aktenzeichen = objekt()

with tab2:
    basis(aktenzeichen)
    
with tab3:
    erweiterte_anschaffungskosten = erweiterte_anschaffungskosten(aktenzeichen)
    
with tab4:
    nettomieteinnahmen = mietgewinn(aktenzeichen)
    
with tab5:
    steuern(aktenzeichen)
    
with tab6:
    eigenkapitalrendite_aus_vermietung, rendite_aus_immobilienhandel = renditeberechnung(aktenzeichen, erweiterte_anschaffungskosten, nettomieteinnahmen)
    
with tab7:
    beschreibung(aktenzeichen)
    
# with tab8:
#     dokumente(aktenzeichen)
    
sidebar(aktenzeichen, eigenkapitalrendite_aus_vermietung, rendite_aus_immobilienhandel, erweiterte_anschaffungskosten)