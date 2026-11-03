import csv
from pathlib import Path
import json
import os

#['AATM', 'ABH', 'AI', 'AitFR-DN', 'AitFR-FCD', 'AitFR-ISF', 'AitFR-THP', 'AU', 'AUD', 'AWM', 'BAM', 'BGDIA', 'BGG', 'BMT', 'CM', 'CoA', 'CoS', 'CRCotN', 'DC', 'DIP', 'DitLCoT', 'DMG', 'DoD', 'DoSI', 'DrDe-BD', 'DSotDQ', 'EFA', 'EGW', 'ERLW', 'ESK', 'FRAiF', 'FTD', 'GGR', 'GoS', 'GotSF', 'HAT-TG', 'HftT', 'HoL', 'HotB', 'HotDQ', 'IDRotF', 'IMR', 'JttRC', 'KftGV', 'KKW', 'LFL', 'LLK', 'LMoP', 'LoX', 'LR', 'LRDT', 'MaBJoV', 'MCV1SC', 'MCV2DC', 'MCV3MC', 'MCV4EC', 'MFF', 'MGELFT', 'MisMV1', 'MM', 'MOT', 'MPMM', 'MPP', 'MTF', 'NF', 'NRH-ASS', 'NRH-AT', 'NRH-AVitW', 'NRH-AWoL', 'NRH-CoI', 'NRH-TCMC', 'OotA', 'OoW', 'PaBTSO', 'PHB', 'PL', 'PotA', 'PSA', 'PSD', 'PSI', 'PSK', 'PSX', 'PSZ', 'QftIS', 'RHW', 'RMBRE', 'RoT', 'RtG', 'RWG', 'SADS', 'SCC', 'SDW', 'SKT', 'SLW', 'TCE', 'TftYP', 'ToA', 'ToFW', 'TTP', 'VD', 'VEoR', 'VGM', 'VRGR', 'WBtW', 'WDH', 'WDMM', 'WttHC', 'XDMG', 'XGE', 'XMM', 'XPHB']

bestiary_dir = Path(__file__).resolve().parent/"data"

fields_to_remove = {
    "page",
    "environment",
    "traitTags",
    "senseTags",
    "actionTags",
    "languageTags",
    "damageTags",
    "miscTags",
    "spellcastingTags",
    "attachedItems",
    "damageTagsSpell",
    "savingThrowForced",
    "conditionInflict",
    "conditionInflictSpell",
    "savingThrowForcedSpell",
    "legendaryGroup",
    "referenceSources",
    "isNamedCreature",
    "isNpc",
    "pbNote",
    "summonedBySpell",
    "summonedBySpellLevel",
    "summonedByClass",
    "hasFluff",
    "soundClip",
    "treasure",
    "_mod",
    "hasFluffImages",
    "_versions",
    "foundryTokenScale",
    "srd52",
    "variant",
    "familiar",
}


def shrink_monster(monster):
    cleaned = {
        field: value
        for field, value in monster.items()
        if field not in fields_to_remove
    }

    if isinstance(cleaned.get("cr"), dict) and "cr" in cleaned["cr"]:
        cleaned["cr"] = cleaned["cr"]["cr"]

    return cleaned


def copy_monster(monster, monsters_by_key):
    copy = monster.get("_copy")
    if not copy:
        return {
            key: value
            for key, value in monster.items()
            if key not in {"_copy", "_mod"}
        }

    base_key = (copy["name"], copy["source"])
    template = monsters_by_key.get(base_key)
    if template is None:
        raise ValueError(
            f'Unable to resolve copy base "{copy["name"]}" '
            f'from source "{copy["source"]}"'
        )

    copied_monster = copy_monster(template, monsters_by_key)
    copied_monster.update(
        {
            key: value
            for key, value in monster.items()
            if key not in {"_copy", "_mod"}
        }
    )
    return copied_monster


output_path = Path(__file__).resolve().parent / "bestiary.csv"
rows = []
monsters = []
sources = []
for entry in os.scandir(bestiary_dir):
    if entry.is_file() and entry.name.__contains__('bestiary-') and not entry.name.__contains__('fluff'):  # check if it's a file
        with open(entry.path, "r") as source_file:
            data = json.load(source_file)
            sources.append(data["monster"][0]["source"])
            for monster in data["monster"]:
                monsters.append(shrink_monster(monster))
            
# print (sources)

monsters_by_key = {
    (monster["name"], monster["source"]): monster
    for monster in monsters
}

print("Resolve copies")

for monster in monsters:
    if "reprintedAs" in monster:
        continue

    monster = copy_monster(monster, monsters_by_key)
    slug = monster["source"]+"-" + \
        "-".join(monster["name"].lower().split())
    cr = monster.get("cr", "unknown")
    rows.append(
        [slug, monster["name"], monster["source"], cr,
         json.dumps(monster, ensure_ascii=False)])

print(f"Write to {output_path}")

with output_path.open("w", newline="", encoding="utf-8") as bestiary_output_file:
    csvwriter = csv.writer(bestiary_output_file)
    csvwriter.writerows(rows)

print(f"Wrote {output_path}")
