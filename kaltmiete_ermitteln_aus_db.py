# import sqlite3
# 
# # Verbindung zur Datenbank herstellen
# conn = sqlite3.connect('immo.db')
# 
# # Cursor erstellen
# c = conn.cursor()
# 
# # Abfrage erstellen
# c.execute("SELECT object_id, ausstattung_beschreibung FROM immo_data WHERE ausstattung_beschreibung IS NOT NULL")
# 
# # Ergebnisse auslesen
# rows = c.fetchall()
# 
# # Alle Ergebnisse durchgehen
# for row in rows:
#     # Prüfen, ob die Spalte leer ist
#     if row[1] != '':
#         # Prüfen, ob der Begriff "miete" oder "Miete" enthalten ist
#         if "kaltmiete" in row[1] or "Kaltmiete" in row[1]:
#             # Preis auslesen
#             words = row[1].split()
#             for word in words:
#                 # Prüfen, ob es sich um eine Zahl handelt
#                 if word.replace('.', '', 1).isdigit():
#                     # Preis ausgeben
#                     print("Object-ID: " + str(row[0]) + " | Preis: " + word)
# 
# # Verbindung schließen
# conn.close()

import sqlite3
import re

# Verbindung zur Datenbank herstellen
conn = sqlite3.connect('immo.db')
cursor = conn.cursor()

# Daten aus der Tabelle immo_data abrufen
cursor.execute("SELECT ausstattung_beschreibung, object_id FROM immo_data")
data = cursor.fetchall()

# Über die Daten iterieren und nach Kaltmiete und Preis suchen
for row in data:
    ausstattung_beschreibung = row[0]
    object_id = row[1]
    
    if ausstattung_beschreibung:
        # Verwende reguläre Ausdrücke, um nach Kaltmiete und Preis zu suchen
        match = re.search(r'(?:kaltmiete.*?)(\d{1,}(?:[.,]\d{3})*(?:[.,](?:\d{2}|\d{1,2})(?!\d))?)', ausstattung_beschreibung, re.IGNORECASE) 
        #match = re.search(r'(?:(?:kaltmiete|jahresnettokaltmiete|jahresmiete|nettomiete|nettojahresmiete|jahresnettomiete|jahreskaltmiete|nettokaltmiete|nettojahreskaltmiete).*?)(\d{1,}(?:[.,]\d{3})*(?:[.,](?:\d{2}|\d{1,2})(?!\d))?)', ausstattung_beschreibung, re.IGNORECASE)
        #match = re.search(r'(?:(?:kaltmiete|jahresnettokaltmiete)\s)(\d{1,}(?:[.,]\d{3})*(?:[.,](?:\d{2}|\d{1,2})(?!\d))?)(?=\s?[\.\?!])', ausstattung_beschreibung, re.IGNORECASE) 
        if match:
            price = match.group(1)
            print(f'object_id: {object_id}, Kaltmiete: {price}')

# Verbindung zur Datenbank schließen
conn.close()

# conn.close()