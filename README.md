# Multilayer Cryptanalysis Challenge

Recovering a confidential message protected by several stacked layers of
encryption, starting from almost nothing: a cryptographic hash of an access
password and a two-character hint.

**Authors:** Julia Brenda Souza da Rosa, Eduarda dos Santos da Silva
**Course:** Algoritmos e Estrutura de Dados III (AEDS3) — UFPEL

## The challenge

We were given four files and had to figure out, from scratch, every
algorithm, mode of operation, key size and encoding used in each one:

| File | What it was |
|------|-------------|
| `message.en` | the secret message, encrypted |
| `key_for_message.en` | the message's key, protected by public-key crypto |
| `key_public.en` | the RSA public key, protected by symmetric crypto |
| `key_for_rsa_public.hash` | hash of the password that unlocks the public key |

The only hint: the password starts with `gu`.

## Approach

The solution is a chain — each step unlocks the next:

1. **Password recovery** — the target is a 256-bit hash. Dictionary attack
   (custom Python) plus mask/brute-force with `hashcat`, filtering by the
   `gu` prefix. Algorithm: **SHA-256**.
2. **Symmetric layer** — `key_public.en` is an `openssl enc` blob. From its
   ciphertext length (157 bytes, not a block multiple) we inferred a stream
   mode and swept ciphers/KDFs until a valid RSA public key came out.
   Algorithm: **AES-256-CTR**.
3. **RSA layer** — the recovered modulus is only 382 bits. Classic shortcuts
   (Fermat, Pollard rho/p-1, ECM) all failed because the two 191-bit primes
   are balanced and random. Factored with a general-purpose quadratic sieve
   (**SIQS**, via `yafu`), then recovered the private key and decrypted the
   message key (RSA with **PKCS#1 v1.5** padding).
4. **Final message** — `message.en` decrypted with the recovered password.
   Algorithm: **AES-256-CBC**.

Tools: `hashcat`, `openssl`, `yafu`, and custom Python/Bash scripts (standard
library only — no external crypto dependencies).

## Repository layout

```
.
├── enunciado.txt              challenge statement (original)
├── message.en                 encrypted files provided (original)
├── key_for_message.en
├── key_public.en
├── key_for_rsa_public.hash
├── relatorio_grupo14.pdf      full write-up (methodology, results, code)
└── scripts/
    ├── crack_hash.py               stage 1 - dictionary attack
    ├── etapa1_descobrir_senha.sh   stage 1 - hashcat brute-force runbook
    ├── etapa2_analise_estrutural.sh  structural analysis of the ciphertexts
    ├── etapa2_decifrar_key_public.sh stage 2 - decrypt the public key
    ├── etapa3_fatorar_rsa.py       stage 3 - RSA factoring + private key
    ├── etapa4_decifrar_message.sh  stage 4 - decrypt the message
    ├── gerar_relatorio.py          builds the PDF report
    └── STATUS.md                   progress notes
```

## Reproducing

```bash
# stage 1: password = SHA-256 preimage, see scripts/etapa1_descobrir_senha.sh
# stage 2:
./scripts/etapa2_decifrar_key_public.sh "<password>"
# stage 3: factor N (SIQS) then
./scripts/etapa3_fatorar_rsa.py --n <N> --e 65537 --c <hex of key_for_message.en>
# stage 4:
./scripts/etapa4_decifrar_message.sh "<message password>"
```

The complete step-by-step procedure, the discovered values, the failed
attempts and all source code are in **`relatorio_grupo14.pdf`**.
