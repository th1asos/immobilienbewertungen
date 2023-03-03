import requests
from lxml import html

def mietpreisspiegel_qm(plz, qm):
    preis_tmp=1 # Default-Wert
    url = 'https://www.miet-check.de/mietpreis-plz/' + plz
    response = requests.get(url)
    tree = html.fromstring(response.content)

    table = tree.xpath('//h2[contains(text(), "Mietpreise pro m")]/following-sibling::div[1]/table')[0]
    rows = table.xpath('.//tr')
  
    for row in rows:
        # Finde alle Zellen der Zeile
        cells = row.xpath('.//td')
        # Wenn es mehr als eine Zelle gibt, ist es eine Zeile mit Daten
        if len(cells) > 1:
            # Hole den Wert der letzten Zelle
            mietspiegel_preis = cells[-1].text_content().replace('€', '')
            mietspiegel_preis = float(mietspiegel_preis.replace(',', '.'))
            mietspiegel_qm = cells[0].text_content().replace('m²', '')
            mietspiegel_qm = mietspiegel_qm.replace(' ','')
            
            if '-' in mietspiegel_qm:
                min, max = mietspiegel_qm.split('-')
                min = int(min)
                max = int(max)
            elif '>=' in mietspiegel_qm:
                min = int(mietspiegel_qm.split('>=')[1])
                max = float('inf')
           
            if qm <= max  and mietspiegel_preis > 0:
                return mietspiegel_preis
            elif mietspiegel_preis > 0:
                preis_tmp = mietspiegel_preis
         
    return preis_tmp # gibt den letzten gefundenen Preis zurück
         
    return mietspiegel_preis

def mietpreisspiegel_zimmer(plz, zimmer):
    preis_tmp = 0
    preis = 0
    if zimmer == None:
        zimmer = 0
    zimmer = float(zimmer)
    
    url = 'https://www.miet-check.de/mietpreis-plz/' + plz
    response = requests.get(url)
    tree = html.fromstring(response.content)

    table = tree.xpath('//h2[contains(text(), "Mietpreise pro Zimmeranzah")]/following-sibling::div[1]/table')[0]
    rows = table.xpath('.//tr')

    for row in rows:
        # Finde alle Zellen der Zeile
        cells = row.xpath('.//td')
        # Wenn es mehr als eine Zelle gibt, ist es eine Zeile mit Daten
        if len(cells) > 1:
            # Hole den Wert der letzten Zelle
            mietspiegel_preis = cells[-1].text_content().replace('€', '')
            mietspiegel_preis = float(mietspiegel_preis.replace(',', '.'))
            mietspiegel_zimmer = cells[0].text_content()
            mietspiegel_zimmer = int(mietspiegel_zimmer.split()[0])

            if zimmer <= mietspiegel_zimmer and mietspiegel_preis > 0:
                return mietspiegel_preis
            elif mietspiegel_preis > 0:
                preis_tmp = mietspiegel_preis
         
    return preis_tmp

def mietspiegelpreis(*, plz, qm, zimmer): # erwartet Keywords
    preis_qm=mietpreisspiegel_qm(plz, qm)
    preis_zimmer=mietpreisspiegel_zimmer(plz, zimmer)
    
    if preis_qm > 0 and preis_zimmer > 0:
        return (preis_qm + preis_zimmer)/2
    elif preis_qm > 0:
        return preis_qm
    elif preis_zimmer > 0:
        return preis_zimmer
    else:
        return None