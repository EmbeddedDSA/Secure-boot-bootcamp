# Secure Boot Bootcamp

A sixteen-week, lab-first course in embedded systems security and secure boot,
built on QEMU (qemuarm64) and real code. Every concept is backed by a lab that
builds something and then breaks it; every lab's output is checked in CI.

**Start here:** open [`index.html`](index.html) in a browser for the live
dashboard, or [`docs/syllabus.html`](docs/syllabus.html) for the full plan.
All documentation is self-contained HTML and works offline.

## What is in here

| Path | Contents |
|---|---|
| `docs/` | One HTML reference document per topic, grouped by module, plus a handbook and glossary |
| `labs/` | One directory per lab: what it proves, one command to run it, expected output |
| `capstone/` | A complete signed boot chain for qemuarm64: TF-A, OP-TEE, signed FIT, dm-verity, measured boot, attestation |
| `interview/` | Question bank with model answers, company notes, mock interview transcripts |
| `progress/` | Score log, weaknesses, weekly reviews |
| `tools/` | Shared scripts: lab runner, secret scanner, dashboard generator |

## Modules

1. Threat models and the root of trust
2. Cryptography for firmware engineers
3. The open-source security stack
4. Secure boot mechanics
5. ARM security architecture
6. The ARM boot chain in practice
7. Trusted execution environments
8. Hardware security blocks
9. Attestation and device identity
10. Secure update and key management
11. Attacking the chain
12. Standards and certification
13. Capstone and interview craft

## Running the labs

```bash
tools/install-hooks.sh     # once per clone: enables the private-key pre-commit hook
tools/gen-keys.sh          # regenerate throwaway test keys into the gitignored keys/
tools/run-labs.sh          # build and run every lab, diff against expected output
```

## Key hygiene

No private key is ever committed, not even a test key. Keys live in the
gitignored `keys/` directory and are regenerated on demand. A pre-commit hook
and a CI step both reject any file containing a private-key header.

## Author

Abdullah Mohammed — embedded software engineer (automotive and industrial),
building depth in platform and firmware security.
