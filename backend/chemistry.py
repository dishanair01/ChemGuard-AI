
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, Crippen, Lipinski


def analyse_compound(smiles):

    # Convert SMILES into a molecular structure
    molecule = Chem.MolFromSmiles(smiles)

    if molecule is None:
        return {"error": "Invalid SMILES structure"}

    # Calculate molecular properties
    results = {
        "canonical_smiles": Chem.MolToSmiles(molecule),
        "molecular_formula": rdMolDescriptors.CalcMolFormula(molecule),
        "molecular_weight": round(Descriptors.MolWt(molecule), 3),
        "logP": round(Crippen.MolLogP(molecule), 3),
        "tpsa": round(Descriptors.TPSA(molecule), 3),
        "hydrogen_bond_donors": Lipinski.NumHDonors(molecule),
        "hydrogen_bond_acceptors": Lipinski.NumHAcceptors(molecule),
        "rotatable_bonds": rdMolDescriptors.CalcNumRotatableBonds(molecule),
        "ring_count": rdMolDescriptors.CalcNumRings(molecule),
        "heavy_atom_count": molecule.GetNumHeavyAtoms(),
        "fraction_csp3": round(
            rdMolDescriptors.CalcFractionCSP3(molecule), 3
        )
    }

    return results


if __name__ == "__main__":

    diclofenac_smiles = "O=C(O)Cc1ccccc1Nc1c(Cl)cccc1Cl"

    result = analyse_compound(diclofenac_smiles)

    print("\n===== CHEMGUARD AI =====")
    print("MOLECULAR PROPERTY ANALYSIS")
    print("========================")

    for property_name, value in result.items():
        print(f"{property_name}: {value}")
