#!/usr/bin/env python3
"""Rebuild derived tables reported in the manuscript from displayed set-level values.

This script is intentionally bounded. It does NOT rerun the JRC CMB fits or the EPA EVLS
whole-profile experiment. It reconstructs the publication tables and the 30 lower-mean-
reduced-chi-square comparisons from the displayed 12-set summary so the derived
headline arithmetic remains transparent and checkable.
"""
from pathlib import Path
import itertools
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "derived_data"
OUT.mkdir(parents=True, exist_ok=True)

rows = [
    ("W3-V2",3.25,0.0508,0.9961,85.4,0,7.92),("W3-V3",14.56,0.0684,0.9953,85.1,2,7.95),
    ("W3-V4",18.79,0.0711,0.9939,83.5,0,9.74),("W4-V2",2.27,0.0528,0.9963,84.1,0,7.63),
    ("W4-V3",14.03,0.0747,0.9953,85.2,0,7.69),("W4-V4",19.51,0.0804,0.9938,84.1,0,9.56),
    ("W5-V2",4.52,0.0517,0.9964,84.3,0,7.49),("W5-V3",14.83,0.0741,0.9953,85.2,0,7.11),
    ("W5-V4",19.78,0.0821,0.9935,83.8,0,9.18),("W6-V2",4.76,0.0512,0.9965,82.7,0,8.71),
    ("W6-V3",17.01,0.0731,0.9952,84.3,0,8.11),("W6-V4",24.24,0.0809,0.9935,83.0,0,10.65),
]
landscape = pd.DataFrame(rows, columns=[
    "profile_set","EL1_percent_reference_mass","mean_reduced_chi2","median_R2",
    "all_three_pass_percent","nonconverged_samples","IL1_percent_mean_observed_PM"])
landscape.to_csv(OUT/"jrc_12set_landscape.csv", index=False, lineterminator="\n")

reference = pd.DataFrame([
    ("BioB","Biomass/wood burning",4.33),("SO4","Ammonium sulfate",7.12),
    ("NO3","Ammonium nitrate",12.69),("DUST","Crustal dust",4.01),
    ("ROAD","Road dust",2.68),("SALT","Sea salt",0.52),
    ("TRA","Vehicle exhaust",6.63),("INDU","Industrial/point sources",5.11),
], columns=["reference_key","source_category","published_mean_ug_m3"])
reference.to_csv(OUT/"jrc_campaign_point_reference.csv", index=False, lineterminator="\n")

lk=landscape.set_index("profile_set")
edges=[]; n=0
for veh in ["V2","V3","V4"]:
    for wa,wb in itertools.combinations(["W3","W4","W5","W6"],2):
        n+=1; edges.append((f"E{n:02d}","Wood",f"{wa}-{veh}",f"{wb}-{veh}","38 species",f"vehicle={veh}; other six source categories fixed"))
for wood in ["W3","W4","W5","W6"]:
    for va,vb in itertools.combinations(["V2","V3","V4"],2):
        n+=1; edges.append((f"E{n:02d}","Vehicle",f"{wood}-{va}",f"{wood}-{vb}","38 species",f"wood={wood}; other six source categories fixed"))

out=[]
for edge_id,fam,a,b,common,fixed in edges:
    ca,cb=float(lk.loc[a,"mean_reduced_chi2"]),float(lk.loc[b,"mean_reduced_chi2"])
    ea,eb=float(lk.loc[a,"EL1_percent_reference_mass"]),float(lk.loc[b,"EL1_percent_reference_mass"])
    fit=a if ca<cb else b; ref=a if ea<eb else b
    fit_e=ea if fit==a else eb
    out.append({
        "edge_id":edge_id,"source_family":fam,"profile_a_id":a,"profile_b_id":b,
        "common_species_basis":common,"fixed_other_profiles":fixed,
        "selector_name":"lower mean reduced chi-square","selector_value_a_published":ca,
        "selector_value_b_published":cb,"fit_favored_endpoint":fit,
        "reference_status":"published campaign-level point reference",
        "reference_distance_a_EL1_percent":ea,"reference_distance_b_EL1_percent":eb,
        "reference_closer_endpoint":ref,"discordance":fit!=ref,
        "selection_regret_pp_from_published_values":fit_e-min(ea,eb),
        "mean_reduced_chi2_gap_from_published_values":abs(ca-cb),
        "reconstruction_status":"derived from displayed set-level values; canonical unrounded comparison ledger not present in this release",
    })
edge_df=pd.DataFrame(out)
edge_df.to_csv(OUT/"jrc_profile_choice_edges_reconstructed.csv", index=False, lineterminator="\n")

assert len(edge_df)==30 and int(edge_df.discordance.sum())==9
assert abs(reference.published_mean_ug_m3.sum()-43.09)<1e-12
print("PASS: publication-derived data rebuilt; 30 edges and 9 lower-chi2 discordances reproduced.")
