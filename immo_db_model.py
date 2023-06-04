import sqlite3

# Erstellen der Datenbank
try:
    conn = sqlite3.connect('immo.db')
    print("Datenbank erfolgreich erstellt!")
except:
    print("Fehler beim Erstellen der Datenbank!")

# Erstelle einen Cursor
c = conn.cursor()

# Basisdaten
c.execute("""CREATE TABLE IF NOT EXISTS basisdaten (
            aktenzeichen TEXT PRIMARY KEY,
            amtsgericht TEXT,
            versteigerungsdatum DATE,
            titel TEXT,
            letztes_update DATE,
            strasse TEXT,
            plz TEXT,
            ort TEXT,
            bundesland TEXT,
            objekt_art TEXT,
            baujahr TEXT,
            qm_wohnung REAL,
            qm_grundstueck REAL,
            anzahl_zimmer REAL,
            url TEXT,
            versteigerungsgrund TEXT
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='basisdaten'").fetchone() is not None:
    print("Die basisdaten Tabelle wurde erfolgreich erstellt.")
else:
    print("Die basisdaten Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())

# Mieterliste
# --> noch zu erstellen

# Kaufkosten
c.execute("""CREATE TABLE IF NOT EXISTS kaufkosten (
            aktenzeichen TEXT PRIMARY KEY,
            max_gebotspreis REAL,
            grunderwerbssteuer_prozent REAL,
            zuschlagskosten_prozent REAL,
            notarkosten_prozent REAL,
            renovierungskosten REAL,
            umbaukosten REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kaufkosten'").fetchone() is not None:
    print("Die kaufkosten Tabelle wurde erfolgreich erstellt.")
else:
    print("Die kaufkosten Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())

# Gesamte Mieteinnahmen
c.execute("""CREATE TABLE IF NOT EXISTS mieteinnahmen (
            aktenzeichen TEXT PRIMARY KEY,
            kaltmiete_gesamt REAL,
            mietspiegelmiete_pro_qm REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mieteinnahmen'").fetchone() is not None:
    print("Die mieteinnahmen Tabelle wurde erfolgreich erstellt.")
else:
    print("Die mieteinnahmen Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Bewirtschaftungskosten
c.execute("""CREATE TABLE IF NOT EXISTS bewirtschaftungskosten (
            aktenzeichen TEXT PRIMARY KEY,
            hausgeld REAL,
            verwaltungskosten_pro_wohnung REAL,
            instandhaltungskosten_pro_qm REAL,
            mietausfallwagnis_prozent REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bewirtschaftungskosten'").fetchone() is not None:
    print("Die bewirtschaftungskosten Tabelle wurde erfolgreich erstellt.")
else:
    print("Die bewirtschaftungskosten Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Steuern
c.execute("""CREATE TABLE IF NOT EXISTS steuern (
            aktenzeichen TEXT PRIMARY KEY,
            bodenrichtwert_pro_qm REAL,
            anteiliger_bodenwert REAL,
            anteil_anschaffungskosten REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='steuern'").fetchone() is not None:
    print("Die steuern Tabelle wurde erfolgreich erstellt.")
else:
    print("Die steuern Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Renditen
c.execute("""CREATE TABLE IF NOT EXISTS renditen (
            aktenzeichen TEXT PRIMARY KEY,
            eigenkapital REAL,
            bankkredit REAL,
            kreditzinssatz REAL,
            laufzeit INT,
            jaehrliche_mietpreissteigerung_prozent REAL,
            marktwert_nach_aufwertung REAL,
            jaehrliche_marktpreissteigerung_prozent REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='renditen'").fetchone() is not None:
    print("Die renditen Tabelle wurde erfolgreich erstellt.")
else:
    print("Die renditen Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Beschreibungen
c.execute("""CREATE TABLE IF NOT EXISTS objektbeschreibung (
            aktenzeichen TEXT PRIMARY KEY,
            objekt_beschreibung TEXT,
            ausstattung_beschreibung TEXT,
            besonderheiten TEXT,
            maengel TEXT
            )""")
            
if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='objektbeschreibung'").fetchone() is not None:
    print("Die objektbeschreibung Tabelle wurde erfolgreich erstellt.")
else:
    print("Die objektbeschreibung Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
 
# DEFAULT-Parameter    
c.execute("""CREATE TABLE IF NOT EXISTS parameter (
            max_mietaufschlag REAL,
            notar_prozent REAL,
            renovierungskosten_prozent REAL,
            umbaukosten_prozent REAL,
            verwaltungskosten REAL,
            instandhaltungskosten_m2 REAL,
            mietausfallwagnis_prozent REAL, 
            kredit_zinssatz REAL,
            kredit_laufzeit INT,
            eigenkapital_anteil REAL,
            jaehrliche_mietpreissteigerung REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parameter'").fetchone() is not None:
    print("Die parameter Tabelle wurde erfolgreich erstellt.")
else:
    print("Die parameter Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Amtsgerichte
c.execute("""CREATE TABLE IF NOT EXISTS amtsgerichte (
                amtsgericht TEXT,
                strasse TEXT,
                plz TEXT,
                ort TEXT
                 )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='amtsgerichte'").fetchone() is not None:
    print("Die amtsgerichte Tabelle wurde erfolgreich erstellt.")
else:
    print("Die amtsgerichte Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Grunderwerbssteuer
c.execute("""CREATE TABLE IF NOT EXISTS grunderwerbssteuersaetze (
                bundesland TEXT,
                steuersatz REAL
                 )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grunderwerbssteuersaetze'").fetchone() is not None:
    print("Die grunderwerbssteuersaetze Tabelle wurde erfolgreich erstellt.")
else:
    print("Die grunderwerbssteuersaetze Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Schätzwerte
c.execute("""CREATE TABLE IF NOT EXISTS schaetzwerte (
                aktenzeichen TEXT,
                immowelt_objekt REAL,
                immoscout_objekt REAL,
                immoscout_miete REAL,
                bodenwert REAL,
                sachwert REAL,
                ertragswert REAL,
                verkehrswert REAL,
                vergleichswert REAL,
                marktuebliche_monatsmiete REAL
                 )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schaetzwerte'").fetchone() is not None:
    print("Die schaetzwerte Tabelle wurde erfolgreich erstellt.")
else:
    print("Die schaetzwerte Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Allgemeines
c.execute("""CREATE TABLE IF NOT EXISTS allgemeines (
                aktenzeichen TEXT,
                grundbuch_abteilung2 TEXT,
                baulasten TEXT,
                nutzungsverhältnisse TEXT,
                erschliessung TEXT,
                energieausweis TEXT,
                denkmalschutz TEXT
                 )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schaetzwerte'").fetchone() is not None:
    print("Die schaetzwerte Tabelle wurde erfolgreich erstellt.")
else:
    print("Die schaetzwerte Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Dokumente
c.execute("""CREATE TABLE IF NOT EXISTS dokumente (
                aktenzeichen TEXT,
                gutachten BLOB,
                expose BLOB
                 )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dokumente'").fetchone() is not None:
    print("Die dokumente Tabelle wurde erfolgreich erstellt.")
else:
    print("Die dokumente Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Dokumente
c.execute("""CREATE TABLE IF NOT EXISTS abschluss (
                aktenzeichen TEXT,
                termin_aufgehoben TEXT
                 )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='abschluss'").fetchone() is not None:
    print("Die abschluss Tabelle wurde erfolgreich erstellt.")
else:
    print("Die abschluss Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())
    
# Dokumente
c.execute("""CREATE TABLE IF NOT EXISTS erbbaurecht (
                aktenzeichen TEXT,
                besteht_erbbaurecht TEXT,
                ablaufdatum DATE,
                erbbauzins REAL,
                entschaedigung_prozent REAL
                 )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='erbbaurecht'").fetchone() is not None:
    print("Die erbbaurecht Tabelle wurde erfolgreich erstellt.")
else:
    print("Die erbbaurecht Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())