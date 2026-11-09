
from pubchem import search_pubchem
from chemistry import analyse_compound


def get_compound_profile(compound_name):

    # Step 1: Retrieve compound from PubChem
    pubchem_data = search_pubchem(compound_name)

    if "error" in pubchem_data:
        return {"error": pubchem_data["error"]}

    # Step 2: Retrieve SMILES
    smiles = (
        pubchem_data.get("ConnectivitySMILES")
        or pubchem_data.get("CanonicalSMILES")
        or pubchem_data.get("SMILES")
        or pubchem_data.get("IsomericSMILES")
    )

    if not smiles:
        return {"error": "No usable SMILES structure found"}

    # Step 3: Calculate descriptors using RDKit
    molecular_data = analyse_compound(smiles)

    if "error" in molecular_data:
        return {"error": molecular_data["error"]}

    # Step 4: Combine both results
    return {
        "compound_name": compound_name,
        "pubchem_cid": pubchem_data.get("CID"),
        "inchikey": pubchem_data.get("InChIKey"),
        "molecular_formula": pubchem_data.get("MolecularFormula"),
        "pubchem_molecular_weight": pubchem_data.get("MolecularWeight"),
        "smiles": smiles,
        "molecular_properties": molecular_data
    }


if __name__ == "__main__":

    name = input("Enter pharmaceutical compound name: ")

    profile = get_compound_profile(name)

    print("\n========== CHEMGUARD AI ==========")
    print("CHEMICAL INTELLIGENCE PROFILE")
    print("=================================")

    if "error" in profile:
        print("Error:", profile["error"])
    else:
        print("\nCompound:", profile["compound_name"])
        print("PubChem CID:", profile["pubchem_cid"])
        print("InChIKey:", profile["inchikey"])
        print("Formula:", profile["molecular_formula"])
        print("SMILES:", profile["smiles"])

        print("\n--- RDKit Molecular Properties ---")

        for key, value in profile["molecular_properties"].items():
            print(f"{key}: {value}")
