#!/usr/bin/env bash
# Etapa 4 - decifra message.en com a senha recuperada no RSA (Etapa 3).
# Uso: ./etapa4_decifrar_message.sh "senha"
#
# message.en e binario (Salted__ + salt), ciphertext de 1520 bytes, multiplo
# de 16 -> cifra de bloco com padding (CBC/ECB). Testa varias cifras de bloco
# x KDF x digest e marca sucesso quando a saida tem os nomes do grupo (o
# enunciado garante que a mensagem contem os nossos nomes).
set -u
cd "$(dirname "$0")"

if [ $# -lt 1 ]; then
  echo "Uso: $0 <senha>"
  exit 1
fi
SENHA="$1"
INFILE="/home/eduarda/Documentos/CRIPTO/message.en"
OUTDIR="./tentativas_message"
mkdir -p "$OUTDIR"

# Cifras de bloco com padding (bate com os 1520 bytes, multiplo de 16)
CIPHERS=(
  aes-128-cbc aes-192-cbc aes-256-cbc
  aes-128-ecb aes-192-ecb aes-256-ecb
  des-cbc des-ecb des-ede3-cbc des-ede3-ecb des-ede-cbc des-ede-ecb
  bf-cbc bf-ecb
  cast5-cbc cast5-ecb
  camellia-128-cbc camellia-192-cbc camellia-256-cbc
  camellia-128-ecb camellia-192-ecb camellia-256-ecb
  aria-128-cbc aria-192-cbc aria-256-cbc
  aria-128-ecb aria-192-ecb aria-256-ecb
  sm4-cbc sm4-ecb
  seed-cbc seed-ecb
  rc2-cbc rc2-ecb
)

DIGESTS=(sha256 sha1 md5)

# Nomes dos integrantes - se aparecerem na saida, achamos a combinacao certa
NOMES_REGEX="eduarda|julia|brenda|rosa|silva|santos|souza"

acertos=0
tentativas=0

tentar() {
  local cipher="$1" ; shift
  local extra_args=("$@")
  local label
  label="${cipher}_$(echo "${extra_args[*]}" | tr ' /' '__')"
  local outfile="$OUTDIR/${label}.txt"
  tentativas=$((tentativas+1))
  openssl enc -d -"$cipher" -in "$INFILE" -pass "pass:$SENHA" \
    "${extra_args[@]}" -out "$outfile" 2>/dev/null
  if [ -s "$outfile" ] && grep -qiE "$NOMES_REGEX" "$outfile" 2>/dev/null; then
    echo ">>> SUCESSO: cifra=$cipher args='${extra_args[*]}' -> $outfile"
    echo "--- conteudo ---"
    cat "$outfile"
    echo "--- fim ---"
    acertos=$((acertos+1))
  fi
}

echo "[*] Testando ${#CIPHERS[@]} cifras x KDF legado/pbkdf2 x ${#DIGESTS[@]} digests..."

for cipher in "${CIPHERS[@]}"; do
  tentar "$cipher"
  for md in "${DIGESTS[@]}"; do
    tentar "$cipher" -md "$md"
  done
  for md in "${DIGESTS[@]}"; do
    tentar "$cipher" -pbkdf2 -md "$md"
  done
done

echo
echo "[*] Total de tentativas: $tentativas | Sucessos: $acertos"
if [ "$acertos" -eq 0 ]; then
  echo "[FALHA] Nenhuma combinacao produziu uma saida com os nomes esperados."
  echo "         Verificar se a senha/chave recuperada da Etapa 3 esta correta,"
  echo "         ou se key_for_message.en usa padding RSA (OAEP/PKCS1) que"
  echo "         precisa ser removido antes de usar os bytes como senha."
fi
