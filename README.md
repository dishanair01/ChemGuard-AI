# ChemGuard AI — enhanced research website prototype

## Open
Open `index.html` in a modern browser. It runs locally and does not require installation.

## Included
- Responsive research-platform interface
- Searchable starter catalogue of 24 compounds / environmental contaminant comparators
- Compound research profiles with chemical identity, SMILES text, environmental occurrence, fate, biodegradation, aquatic effects, wastewater treatment and MOF research sections
- Evidence-quality checklist and clear data-gap labels
- Research-source registry and links to PHARMS-UBA, EPA CompTox/ECOTOX, RISMEAU, SIPIBEL and Canadian wastewater monitoring data
- MOF research section explaining the need for compound-specific aqueous adsorption evidence
- Public medicine-waste education page

## Scientific limitations
This is an enhanced front-end prototype, not yet a connected live database or validated AI prediction service. The starter compound records are discovery/navigation records. Their evidence sections deliberately identify where study-level extraction is still required. No numerical environmental concentration, ecotoxicity score, wastewater removal percentage, MOF capacity or model prediction is invented.

The SMILES strings are seed metadata and should be checked against authoritative chemical registries before RDKit processing. A real release should use stable identifiers (e.g. PubChem CID, CAS where verified, InChIKey), record provenance, and store study-level evidence with units and uncertainty.

## Next engineering stage
1. Download and audit source datasets.
2. Build a normalized evidence schema and source provenance.
3. Verify compound identity and structures.
4. Import measured records while preserving matrix, geography, date, detection limits, units, method and publication.
5. Build endpoint-specific models only where the data support valid training and external/scaffold/study-level validation.
6. Connect a Python API and database to this frontend.
7. Implement compound-specific MOF adsorption analysis from suitable aqueous adsorption datasets.
