import streamlit as st
st.set_page_config(page_title="Immobilienbewertung", page_icon="logo-thiasos.png")

st.header("Letzte Änderungen")

st.subheader("Version 0.13 von 08. Juni 2023")
st.text("Änderungen:")
st.caption("* Neues Input-Feld: Eigene Einschätzung, Fazit im Tab Beschreibung -> Objektbeschreibung.")
st.caption("* kleinere Code-Überarbeitungen")

st.subheader("Version 0.12 von 07. Juni 2023")
st.text("Änderungen:")
st.caption("* Berechnung der Zinskosten für den Zeitraum nach Zuschlag bis Verteilungstermin korrigiert. Vom Gebotspreis ist die Sicherheitsleistung (10% vom Verkehrswert) abzuziehen")

st.subheader("Version 0.11 vom 06. Juni 2023")
st.text("Änderungen:")
st.caption("* Fehlerbehandlung beim Lesen der json-Daten von OpenStreetMap")

st.subheader("Version 0.1 vom 04. Juni 2023")
st.text("Änderungen:")
st.caption("* Download und Upload-Möglichkeit entfernt, da dieser bei Github nicht funktioniert.")
st.caption("* Zinskosten, die durch den Zuschlag bis zum Verteilungstermin entstehen, im Tab 'Erweiterte Anschaffungskosten' hinzugefügt.")
st.caption("* Diese Seite hinzugefügt.")