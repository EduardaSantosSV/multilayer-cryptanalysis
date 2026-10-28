#!/usr/bin/env bash
# Analise dos arquivos cifrados so olhando tamanho e cabecalho (sem a senha).
# Serve pra deduzir o modo de cada cifra antes de tentar decifrar.
set -e
cd /home/eduarda/Documentos/CRIPTO

echo "### message.en ###"
wc -c message.en
xxd message.en | head -2
echo "Cabecalho: 'Salted__' (8 bytes, magic do openssl enc) + salt (8 bytes) = 16 bytes"
CT=$(( $(wc -c < message.en) - 16 ))
echo "Ciphertext: $CT bytes | resto mod 16 = $(( CT % 16 ))"
echo ">> multiplo exato de 16 => cifra de bloco de 128 bits (AES?) com padding (CBC/ECB)"

echo
echo "### key_public.en (base64) ###"
wc -c key_public.en
base64 -d key_public.en > /tmp/key_public_decoded.bin
wc -c /tmp/key_public_decoded.bin
xxd /tmp/key_public_decoded.bin | head -2
B=$(wc -c < /tmp/key_public_decoded.bin)
CT2=$(( B - 16 ))
echo "Ciphertext: $CT2 bytes | resto mod 16 = $(( CT2 % 16 )) | resto mod 8 = $(( CT2 % 8 ))"
echo ">> NAO e multiplo de 8 nem 16 (157 e primo) => sem padding de bloco"
echo ">> indica modo STREAM (CTR/CFB/OFB), nao CBC/ECB"

echo
echo "### key_for_message.en (hex) ###"
H=$(tr -d '\n' < key_for_message.en)
echo "tamanho: ${#H} hex chars -> $(( ${#H} / 2 )) bytes -> $(( ${#H} / 2 * 8 )) bits"
echo ">> 48 bytes = 384 bits: tem cara de cifra RSA crua (o ciphertext tem o tamanho do modulo)"
echo ">> nossa aposta: e um modulo RSA bem curto (384 bits), da pra fatorar"
