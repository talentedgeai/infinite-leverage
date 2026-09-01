#!/usr/bin/env bash
# doctor-smoke.sh — runs il-doctor's project-layout section against synthetic
# trees and asserts which lines fire. Section C is the part a client actually
# reads; before this test, its adopted-repo path had never executed at all.
#
# Usage: bash .github/scripts/doctor-smoke.sh      (from the repo root or anywhere)
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
DOCTOR="$ROOT/plugin/skills/il-doctor/scripts/doctor.sh"
export CLAUDE_PLUGIN_ROOT="$ROOT/plugin"
EXPECT_V=$(tr -d '[:space:]' < "$ROOT/VERSION")

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
FAILS=0

fresh_tree() {  # $1 = dir — the canonical 4 agents, 16 skills, the rules file
  mkdir -p "$1/.claude/agents" "$1/.claude/skills" "$1/.claude/rules"
  for a in product-manager developer qa devops; do : > "$1/.claude/agents/$a.md"; done
  for i in $(seq 1 16); do mkdir -p "$1/.claude/skills/skill-$i"; done
  : > "$1/.claude/rules/global-engineering.md"
}
current_block() {
  printf '<!-- BEGIN: AGENT-DELEGATION -->\n| **product-manager** | x |\n| **developer** | x |\n<!-- END: AGENT-DELEGATION -->\n'
}
legacy_block() {
  printf '<!-- BEGIN: AGENT-DELEGATION -->\n| **product-manager** | x |\n| **designer** | x |\n| **writer** | x |\n<!-- END: AGENT-DELEGATION -->\n'
}
run_doctor() { (cd "$1" && bash "$DOCTOR" 2>/dev/null); }
section_c()  { sed -n '/\[ C · Project Layout \]/,/\[ C2 ·/p'; }

# expect <case> <yes|no> <regex>  — assert the captured output does / doesn't match
expect() {
  local case=$1 want=$2 re=$3 got=no
  grep -qE -- "$re" "$TMP/$case.out" && got=yes
  if [ "$got" = "$want" ]; then
    printf '  ok    %-24s %s /%s/\n' "$case" "$want" "$re"
  else
    printf '  FAIL  %-24s expected %s /%s/\n' "$case" "$want" "$re"
    sed 's/^/        | /' "$TMP/$case.out"
    FAILS=$((FAILS + 1))
  fi
}

echo "doctor smoke — $DOCTOR"

# 1. Fresh scaffold from /il-project: all green.
D="$TMP/scaffolded"; fresh_tree "$D"; : > "$D/FOLDER-STRUCTURE.md"; current_block > "$D/CLAUDE.md"
run_doctor "$D" | section_c > "$TMP/scaffolded.out"
expect scaffolded yes 'PASS  FOLDER-STRUCTURE.md present'
expect scaffolded yes 'PASS  canonical agents installed'
expect scaffolded yes 'PASS  project skills installed'
expect scaffolded yes 'PASS  engineering rules installed'
expect scaffolded yes 'PASS  no retired v2.4'
expect scaffolded yes 'PASS  CLAUDE.md delegation block'
expect scaffolded no  'FAIL'

# 2. Adopted repo (/il-adopt): no FOLDER-STRUCTURE.md, plus one custom agent.
#    Section C must still run, and the extra agent must not fail the check.
D="$TMP/adopted"; fresh_tree "$D"; : > "$D/.claude/agents/data-analyst.md"; current_block > "$D/CLAUDE.md"
run_doctor "$D" | section_c > "$TMP/adopted.out"
expect adopted yes '\[ C · Project Layout \]'
expect adopted yes 'adopted repo'
expect adopted yes 'PASS  canonical agents installed .*5 agents'
expect adopted no  'FAIL'

# 3. Legacy v2.4 project: writer/designer + a retired skill + the old block.
D="$TMP/legacy"; fresh_tree "$D"; : > "$D/FOLDER-STRUCTURE.md"
: > "$D/.claude/agents/writer.md"; : > "$D/.claude/agents/designer.md"
mkdir -p "$D/.claude/skills/writer-seo-content" "$D/.claude/skills/designer-ui-ux"
legacy_block > "$D/CLAUDE.md"
run_doctor "$D" | section_c > "$TMP/legacy.out"
expect legacy yes 'FAIL  no retired v2.4.*agents/writer.md'
expect legacy yes 'FAIL  no retired v2.4.*agents/designer.md'
expect legacy yes 'FAIL  no retired v2.4.*skills/writer-seo-content/'
expect legacy yes 'FAIL  no retired v2.4.*skills/designer-ui-ux/'
expect legacy yes 'FAIL  CLAUDE.md delegation block current.*writer/designer'
expect legacy yes 'fix: run /il-adopt'
expect legacy yes 'PASS  canonical agents installed'

# 4. Six agents on disk but qa missing — a bare "count >= 4" would have passed this.
D="$TMP/missing-qa"; fresh_tree "$D"; rm "$D/.claude/agents/qa.md"
: > "$D/.claude/agents/writer.md"; : > "$D/.claude/agents/designer.md"; : > "$D/.claude/agents/custom.md"
current_block > "$D/CLAUDE.md"
run_doctor "$D" | section_c > "$TMP/missing-qa.out"
expect missing-qa yes 'FAIL  canonical agents installed .*missing: qa'

# 5. No block, no rules, too few skills.
D="$TMP/partial"; mkdir -p "$D/.claude/agents"; : > "$D/.claude/agents/developer.md"
run_doctor "$D" | section_c > "$TMP/partial.out"
expect partial yes 'FAIL  canonical agents installed .*missing: product-manager qa devops'
expect partial yes 'FAIL  project skills installed .*found 0 \(expected 16\)'
expect partial yes 'FAIL  engineering rules installed'
expect partial yes 'FAIL  CLAUDE.md delegation block .*fix: run /il-adopt'

# 6. A plain directory: section C must not appear at all.
D="$TMP/plain"; mkdir -p "$D"
run_doctor "$D" > "$TMP/plain.out"
expect plain no '\[ C · Project Layout \]'

# 7. Version parse without python3: the installed-plugin line shows the VERSION file's value.
run_doctor "$TMP/plain" | sed -n '/\[ C2 ·/,/\[ D ·/p' > "$TMP/version.out"
expect version yes "PASS  installed plugin .*v${EXPECT_V//./\\.}"
expect version no  'vunknown'

echo
if [ "$FAILS" -eq 0 ]; then
  echo "doctor smoke: all assertions passed"
else
  echo "doctor smoke: $FAILS assertion(s) failed"; exit 1
fi
