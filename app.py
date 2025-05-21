from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route("/rzp", methods=["GET"])
def rzp_lookup():
    ico = request.args.get("ico")
    if not ico:
        return jsonify({"error": "Chybí parametr IČO"}), 400

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
        return jsonify({"error": "Chyba při dotazu na RŽP"}), 500

    tree = ET.fromstring(response.content)

    try:
        name = tree.find('.//nazev_osoby').text
        ico = tree.find('.//ico').text
        status = tree.find('.//stav').text
        zivnosti = [elem.text for elem in tree.findall('.//nazev_oboru_cinnosti')]
    except:
        return jsonify({"error": "Nepodařilo se načíst data"}), 500

    return jsonify({
        "nazev": name,
        "ico": ico,
        "stav": status,
        "zivnosti": zivnosti
    })

if __name__ == "__main__":
    app.run(debug=True)
