#!/usr/bin/env bash
# Etapa 1 - descoberta da senha de key_for_rsa_public.hash
# Precisa de hashcat, python3 e as wordlists (wbrazilian, wportuguese,
# cracklib-runtime, john). Rodar os blocos em ordem; os marcados [FALHOU]
# sao as tentativas que nao deram certo.
set -e
cd "$(dirname "$0")"

echo "### 1) Dar uma olhada nos arquivos de entrada ###"
cd /home/eduarda/Documentos/CRIPTO
file message.en key_for_message.en key_public.en key_for_rsa_public.hash
echo "--- key_for_message.en (chave cifrada, RSA?) ---"
cat key_for_message.en
echo
echo "--- key_for_rsa_public.hash (hash da senha) ---"
cat key_for_rsa_public.hash
echo
H=$(tr -d '\n' < key_for_rsa_public.hash)
echo "tamanho do hash: ${#H} caracteres hex -> $(( ${#H} / 2 )) bytes (= digest de 256 bits)"

echo
echo "### 2) Localizar wordlists disponiveis no sistema ###"
dpkg -L wbrazilian 2>/dev/null | grep dict
dpkg -L wportuguese 2>/dev/null | grep dict
dpkg -L cracklib-runtime 2>/dev/null | grep dict
ls -la /usr/share/john/password.lst

echo
echo "### 3) Ataque de dicionario (script Python, prefixo 'gu' + mutacoes) ###"
cd /home/eduarda/Documentos/CRIPTO/scripts
python3 -I crack_hash.py
# [FALHOU] nada bateu (46560 tentativas em sha256/sha3_256/blake2s)

echo
echo "### 4) Benchmark do hashcat (ver se da pra fazer forca bruta) ###"
hashcat -I            # lista os dispositivos (aqui so CPU)
hashcat -b -m 1400     # benchmark do SHA-256 (modo 1400)

echo
echo "### 5) Forca bruta com mascara: 'gu' + sufixo minusculas+digitos ###"
echo "--- 5a) tamanho total 1 a 5 [FALHOU - increment mal configurado] ---"
hashcat -m 1400 -a 3 -O --potfile-disable \
  -1 ?l?d --increment --increment-min=1 --increment-max=5 \
  target_hash.txt 'gu?1?1?1?1?1' -o cracked_5a.txt --force || true
# deu ruim aqui: o --increment conta o tamanho TOTAL da mascara (contando
# o "gu" fixo), nao so o sufixo, entao acabou testando menos do que a gente
# pensava.

echo "--- 5b) tamanho total 2 a 7 (sufixo 0 a 5), minusculas+digitos [FALHOU] ---"
hashcat -m 1400 -a 3 -O --potfile-disable \
  -1 ?l?d --increment --increment-min=2 --increment-max=7 \
  target_hash.txt 'gu?1?1?1?1?1' -o cracked_5b.txt --force || true

echo "--- 5c) tamanho total 8 (sufixo 6), minusculas+digitos [FALHOU] ---"
hashcat -m 1400 -a 3 -O --potfile-disable \
  -1 ?l?d --increment --increment-min=8 --increment-max=8 \
  target_hash.txt 'gu?1?1?1?1?1?1' -o cracked_5c.txt --force || true

echo
echo "### 6) Forca bruta com mascara: minusculas+MAIUSCULAS+digitos ###"
echo "--- 6a) tamanho total 2 a 7 [FALHOU] ---"
hashcat -m 1400 -a 3 -O --potfile-disable \
  -1 ?l?u?d --increment --increment-min=2 --increment-max=7 \
  target_hash.txt 'gu?1?1?1?1?1' -o cracked_6a.txt --force || true

echo "--- 6b) tamanho total 8 [FALHOU - colidiu com instancia anterior do hashcat] ---"
# [FALHOU] da primeira vez rodamos esse junto com outro hashcat e deu
# "Already an instance running" - so da pra rodar um hashcat por vez.
hashcat -m 1400 -a 3 -O --potfile-disable \
  -1 ?l?u?d --increment --increment-min=8 --increment-max=8 \
  target_hash.txt 'gu?1?1?1?1?1?1' -o cracked_6b.txt --force || true

