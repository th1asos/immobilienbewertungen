import streamlit as st
st.set_page_config(page_title="Immobilienbewertung", page_icon="logo-thiasos.png")

st.header("Letzte Änderungen")

st.subheader("Version 0.17 von 14. Juni 2023")
st.caption("* Kosten für sanierungspflichtige Tätigkeiten können nun gespeichert werden in Beschreibung -> Sanierungspflicht.")

st.subheader("Version 0.16 von 12. Juni 2023")
st.caption("* Im Tab Basis wird nun der Wertermittlungsstichtag (Gutachten) abgefragt.")

st.subheader("Version 0.15 von 10. Juni 2023")
st.caption("* Es wird nun nach Eingabe einer Mindestrendite ein maximaler Gebotspreis vorgeschlagen")
st.caption("* Es können nun im Bereich Beschreibung -> Bewertung eigene Einschätzungen hinterlegt werden")

st.subheader("Version 0.141 von 09. Juni 2023")
st.caption("* Bei der Auswahl des Objekts wird zusätzlich noch der Ort angezeigt.")

st.subheader("Version 0.14 von 09. Juni 2023")
st.caption("* Bei der Auswahl eines Objekts wird nun auch die Straße in der Auswahl angezeigt. Dies erleichtert das Finden des gesuchten Objekts erheblich.")

st.subheader("Version 0.13 von 08. Juni 2023")
st.caption("* Neues Input-Feld: Eigene Einschätzung, Fazit im Tab Beschreibung -> Objektbeschreibung.")
st.caption("* kleinere Code-Überarbeitungen")

st.subheader("Version 0.12 von 07. Juni 2023")
st.caption("* Berechnung der Zinskosten für den Zeitraum nach Zuschlag bis Verteilungstermin korrigiert. Vom Gebotspreis ist die Sicherheitsleistung (10% vom Verkehrswert) abzuziehen")

st.subheader("Version 0.11 vom 06. Juni 2023")
st.caption("* Fehlerbehandlung beim Lesen der json-Daten von OpenStreetMap")

st.subheader("Version 0.1 vom 04. Juni 2023")
st.caption("* Download und Upload-Möglichkeit entfernt, da dieser bei Github nicht funktioniert.")
st.caption("* Zinskosten, die durch den Zuschlag bis zum Verteilungstermin entstehen, im Tab 'Erweiterte Anschaffungskosten' hinzugefügt.")
st.caption("* Diese Seite hinzugefügt.")