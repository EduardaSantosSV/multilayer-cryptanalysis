#!/usr/bin/env python3
"""
Etapa 1 - tentativa de quebrar a senha por dicionario.
O hash tem 64 hex (256 bits), entao chutamos SHA-256. Sabemos que a
senha comeca com "gu", entao juntamos umas wordlists do sistema, filtramos
pelo prefixo, aplicamos algumas mutacoes e comparamos o hash. Se o SHA-256
nao bater, testa sha3_256 e blake2s tambem.
"""
import hashlib

TARGET_HASH = "befb7036fb77a8517e95d9dbb797031850fce2ecdb988e96d7f040a2608e87e4"
KNOWN_PREFIX = "gu"

WORDLIST_FILES = [
    "/usr/share/dict/portuguese",
    "/usr/share/dict/brazilian",
    "/usr/share/dict/cracklib-small",
    "/usr/share/john/password.lst",
    "/usr/share/dict/american-english",
]

# chutes nossos ligados ao tema do trabalho
THEMATIC_WORDS = [
    "guerra", "guerreiro", "guarda", "guardiao", "guardia", "guardian",
    "guarani", "gustavo", "guaraci", "guaxinim", "gurgel", "gula",
    "guzik", "gu14", "grupo14", "gu2026",
]


def load_candidates():
    seen = set()
    candidates = []

    def add(w):
        w = w.strip()
        if w and w not in seen:
            seen.add(w)
            candidates.append(w)

    for path in WORDLIST_FILES:
        try:
            with open(path, "r", encoding="latin-1", errors="ignore") as f:
                for line in f:
                    add(line.rstrip("\n"))
        except FileNotFoundError:
            print(f"[aviso] wordlist nao encontrada: {path}")

    for w in THEMATIC_WORDS:
        add(w)

    return candidates


def mutate(word):
    # capitaliza/maiusculas + sufixos comuns (numeros, ano, simbolo)
    base_forms = {word, word.lower(), word.upper(), word.capitalize()}
    suffixes = ["", "1", "12", "123", "!", "@", "#", "2024", "2025", "2026",
                "14", "#14"]
    for b in base_forms:
        for s in suffixes:
            yield b + s


def hash_fns():
    return {
        "sha256": lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest(),
        "sha3_256": lambda s: hashlib.sha3_256(s.encode("utf-8")).hexdigest(),
        "blake2s": lambda s: hashlib.blake2s(s.encode("utf-8")).hexdigest(),
    }


def main():
    print(f"[*] hash alvo: {TARGET_HASH}")
    print(f"[*] tamanho do hash: {len(TARGET_HASH)} hex chars -> {len(TARGET_HASH)//2} bytes")
    print(f"[*] prefixo conhecido da senha: '{KNOWN_PREFIX}'")

    raw_candidates = load_candidates()
    print(f"[*] total de palavras carregadas (antes do filtro de prefixo): {len(raw_candidates)}")

    filtered = [w for w in raw_candidates if w.lower().startswith(KNOWN_PREFIX)]
    print(f"[*] candidatos com prefixo '{KNOWN_PREFIX}': {len(filtered)}")

    tested = 0
    algos = hash_fns()
    for base in filtered:
        for cand in mutate(base):
            tested += 1
            for algo_name, fn in algos.items():
                if fn(cand) == TARGET_HASH:
                    print(f"\n[SUCESSO] senha encontrada!")
                    print(f"  senha    : {cand!r}")
                    print(f"  algoritmo: {algo_name}")
                    print(f"  tentativas: {tested}")
                    return cand, algo_name

    print(f"\n[FALHA] nenhuma senha encontrada entre {tested} tentativas "
          f"({len(algos)} algoritmos testados: {', '.join(algos)}).")
    return None, None


if __name__ == "__main__":
    main()
