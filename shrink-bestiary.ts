import fs from "fs";
import path from "path";

const filePath = path.resolve("./src/util/bestiaryShort.json");

// Fields to remove from each entry
const fieldsToRemove: string[] = [
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
  "hasToken",
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
  "familiar"
  // "skill",
  // "trait",
  // "action",
  // "spellcasting",
  // "bonus",
  // "reaction",
  // "legendary",
  // "immune",
  // "conditionImmune",
  // "resist",
  // "passive",
  // "languages",
  // "vulnerable",
  // "alignment",
  // "senses",
];

const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
const filtered = data.filter((entry: Record<string, unknown>) => !("reprintedAs" in entry));

const updated = filtered.map((entry) => {
  const cleaned = { ...entry };
  for (const field of fieldsToRemove) {
    delete cleaned[field];
  }
  if (
    typeof cleaned.cr === "object" &&
    cleaned.cr !== null &&
    "cr" in cleaned.cr
  ) {
    cleaned.cr = cleaned.cr.cr;
  }
  return cleaned;
});

fs.writeFileSync(filePath, JSON.stringify(updated, null, 2), "utf8");

console.log(
  `Removed fields [${fieldsToRemove.join(", ")}] from ${updated.length} entries`,
);