echo
echo "### 7) Forca bruta com mascara: ASCII imprimivel completo (com simbolos) ###"
echo "--- 7a) tamanho total 2 a 7 [FALHOU] ---"
hashcat -m 1400 -a 3 -O --potfile-disable \
  -1 ?a --increment --increment-min=2 --increment-max=7 \
  target_hash.txt 'gu?1?1?1?1?1' -o cracked_7a.txt --force || true

echo
echo "### 8) Verificar se algum arquivo cracked_*.txt tem resultado ###"
for f in cracked_5a.txt cracked_5b.txt cracked_5c.txt cracked_6a.txt cracked_6b.txt cracked_7a.txt; do
  if [ -s "$f" ]; then
    echo ">>> SUCESSO em $f:"
    cat "$f"
  fi
done
echo "(se nada apareceu acima, nenhuma faixa testada ainda encontrou a senha)"

echo
echo "### 9) Testar outros hashes de 256 bits (rapido, so pra garantir) ###"
echo "--- 9a) SHA3-256 (modo hashcat 17400) ---"
hashcat -m 17400 -a 3 -O --potfile-disable \
  -1 ?l?d --increment --increment-min=2 --increment-max=8 \
  target_hash.txt 'gu?1?1?1?1?1?1' -o cracked_9a.txt --force || true
hashcat -m 17400 -a 3 -O --potfile-disable \
  -1 ?l?u?d --increment --increment-min=2 --increment-max=8 \
  target_hash.txt 'gu?1?1?1?1?1?1' -o cracked_9a2.txt --force || true

echo "--- 9b) Keccak-256 (modo hashcat 17800, pre-padronizacao do SHA3) ---"
hashcat -m 17800 -a 3 -O --potfile-disable \
  -1 ?l?d --increment --increment-min=2 --increment-max=8 \
  target_hash.txt 'gu?1?1?1?1?1?1' -o cracked_9b.txt --force || true
hashcat -m 17800 -a 3 -O --potfile-disable \
  -1 ?l?u?d --increment --increment-min=2 --increment-max=8 \
  target_hash.txt 'gu?1?1?1?1?1?1' -o cracked_9b2.txt --force || true
# BLAKE2s nao tem modo no hashcat, so deu pra testar pelo crack_hash.py (bloco 3)

echo
echo "### 10) Forca bruta SHA-256, tamanho total 9, minusculas+digitos ###"
echo "    (mais pesado - 36^7 combinacoes, uns 15-20 min so de CPU)"
hashcat -m 1400 -a 3 -O --potfile-disable \
  -1 ?l?d --increment --increment-min=9 --increment-max=9 \
  target_hash.txt 'gu?1?1?1?1?1?1?1' -o cracked_10.txt --force || true

echo
echo "### 11) Chutes manuais ligados ao tema (nomes do grupo, Biuro Szyfrow...) ###"
python3 -I - <<'PYEOF'
import hashlib
target = "befb7036fb77a8517e95d9dbb797031850fce2ecdb988e96d7f040a2608e87e4"
candidatos = [
    "gu14", "GU14", "grupo14senha", "guBiuroSzyfrow", "guszyfrow",
    "guRejewski", "guEnigma", "guCriptoanalise", "gueduarda", "gujulia",
    "gubrenda", "gurosa", "gusilva", "gusouza",
]
algos = {
    "sha256": lambda s: hashlib.sha256(s.encode()).hexdigest(),
    "sha3_256": lambda s: hashlib.sha3_256(s.encode()).hexdigest(),
    "blake2s": lambda s: hashlib.blake2s(s.encode()).hexdigest(),
}
achou = False
for c in candidatos:
    for nome, fn in algos.items():
        if fn(c) == target:
            print(f">>> SUCESSO: senha={c!r} algoritmo={nome}")
            achou = True
if not achou:
    print("Nenhum candidato tematico bateu com o hash.")
PYEOF

echo
echo "### 12) Verificar TODOS os arquivos cracked_* no final ###"
for f in cracked_*.txt; do
  [ -s "$f" ] && echo ">>> SUCESSO em $f:" && cat "$f"
done
echo "(se nada apareceu acima, repensar algoritmo/encoding e expandir mascara)"
