import sqlite3

# Erstellen der Datenbank
try:
    conn = sqlite3.connect('immo.db')
    print("Datenbank erfolgreich erstellt!")
except:
    print("Fehler beim Erstellen der Datenbank!")

# Erstelle einen Cursor
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS immo_data (
            object_id TEXT PRIMARY KEY,
            letztes_update DATE,
            anbieter_id TEXT,
            strasse TEXT,
            plz TEXT,
            stadt TEXT,
            bundesland TEXT,
            staat TEXT,
            object_typ TEXT,
            object_art TEXT,
            baujahr TEXT,
            qm REAL,
            raeume TEXT,
            balkon TEXT,
            heizungsart TEXT,
            kueche TEXT,
            garten TEXT,
            ausstattung TEXT,
            baualterkategorie TEXT,
            zustand TEXT,
            effizienzklasse TEXT,
            endenergieverbrauch REAL,
            befeuerungsart TEXT,
            baujahr_heizung DATE,
            titel TEXT,
            ausstattung_beschreibung TEXT,
            umgebungsbeschreibung TEXT,
            sonstige_beschreibung TEXT,
            objekt_beschreibung TEXT,
            transaktionsart TEXT,
            preis REAL,
            waehrung TEXT,
            courtage REAL,
             kaltmiete REAL,
             vorauszahlende_betriebskosten REAL,
             vorauszahlende_heizkosten REAL,
             hausgeld REAL,
             ruecklagen REAL,
             vermietet_seit DATE,
             letzte_mieterhöhung DATE,
             wertgutachtenkosten REAL,
             renovierungskosten REAL,
             umbaukosten REAL,
             verwaltungskosten_pro_jahr REAL,
             instandhaltungskosten_pro_jahr_qm REAL,
             mietspiegelmiete_pro_qm REAL,
             eigenkapital REAL,
             eigenkapitalrendite REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='immo_data'").fetchone() is not None:
    print("Die immo_data Tabelle wurde erfolgreich erstellt.")
else:
    print("Die immo_data Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())

# Erstellen der Datenbank
try:
    conn = sqlite3.connect('immo.db')
    print("Datenbank erfolgreich erstellt!")
except:
    print("Fehler beim Erstellen der Datenbank!")

# Erstelle einen Cursor
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS immo_data_kalk (
            object_id TEXT PRIMARY KEY,
            letztes_update DATE,
            strasse TEXT,
            plz TEXT,
            stadt TEXT,
            bundesland TEXT,
            staat TEXT,
            object_typ TEXT,
            object_art TEXT,
            baujahr TEXT,
            qm REAL,
            raeume TEXT,
            balkon TEXT,
            heizungsart TEXT,
            kueche TEXT,
            garten TEXT,
            ausstattung TEXT,
            baualterkategorie TEXT,
            zustand TEXT,
            effizienzklasse TEXT,
            endenergieverbrauch REAL,
            befeuerungsart TEXT,
            baujahr_heizung DATE,
            titel TEXT,
            ausstattung_beschreibung TEXT,
            umgebungsbeschreibung TEXT,
            sonstige_beschreibung TEXT,
            objekt_beschreibung TEXT,
            transaktionsart TEXT,
            preis REAL,
            waehrung TEXT,
            courtage REAL,
             kaltmiete REAL,
             betriebskosten REAL,
             heizkosten REAL,
             vermietet_seit DATE,
             letzte_mieterhöhung DATE,
             wertgutachtenkosten REAL,
             renovierungskosten REAL,
             umbaukosten REAL,
             verwaltungskosten_pro_jahr REAL,
             instandhaltungskosten_pro_jahr_qm REAL,
             mietspiegelmiete_pro_qm REAL,
             eigenkapital REAL,
             eigenkapitalrendite REAL
            )""")

if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='immo_data_kalk'").fetchone() is not None:
    print("Die immo_data Tabelle wurde erfolgreich erstellt.")
else:
    print("Die immo_data Tabelle konnte nicht erstellt werden. Fehlermeldung: " + sqlite3.errmsg())