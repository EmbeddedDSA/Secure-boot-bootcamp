# Lab 00 — Signing a firmware image, and watching tampering fail

**Module 1: Threat models and the root of trust** · Status: *in progress*

## What security property this lab demonstrates

**Authenticity and integrity of a firmware image.** A device should run an image
only if it was produced by the holder of a specific private key, and has not
been changed by even one bit since it was signed. This lab shows that property
end to end with standard tools, and computes the exact value a silicon vendor
would burn into one-time-programmable fuses to anchor it.

## What gets built

1. An RSA key pair and an elliptic-curve key pair (in the gitignored `keys/`
   directory, via `tools/gen-keys.sh`; no private key is ever committed).
2. A dummy firmware image, signed with RSA-PSS over SHA-256.
3. A successful verification of the untouched image.
4. A one-byte modification of the image, and the verification failure it causes.
5. The SHA-256 digest of the public key in DER encoding — the value that
   would be programmed into the root-of-trust fuses.

## How to run

```bash
./run.sh
```

`run.sh` regenerates throwaway keys, runs every step above, and prints only
deterministic lines (pass/fail results, never key-dependent bytes), so the
output can be compared against `expected-output.txt` in CI.

## What the expected output means

Filled in when the lab is complete.
