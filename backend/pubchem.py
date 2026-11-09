
import ssl
import certifi
import json
import urllib.parse
import urllib.request
import urllib.error


def search_pubchem(compound_name):

    encoded_name = urllib.parse.quote(compound_name)

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
        f"{encoded_name}/property/"
        "MolecularFormula,MolecularWeight,CanonicalSMILES,"
        "IsomericSMILES,InChIKey/JSON"
    )

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ChemGuardAI/1.0"}
        )

        ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )

        with urllib.request.urlopen(
            request,
            timeout=20,
            context=ssl_context
        ) as response:

            data = json.loads(response.read().decode("utf-8"))

        properties = data["PropertyTable"]["Properties"]

        if not properties:
            return {"error": "No compound record found"}

        return properties[0]

    except urllib.error.HTTPError as error:
        if error.code == 404:
            return {"error": "Compound not found in PubChem"}

        return {"error": f"PubChem HTTP error: {error.code}"}

    except Exception as error:
        return {"error": str(error)}


if __name__ == "__main__":

    result = search_pubchem("Diclofenac")

    print("\n===== PUBCHEM RESULTS =====")

    if "error" in result:
        print(result["error"])
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
