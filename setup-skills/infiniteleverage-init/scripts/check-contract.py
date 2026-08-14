#!/usr/bin/env python3
"""Contract check for the infiniteleverage-init skill and prompt.

Layer-1 CI check (see TESTING.md). Runs from the skill directory:
    python3 scripts/check-contract.py [skill_dir]

Checks, mechanical half of SKILL-REGRESSION-CHECK.md:
  1. PROMPT.md's raw URL points at the `stable` branch.
  2. Every "Your turn" gate in SKILL.md carries its three parts
     (clicks, a why, a verify).
  3. Every references/ file SKILL.md mentions exists on disk.
  4. The catalog keys Stage F fills appear in SKILL.md's fill list,
     and no catalog instruction ever writes a key value.
  5. Neither file contains anything shaped like a real credential.
"""

import re
import sys
from pathlib import Path

FAILURES = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def main() -> int:
    skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    prompt = (skill_dir / "PROMPT.md").read_text(encoding="utf-8")

    # 1. Prompt URL pins stable.
    urls = re.findall(r"https://raw\.githubusercontent\.com/\S+/SKILL\.md", prompt)
    if not urls:
        fail("PROMPT.md: no raw SKILL.md URL found")
    for url in urls:
        if "/stable/" not in url:
            fail(f"PROMPT.md: URL must point at the stable branch, got: {url}")
    if re.search(r"raw\.githubusercontent\.com/\S+/main/", prompt + skill):
        fail("A runtime URL points at main; consumers must pin stable")

    # 2. Gate structure: each gate block needs its three parts.
    gate_heads = re.findall(r"\*\*Gate [\w0-9]+ —[^*]*\*\*", skill)
    if len(gate_heads) < 6:
        fail(f"SKILL.md: expected at least 6 gates, found {len(gate_heads)}")
    blocks = re.split(r"(?=\*\*Gate [\w0-9]+ —)", skill)
    for block in blocks[1:]:
        head = block.splitlines()[0][:60]
        section = block.split("###")[0].split("**Gate", 2)
        body = "**Gate" + section[1] if len(section) > 1 else block
        for part in ("Your turn", "Why it", "Verify"):
            if part.lower() not in body.lower():
                fail(f"SKILL.md gate '{head}': missing part '{part}'")

    # 3. Referenced files exist.
    refs = set(re.findall(r"references/([\w.-]+\.md)", skill))
    for ref in sorted(refs):
        if not (skill_dir / "references" / ref).exists():
            fail(f"SKILL.md references missing file: references/{ref}")
    # only paths relative to this skill dir; skip e.g. the patch skill's scripts/
    for script in set(re.findall(r"(?<![\w/-])scripts/([\w.-]+\.(?:py|sh))", skill)):
        if not (skill_dir / "scripts" / script).exists():
            fail(f"SKILL.md references missing script: scripts/{script}")

    # 4. Catalog fill list: required keys present, secrets never written.
    # The contract: every catalog key the Block I prompt writes as [pending] must
    # appear in the skill's Stage F fill list. Derived from PROMPT.md rather than
    # hardcoded, so changing a key in the prompt cannot silently leave setup
    # unable to clear it. Build-status lines are filled by Blocks III and IV, not
    # by setup, so they are excluded here.
    pending_keys = re.findall(r"^- ([A-Za-z][^:\n]*): \[pending\]", prompt, re.M)
    if not pending_keys:
        fail("PROMPT.md: no [pending] catalog keys found; the Block I prompt is missing or changed shape")
    required_fill_keys = [k for k in pending_keys if not k.startswith("Build ") and k != "Admin account seeded"]
    for key in required_fill_keys:
        if key not in skill:
            fail(f"SKILL.md Stage F fill list is missing catalog key: {key}")
    if "stored in website/.env.local, never written here" not in skill:
        fail("SKILL.md: the key-line rule ('stored in website/.env.local, never written here') is gone")
    if "[deferred to Build 2]" not in skill:
        fail("SKILL.md: the Email and domain deferral marker is gone (the Build 1 gate would block)")

    # 5. Nothing shaped like a real credential in either file.
    secret_shapes = [
        (r"sb_secret_[A-Za-z0-9]{10,}", "Supabase secret key"),
        (r"eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{10,}", "JWT"),
        (r"re_[A-Za-z0-9]{16,}", "Resend key"),
        (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
        (r"AIza[A-Za-z0-9_-]{20,}", "Google API key"),
    ]
    for text, name in (("SKILL.md", skill), ("PROMPT.md", prompt)):
        for pattern, label in secret_shapes:
            if re.search(pattern, name):
                fail(f"{text}: contains something shaped like a {label}")

    if FAILURES:
        print(f"contract check FAILED ({len(FAILURES)}):")
        for msg in FAILURES:
            print(f"  - {msg}")
        return 1
    print("contract check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
