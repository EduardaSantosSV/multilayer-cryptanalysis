#!/usr/bin/env python3
"""
Etapa 3 - fatora o modulo RSA, recupera a chave privada e decifra
key_for_message.en.
Uso: python3 -I etapa3_fatorar_rsa.py --n <modulo> --e <expoente> [--c <hex>]

O modulo tem ~382 bits (curto), entao da pra fatorar sem hardware especial.
Tenta, da mais barata pra mais cara: factordb, divisao por tentativa, Fermat
(bom se p e q sao proximos), Pollard rho e Pollard p-1. Se nenhuma dessas
der conta, precisa de uma ferramenta de crivo (yafu/msieve). So usa stdlib.
"""
import argparse
import math
import random
import sys
import urllib.request
import urllib.error
import json


def is_probable_prime(n, k=20):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def trial_division(n, bound=2_000_000):
    print(f"[*] Tentando divisao por tentativa (limite {bound})...")
    if n % 2 == 0:
        return 2, n // 2
    f = 3
    while f <= bound and f * f <= n:
        if n % f == 0:
            return f, n // f
        f += 2
    return None


def fermat_factor(n, max_iter=5_000_000):
    print(f"[*] Tentando fatoracao de Fermat (ate {max_iter} iteracoes)...")
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    for i in range(max_iter):
        if i % 500_000 == 0 and i > 0:
            print(f"    {i:,}/{max_iter:,} iteracoes...", flush=True)
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            p, q = a - b, a + b
            if p > 1 and q > 1:
                return p, q
        a += 1
    return None


def pollard_rho(n, max_tries=20, max_iter_per_try=2_000_000):
    print(f"[*] Tentando Pollard's rho ({max_tries} tentativas x ate "
          f"{max_iter_per_try:,} iteracoes cada)...")
    if n % 2 == 0:
        return 2, n // 2

    def f(x, c, n):
        return (x * x + c) % n

    for tentativa in range(max_tries):
        x = random.randrange(2, n - 1)
        y = x
        c = random.randrange(1, n - 1)
        d = 1
        it = 0
        while d == 1 and it < max_iter_per_try:
            x = f(x, c, n)
            y = f(f(y, c, n), c, n)
            d = math.gcd(abs(x - y), n)
            it += 1
            if it % 200_000 == 0:
                print(f"    tentativa {tentativa+1}/{max_tries}, "
                      f"{it:,} iteracoes...", flush=True)
        if d != 1 and d != n:
            return d, n // d
        print(f"    tentativa {tentativa+1}/{max_tries} esgotada sem sucesso.",
              flush=True)
    return None


def pollard_p_minus_1(n, bound=1_000_000):
    print(f"[*] Tentando Pollard p-1 (limite de suavidade {bound})...")
    a = 2
    for p in range(2, bound):
        a = pow(a, p, n)
        if a == 0:
            return None
        d = math.gcd(a - 1, n)
        if 1 < d < n:
            return d, n // d
    return None


def factordb_lookup(n):
    print("[*] Consultando factordb.com (banco publico de fatoracoes)...")
    try:
        url = f"http://factordb.com/api?query={n}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        status = data.get("status")
        factors = data.get("factors", [])
        if status in ("FF", "P", "PRP") and len(factors) >= 2:
            # factors: lista de [fator, multiplicidade]
            flat = []
            for fac, mult in factors:
                flat.extend([int(fac)] * int(mult))
            if len(flat) == 2:
                return flat[0], flat[1]
            # mais de 2 fatores (nao deveria acontecer p/ RSA valido) - agrupa
            p = flat[0]
            q = n // p
            return p, q
        print(f"    factordb: status={status}, sem fatoracao completa disponivel.")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"    factordb: sem acesso ({exc}).")
    except Exception as exc:
        print(f"    factordb: erro ao interpretar resposta ({exc}).")
    return None


