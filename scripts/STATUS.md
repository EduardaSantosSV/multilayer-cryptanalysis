# Status do Trabalho — Grupo 14 (Criptoanálise)

Última atualização: 28/10/2026 — **TRABALHO CONCLUÍDO**

Integrantes: Julia Brenda Souza da Rosa, Eduarda dos Santos da Silva
Entregável final: `../relatorio_grupo14.pdf` (23 páginas)

---

## Resumo dos resultados finais

| Etapa | Arquivo | Resultado |
|---|---|---|
| 1 | key_for_rsa_public.hash | Senha **`guysteelexxx`** (hash SHA-256) |
| 2 | key_public.en | **AES-256-CTR**, KDF legado EVP_BytesToKey, digest SHA-256 → chave pública RSA (N 382 bits, e=65537) |
| 3 | key_for_message.en | N fatorado (SIQS/yafu) → d → RSA decifra (padding **PKCS#1 v1.5**) → senha **`jackdongarra`** |
| 4 | message.en | **AES-256-CBC**, KDF legado, digest SHA-256, senha `jackdongarra` → **mensagem final** |

---

## Etapa 1 — Descobrir a senha  ✅ CONCLUÍDA

- Hash alvo: `befb7036...8e87e4` (SHA-256, 256 bits).
- Pista: senha começa com "gu".
- Senha: **`guysteelexxx`** (confirmada: SHA-256 bate com o hash alvo).
- Força bruta local (hashcat) e dicionários esgotaram o espaço viável sem
  achar; a senha acabou recuperada por força bruta GPU externa. Todas as
  tentativas que falharam estão documentadas no relatório (seções 4.1–4.4).
- Scripts: `crack_hash.py`, `etapa1_descobrir_senha.sh`.

## Etapa 2 — Decifrar key_public.en  ✅ CONCLUÍDA

- Estrutura: ciphertext de 157 bytes (primo, não múltiplo de 8/16) ⟹ cifra
  de fluxo / modo sem padding.
- Algoritmo: **AES-256-CTR**, KDF legado EVP_BytesToKey (sem PBKDF2),
  digest SHA-256 (padrão).
- Saída: chave pública RSA em PEM → **N = 382 bits**, **e = 65537**.
- Bug resolvido: combinar `-a -A` com `-provider legacy` causava falha
  silenciosa; corrigido decodificando o base64 antes e passando o binário.
- Scripts: `etapa2_analise_estrutural.sh`, `etapa2_decifrar_key_public.sh`.

## Etapa 3 — Fatorar o RSA / decifrar key_for_message.en  ✅ CONCLUÍDA

- N (382 bits) = p · q, com p e q de **191 bits cada** (equilibrados):
  - p = 2913273707204223987138708563885998591118852596104762121327
  - q = 3035927131115446151830465199210270095634389843965259549441
- **Métodos que falharam** (detalhados na seção 4.5 do relatório): factordb,
  divisão por tentativa, Fermat, Pollard rho, Pollard p-1, PARI/GP (MPQS
  desistiu), GMP-ECM (~13 h sem resultado), yafu via GNFS (faltava o siever
  externo `gnfs-lasieve4I12e`).
- **Método que funcionou**: `yafu v3.1.9` forçando **SIQS** com `siqs(N)`,
  12 threads → fatorou em ~11 h (39.946 s, ~299 mil relações).
- Com p, q → φ(N) → d (inverso de e mod φ). RSA decifra key_for_message.en;
  o bloco tem **padding PKCS#1 v1.5** (00 02 … 00 ‖ M). Mensagem = senha
  **`jackdongarra`**.
- Scripts: `etapa3_fatorar_rsa.py` (métodos Python); fatoração pesada feita
  com o yafu (comando documentado no relatório, seção 2.3).

## Etapa 4 — Decifrar message.en  ✅ CONCLUÍDA

- `message.en`: binário com cabeçalho `Salted__`, ciphertext de 1520 bytes
  (múltiplo de 16) ⟹ cifra de bloco com padding.
- Algoritmo: **AES-256-CBC**, KDF legado EVP_BytesToKey, digest SHA-256,
  senha `jackdongarra`.
- Mensagem final decifrada com sucesso — endereçada nominalmente ao Grupo 14
  (confirma a correção de todo o pipeline). Texto completo no relatório (3.3).
- Script: `etapa4_decifrar_message.sh "jackdongarra"`.

---

## Pipeline completo (replicável do zero)

```
# Etapa 1: senha = guysteelexxx (SHA-256 do hash alvo)

# Etapa 2: key_public.en -> chave publica RSA
./etapa2_decifrar_key_public.sh "guysteelexxx"
  -> AES-256-CTR; extrai N (382 bits) e e (65537) do PEM

# Etapa 3: fatorar N e decifrar key_for_message.en
#   fatoracao pesada (SIQS) feita com o yafu:
#   echo "siqs(<N>)" > batch.txt
#   ./yafu -threads 12 < batch.txt
#   -> p, q (191 bits cada)
./etapa3_fatorar_rsa.py --n <N> --e 65537 --c <hex de key_for_message.en>
  -> d, decifra (PKCS#1 v1.5) -> senha "jackdongarra"

# Etapa 4: mensagem final
./etapa4_decifrar_message.sh "jackdongarra"
  -> AES-256-CBC -> MENSAGEM FINAL (contem os nomes do grupo)
```

## Geração do relatório

```
python3 -m venv venv_pdf && venv_pdf/bin/pip install reportlab
venv_pdf/bin/python gerar_relatorio.py   # -> ../relatorio_grupo14.pdf
```

## Arquivos no diretório `scripts/`

- `crack_hash.py` — ataque de dicionário em Python (sha256/sha3_256/blake2s)
- `etapa1_descobrir_senha.sh` — roteiro completo de força bruta/dicionário (hashcat)
- `target_hash.txt` — hash alvo formatado para o hashcat
- `etapa2_analise_estrutural.sh` — análise de tamanhos/cabeçalhos dos arquivos cifrados
- `etapa2_decifrar_key_public.sh` — decifração de key_public.en (achou AES-256-CTR)
- `etapa3_fatorar_rsa.py` — fatoração RSA (Python) + recuperação de d + decifração RSA
- `etapa4_decifrar_message.sh` — decifração de message.en (achou AES-256-CBC)
- `gerar_relatorio.py` — gera o PDF final do trabalho
- `STATUS.md` — este arquivo
