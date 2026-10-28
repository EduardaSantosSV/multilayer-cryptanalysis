#!/usr/bin/env bash
# Etapa 2 - decifra key_public.en (precisa da senha da Etapa 1).
# Uso: ./etapa2_decifrar_key_public.sh "senha"
#
# O ciphertext tem 157 bytes (nao multiplo de 8/16), entao e modo de fluxo
# (CTR/CFB/OFB), sem padding. O script testa varias cifras de fluxo x KDF
# (legado/pbkdf2) x digest e ve qual produz uma chave publica PEM/DER valida.
set -u
cd "$(dirname "$0")"

if [ $# -lt 1 ]; then
  echo "Uso: $0 <senha>"
  exit 1
fi
SENHA="$1"
INFILE_B64="/home/eduarda/Documentos/CRIPTO/key_public.en"
OUTDIR="./tentativas_key_public"
mkdir -p "$OUTDIR"

# Decodifica o base64 uma vez so. (Usar "-a -A" junto com "-provider legacy"
# dava "error reading input file" nesta versao do openssl, entao decodificamos
# na mao e passamos o binario direto.)
INFILE="$OUTDIR/_key_public_decoded.bin"
base64 -d "$INFILE_B64" > "$INFILE"

# Cifras de fluxo / sem padding de bloco (bate com os 157 bytes, que nao sao multiplos de 8/16)
CIPHERS=(
  aes-128-ctr aes-192-ctr aes-256-ctr
  aes-128-cfb aes-192-cfb aes-256-cfb
  aes-128-cfb8 aes-192-cfb8 aes-256-cfb8
  aes-128-ofb aes-192-ofb aes-256-ofb
  chacha20
  rc4 rc4-40
  bf-cfb bf-ofb
  cast5-cfb cast5-ofb
  des-cfb des-ofb des-ede3-cfb des-ede3-ofb
  sm4-ctr sm4-cfb sm4-ofb
  camellia-128-ctr camellia-192-ctr camellia-256-ctr
  camellia-128-cfb camellia-256-cfb
  camellia-128-ofb camellia-256-ofb
  aria-128-ctr aria-256-ctr
  seed-cfb seed-ofb
)

DIGESTS=(sha256 sha1 md5 sha512)
ITERS=(1 1000 4096 10000 50000 100000 250000 600000)

acertos=0
tentativas=0

tentar() {
  local cipher="$1" ; shift
  local extra_args=("$@")
  local label
  label="${cipher}_$(echo "${extra_args[*]}" | tr ' /' '__')"
  local outfile="$OUTDIR/${label}.pem"
  tentativas=$((tentativas+1))
  openssl enc -d -"$cipher" -in "$INFILE" -pass "pass:$SENHA" \
    -provider legacy -provider default \
    "${extra_args[@]}" -out "$outfile" 2>/dev/null
  if [ ! -s "$outfile" ]; then
    return
  fi
  if grep -q "BEGIN.*PUBLIC KEY" "$outfile" 2>/dev/null; then
    echo ">>> SUCESSO (PEM): cifra=$cipher args='${extra_args[*]}' -> $outfile"
    cat "$outfile"
    acertos=$((acertos+1))
    return
  fi
  # chave DER comeca com 0x30 (SEQUENCE do ASN.1); confirma com o openssl
  primeiro_byte=$(xxd -p -l1 "$outfile" 2>/dev/null)
  if [ "$primeiro_byte" = "30" ]; then
    if openssl pkey -pubin -inform DER -in "$outfile" -noout 2>/dev/null; then
      echo ">>> SUCESSO (DER): cifra=$cipher args='${extra_args[*]}' -> $outfile"
      openssl pkey -pubin -inform DER -in "$outfile" -text -noout 2>/dev/null
      acertos=$((acertos+1))
      return
    fi
  fi
}

echo "[*] Testando ${#CIPHERS[@]} cifras x KDF legado/pbkdf2 x ${#DIGESTS[@]} digests..."

for cipher in "${CIPHERS[@]}"; do
  # KDF legado, sem passar -md (usa o digest padrao do openssl)
  tentar "$cipher"
  # KDF legado, variando -md
  for md in "${DIGESTS[@]}"; do
    tentar "$cipher" -md "$md"
  done
  # PBKDF2 (openssl >= 1.1.0), com -md e variando -iter
  for md in "${DIGESTS[@]}"; do
    for it in "${ITERS[@]}"; do
      tentar "$cipher" -pbkdf2 -md "$md" -iter "$it"
    done
  done
done

echo
echo "[*] Total de tentativas: $tentativas | Sucessos: $acertos"
if [ "$acertos" -eq 0 ]; then
  echo "[FALHA] Nenhuma combinacao de cifra/KDF/digest produziu uma chave PEM/DER valida."
  echo
  echo "[*] Top 5 saidas mais 'parecidas com texto' (proporcao de bytes imprimiveis),"
  echo "    pra olhar na mao - a certa fica com proporcao perto de 1.0:"
  for f in "$OUTDIR"/*.pem; do
    [ -s "$f" ] || continue
    total=$(wc -c < "$f")
    printaveis=$(tr -dc '[:print:]\n' < "$f" | wc -c)
    razao=$(awk -v p="$printaveis" -v t="$total" 'BEGIN{printf "%.3f", p/t}')
    echo "$razao $f"
  done | sort -rn | head -5 | while read -r razao f; do
    echo "  razao=$razao  $f"
  done
fi