def factor_n(n):
    for strategy in (factordb_lookup, trial_division, fermat_factor,
                     pollard_rho, pollard_p_minus_1):
        result = strategy(n)
        if result:
            p, q = result
            if p * q == n and p > 1 and q > 1:
                return p, q
            print(f"    (resultado inconsistente de {strategy.__name__}, ignorando)")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", required=True, help="modulo RSA (hex com 0x ou decimal)")
    ap.add_argument("--e", type=int, default=65537, help="expoente publico (default 65537)")
    ap.add_argument("--c", help="ciphertext de key_for_message.en (hex) - se passado, "
                                 "decifra automaticamente apos fatorar N")
    args = ap.parse_args()

    n_str = args.n.strip()
    n = int(n_str, 16) if n_str.lower().startswith("0x") else int(n_str)
    e = args.e

    print(f"[*] N = {n}")
    print(f"[*] bits(N) = {n.bit_length()}")
    print(f"[*] e = {e}")
    print()

    result = factor_n(n)
    if not result:
        print("\n[FALHA] Nenhuma estrategia conseguiu fatorar N.")
        print("        Considerar instalar yafu/msieve/gmp-ecm/pari-gp para")
        print("        fatores maiores, ou revisar se N foi extraido corretamente.")
        sys.exit(1)

    p, q = result
    if p > q:
        p, q = q, p

    print(f"\n[SUCESSO] N = p * q")
    print(f"  p = {p}  ({p.bit_length()} bits)")
    print(f"  q = {q}  ({q.bit_length()} bits)")

    if not is_probable_prime(p) or not is_probable_prime(q):
        print("  [aviso] p ou q nao passou no teste de primalidade - revisar.")

    phi = (p - 1) * (q - 1)
    try:
        d = pow(e, -1, phi)
    except ValueError:
        print("  [ERRO] e nao e invertivel mod phi(n) - e e phi(n) nao sao coprimos.")
        sys.exit(1)

    print(f"\n  phi(N) = {phi}")
    print(f"  d (expoente privado) = {d}")
    print(f"\n  Chave privada RSA recuperada: (n={n}, e={e}, d={d})")

    if not args.c:
        print("\n  Use --c <hex de key_for_message.en> pra decifrar automaticamente,")
        print("  ou faca manualmente:")
        print("    c = int(open('key_for_message.en').read().strip(), 16)")
        print("    m = pow(c, d, n)")
        print("    plaintext_bytes = m.to_bytes((m.bit_length()+7)//8, 'big')")
        return

    c_str = args.c.strip()
    c = int(c_str, 16) if not c_str.lower().startswith("0x") else int(c_str, 16)
    nbytes = (n.bit_length() + 7) // 8  # tamanho do modulo em bytes

    print(f"\n[*] Decifrando key_for_message.en (RSA textbook, sem padding assumido)...")
    m = pow(c, d, n)
    plaintext = m.to_bytes(nbytes, "big")  # preserva zeros a esquerda do tamanho do modulo
    plaintext_stripped = plaintext.lstrip(b"\x00")

    print(f"  bytes (com zeros a esquerda do tamanho do modulo, {nbytes} bytes):")
    print(f"    hex: {plaintext.hex()}")
    print(f"  bytes (sem zeros a esquerda, {len(plaintext_stripped)} bytes):")
    print(f"    hex: {plaintext_stripped.hex()}")
    try:
        texto = plaintext_stripped.decode("utf-8")
        print(f"  como texto UTF-8: {texto!r}")
        print("\n  >>> Esse texto e provavelmente a SENHA usada em 'openssl enc -k'")
        print("      para cifrar message.en (ele tem cabecalho 'Salted__', ou seja,")
        print("      foi cifrado por senha, nao por chave bruta).")
        print(f"      Proximo passo: ./etapa4_decifrar_message.sh {texto!r}")
    except UnicodeDecodeError:
        print("  [aviso] nao decodifica como UTF-8 limpo - pode ter padding")
        print("          (OAEP/PKCS1) que nao foi removido, ou ser bytes binarios")
        print("          de chave+IV em vez de uma senha texto. Inspecionar o hex acima.")


if __name__ == "__main__":
    main()
