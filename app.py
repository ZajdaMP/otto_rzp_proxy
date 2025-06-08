import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def rzp_lookup(ico):
    soap_request = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <zr:GetZaznamPodleIC xmlns:zr="http://zr.ws.zr.rzp.mfcr.cz">
              <zr:ico>{ico}</zr:ico>
            </zr:GetZaznamPodleIC>
          </soap:Body>
        </soap:Envelope>
    """

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://zr.ws.zr.rzp.mfcr.cz/GetZaznamPodleIC"
    }

    response = requests.post(
        "https://www.rzp.cz/portal/swsrvzs/ws_zr_soap.asmx",
        data=soap_request.encode("utf-8"),
        headers=headers
    )

    if response.status_code != 200:
        return {"error": "Chyba při dotazu na RŽP"}

    tree = ET.fromstring(response.content)

    try:
        name = tree.find('.//nazev_osoby').text
        ico = tree.find('.//ico').text
        status = tree.find('.//stav').text
        zivnosti = [elem.text for elem in tree.findall('.//nazev_oboru_cinnosti')]
    except:
        return {"error": "Nepodařilo se načíst data"}

    return {
        "nazev": name,
        "ico": ico,
        "stav": status,
        "zivnosti": zivnosti
    }


def search_by_name(jmeno, prijmeni):
    params = {
        "zn_jmeno": jmeno,
        "zn_prijmeni": prijmeni,
        "zn_subjekt": "F"
    }

    res = requests.get("https://www.rzp.cz/cgi-bin/neplatne/licence.cgi", params=params)
    soup = BeautifulSoup(res.content, "html.parser")

    results = []
    for row in soup.select("table tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 5:
            results.append({
                "jmeno": cols[0].text.strip(),
                "ico": cols[1].text.strip(),
                "mesto": cols[3].text.strip()
            })

    return results


def isir_lookup(ico=None, prijmeni=None):
    if not ico and not prijmeni:
        return {"error": "Zadejte IČO nebo příjmení"}

    url = "https://isir.justice.cz/isir/ueu/vysledky_lustrace_osoba.do"
    data = {
        "rcSubjektu": "",
        "nazevSubjektu": prijmeni if not ico else "",
        "icoSubjektu": ico,
        "cisloSenatu": "",
        "idOsobyKategorie": "0",
        "idStavRizeni": "0"
    }

    res = requests.post(url, data=data)
    soup = BeautifulSoup(res.content, "html.parser")

    rows = soup.select("table.vysledky tr")[1:]
    results = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            results.append({
                "jmeno": cols[0].text.strip(),
                "ico": cols[1].text.strip(),
                "soud": cols[2].text.strip(),
                "stav": cols[3].text.strip(),
                "datum": cols[4].text.strip()
            })

    return results


# 💡 Hlavní vstup pro Codex:
def run(input_data: dict = None):
    if input_data is None:
        input_data = {}

    source = input_data.get("source", "rzp")
    ico = input_data.get("ico", "").strip()
    jmeno = input_data.get("jmeno", "").strip()
    prijmeni = input_data.get("prijmeni", "").strip()

    if source == "rzp":
        return rzp_lookup(ico)
    elif source == "search":
        return search_by_name(jmeno, prijmeni)
    elif source == "isir":
        return isir_lookup(ico, prijmeni)
    else:
        return {"error": f"Neznámý zdroj: {source}"}
