---
name: infiniteleverage-whitelabel
description: Clone and rebrand the Infinite Leverage framework under a partner's own brand. Partner access required.
---

# Infinite Leverage — Whitelabel Setup

## Step 1 — Verify partner access

```bash
if ! gh repo view talentedgeai/infiniteleverage-partner-portal --json name > /dev/null 2>&1; then
  echo "❌ Partner access required."
  echo "   Contact partners@infiniteleverage.com to apply."
  exit 1
fi
echo "✓ Partner access confirmed"
```

If the check fails, stop here. Do not proceed.

---

## Step 2 — Collect brand details

Ask the operator for the following. Do not guess defaults.

| Field | Example |
|---|---|
| Brand name (full) | `Acme AI` |
| Brand slug (lowercase, no spaces) | `acme-ai` |
| GitHub org or username | `acmecorp` |
| Plugin repo name | `acme-ai-plugin` |
| Template repo name | `acme-ai-8-agents-template` |
| Partner portal repo name | `acme-ai-partner-portal` |
| Contact email (for partner access messages) | `partners@acmecorp.com` |
| Primary brand colour (hex) | `#0057FF` |

Save these as shell variables for use in later steps:

```bash
BRAND_NAME="Acme AI"
BRAND_SLUG="acme-ai"
GH_ORG="acmecorp"
PLUGIN_REPO="acme-ai-plugin"
TEMPLATE_REPO="acme-ai-8-agents-template"
PORTAL_REPO="acme-ai-partner-portal"
PARTNER_EMAIL="partners@acmecorp.com"
```

---

## Step 3 — Clone the canonical template

```bash
gh repo clone talentedgeai/infiniteleverage-8-agents-template /tmp/il-whitelabel
cd /tmp/il-whitelabel
```

---

## Step 4 — Rebrand all references

Run find-and-replace across all text files. This covers agent files, skill files, CLAUDE.md, scripts, and docs.

```bash
# Files to rebrand (text only — skip zips and binaries)
find /tmp/il-whitelabel -type f \
  ! -name "*.zip" ! -name "*.png" ! -name "*.jpg" ! -name "*.webp" \
  | xargs grep -l "Infinite Leverage\|infiniteleverage\|talentedgeai" 2>/dev/null \
  | while read f; do
      sed -i '' \
        -e "s|Infinite Leverage|${BRAND_NAME}|g" \
        -e "s|infiniteleverage|${BRAND_SLUG}|g" \
        -e "s|talentedgeai|${GH_ORG}|g" \
        -e "s|infiniteleverage-8-agents-template|${TEMPLATE_REPO}|g" \
        -e "s|infiniteleverage-plugin|${PLUGIN_REPO}|g" \
        -e "s|infiniteleverage-partner-portal|${PORTAL_REPO}|g" \
        -e "s|partners@infiniteleverage\.com|${PARTNER_EMAIL}|g" \
        "$f"
      echo "  rebranded: $f"
    done
```

Verify the result — spot-check a few key files:

```bash
grep -r "Infinite Leverage\|talentedgeai\|infiniteleverage" /tmp/il-whitelabel \
  --include="*.md" --include="*.sh" --include="*.json" -l
```

If any files still contain the original brand, investigate before continuing.

---

## Step 5 — Rename skill and script filenames

```bash
cd /tmp/il-whitelabel

# Rename setup-skill directories
for d in setup-skills/infiniteleverage-*; do
  newname="${d/infiniteleverage-/${BRAND_SLUG}-}"
  mv "$d" "$newname"
done

# Rename zip files (will be regenerated in Step 7)
rm -f setup-skills/*.zip
```

---

## Step 6 — Create GitHub repos for the partner

```bash
# Public template repo
gh repo create "${GH_ORG}/${TEMPLATE_REPO}" --public --description "${BRAND_NAME} 8-Agent Templates"

# Private partner portal repo
gh repo create "${GH_ORG}/${PORTAL_REPO}" --private --description "${BRAND_NAME} Partner Portal (restricted)"
```

---

## Step 7 — Push the rebranded template

```bash
cd /tmp/il-whitelabel
git remote set-url origin "https://github.com/${GH_ORG}/${TEMPLATE_REPO}.git"

# Rebuild zips before pushing
bash scripts/rebuild-zips.sh

git add setup-skills/
git commit -m "chore: initial whitelabel rebrand from Infinite Leverage to ${BRAND_NAME}"
git push origin main
```

---

## Step 8 — Seed the partner portal

The partner portal mirrors the same structure as this skill but under the partner's brand. Copy this whitelabel skill into it so the partner can grant their own sub-partners access.

```bash
mkdir -p /tmp/il-portal/setup-skills/${BRAND_SLUG}-whitelabel
cp /tmp/il-whitelabel/setup-skills/${BRAND_SLUG}-whitelabel/SKILL.md \
   /tmp/il-portal/setup-skills/${BRAND_SLUG}-whitelabel/SKILL.md

cd /tmp/il-portal
git init
git remote add origin "https://github.com/${GH_ORG}/${PORTAL_REPO}.git"
git add .
git commit -m "feat: initialize partner portal"
git push origin main
```

---

## Step 9 — Update the partner check in init skill

The rebranded init skill still points to `talentedgeai/infiniteleverage-partner-portal` for the partner check. Update it to point to the partner's own portal:

File: `setup-skills/${BRAND_SLUG}-init/SKILL.md`

Find:
```
gh repo view talentedgeai/infiniteleverage-partner-portal
```

Replace with:
```
gh repo view ${GH_ORG}/${PORTAL_REPO}
```

Commit and push.

---

## Step 10 — Verify

```bash
echo "=== Whitelabel verification ==="
echo "Template repo:"
gh repo view "${GH_ORG}/${TEMPLATE_REPO}" --json name,visibility --jq '"  \(.name) [\(.visibility)]"'

echo "Partner portal repo:"
gh repo view "${GH_ORG}/${PORTAL_REPO}" --json name,visibility --jq '"  \(.name) [\(.visibility)]"'

echo "Spot-check for leftover IL branding:"
count=$(gh api "repos/${GH_ORG}/${TEMPLATE_REPO}/git/trees/main?recursive=1" \
  --jq '[.tree[].path | select(test("infiniteleverage|talentedgeai"))] | length')
echo "  Files with original branding: ${count} (should be 0)"
```

---

## Done

Hand the partner:

1. URL of their template repo: `https://github.com/${GH_ORG}/${TEMPLATE_REPO}`
2. URL of their partner portal (private): `https://github.com/${GH_ORG}/${PORTAL_REPO}`
3. Instructions to invite their own sub-partners to the portal repo (GitHub → Settings → Collaborators)
4. Their init zip from `setup-skills/${BRAND_SLUG}-init/${BRAND_SLUG}-init.zip` — this is what they distribute to their own clients
