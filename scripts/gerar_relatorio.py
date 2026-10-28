#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o PDF final do trabalho (Grupo 14 - Criptoanalise).

Uso:
    python3 gerar_relatorio.py

Requer reportlab (pip install reportlab, de preferencia numa venv:
    python3 -m venv venv_pdf && venv_pdf/bin/pip install reportlab
    venv_pdf/bin/python gerar_relatorio.py
).

Varios campos abaixo (marcados com [PENDENTE]) devem ser preenchidos
assim que tivermos a senha, a chave RSA e a mensagem final decifrada.
"""
import textwrap
from pathlib import Path
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Preformatted, XPreformatted, ListFlowable, ListItem,
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
OUT_PATH = PROJECT_DIR / "relatorio_grupo14.pdf"

# =============================================================================
# CAMPOS A PREENCHER QUANDO TIVERMOS O RESULTADO FINAL
# =============================================================================
SENHA_DESCOBERTA = "guysteelexxx"
ALGORITMO_HASH_SENHA = "SHA-256"
ALGORITMO_KEY_PUBLIC = "AES-256-CTR, KDF legado EVP_BytesToKey (sem PBKDF2), digest SHA-256 (padrão)"
MODULO_RSA_N = ("8844486688066579999081001449267985268759583045069232509539285795978980877251751417211616710762958318527583397028207"
                 "  (382 bits)")
EXPOENTE_RSA_E = "65537 (0x10001)"
FATORES_RSA_P_Q = (
    "p = 2913273707204223987138708563885998591118852596104762121327 (191 bits)<br/>"
    "q = 3035927131115446151830465199210270095634389843965259549441 (191 bits)<br/>"
    "Fatorado com yafu v3.1.9 (SIQS, 12 threads) em ~11 h (39.946 s)."
)
SENHA_MESSAGE_EN = "jackdongarra  (bloco RSA com padding PKCS#1 v1.5; senha = bytes após o separador 0x00)"
ALGORITMO_MESSAGE_EN = "AES-256-CBC, KDF legado EVP_BytesToKey (sem PBKDF2), digest SHA-256"
MENSAGEM_FINAL = """MENSAGEM CONFIDENCIAL — GRUPO 14
============================================================

Destinatários autorizados: Julia Brenda Souza da Rosa, Eduarda dos Santos da Silva

Classificação: ULTRA SECRETO
Protocolo: Biuro Szyfrów — Operação Enigma 2026-2

Prezados agentes,

A operação de interceptação foi bem-sucedida. Os dados coletados
confirmam que o sistema de criptografia inimigo utilizou chaves
RSA de baixa entropia combinadas com AES-256 para proteger as
comunicações. Esta combinação, embora aparentemente segura,
possui vulnerabilidades que podem ser exploradas sistematicamente.

Nossos analistas identificaram que a chave pública RSA pode ser
fatorada em tempo viável utilizando o algoritmo GNFS (General
Number Field Sieve). A senha utilizada para proteger esta chave
foi derivada de um espaço de busca limitado, permitindo ataques
de força bruta contra o hash armazenado.

Recomendações operacionais:
  1. Utilize ferramentas especializadas para recuperação da senha.
  2. Aplique algoritmos de fatoração para a chave RSA.
  3. Documente todos os procedimentos para replicabilidade.

Este documento foi gerado exclusivamente para o grupo 14
(Julia Brenda Souza da Rosa, Eduarda dos Santos da Silva). Qualquer compartilhamento não autorizado será
detectado através da análise forense dos metadados embutidos.

Assinado digitalmente,
Biuro Szyfrów — Divisão de Criptoanálise
Data: 11/10/2026
============================================================"""

# =============================================================================
# ESTILOS
# =============================================================================
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CapaTitulo", parent=styles["Title"], fontSize=22, leading=28,
    alignment=TA_CENTER, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="CapaSub", parent=styles["Normal"], fontSize=13, leading=18,
    alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="H1", parent=styles["Heading1"], fontSize=16, spaceBefore=18, spaceAfter=10,
    textColor=colors.HexColor("#1a1a2e"),
))
styles.add(ParagraphStyle(
    name="H2", parent=styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=6,
    textColor=colors.HexColor("#1a1a2e"),
))
styles.add(ParagraphStyle(
    name="Corpo", parent=styles["Normal"], fontSize=10.5, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="Codigo", parent=styles["Code"], fontSize=7, leading=8.4,
    fontName="Courier", backColor=colors.HexColor("#f4f4f8"),
    borderPadding=6, leftIndent=4,
))
styles.add(ParagraphStyle(
    name="Destaque", parent=styles["Normal"], fontSize=10.5, leading=15,
    backColor=colors.HexColor("#fff6d8"), borderPadding=8,
    spaceAfter=8, spaceBefore=4,
))
styles.add(ParagraphStyle(
    name="Legenda", parent=styles["Normal"], fontSize=8.5, leading=11,
    textColor=colors.HexColor("#555555"),
))
styles.add(ParagraphStyle(
    name="CelulaHead", parent=styles["Normal"], fontSize=8.5, leading=11,
    textColor=colors.white, fontName="Helvetica-Bold",
))
styles.add(ParagraphStyle(
    name="Celula", parent=styles["Normal"], fontSize=8.5, leading=11,
))
styles.add(ParagraphStyle(
    name="CelulaLabel", parent=styles["Normal"], fontSize=8.5, leading=11,
    fontName="Helvetica-Bold",
))


def head(text):
    return Paragraph(text, styles["CelulaHead"])


def cell(text):
    return Paragraph(text, styles["Celula"])


def label(text):
    return Paragraph(text, styles["CelulaLabel"])


story = []

# =============================================================================
# CAPA
# =============================================================================
story.append(Spacer(1, 5 * cm))
story.append(Paragraph("Trabalho de Criptoanálise", styles["CapaTitulo"]))
story.append(Paragraph("Grupo 14", styles["CapaTitulo"]))
story.append(Spacer(1, 1 * cm))
story.append(Paragraph(
    "Recuperação e decifração de mensagem confidencial<br/>"
    "interceptada pelo Biuro Szyfrów", styles["CapaSub"]))
story.append(Spacer(1, 2 * cm))
story.append(Paragraph("<b>Integrantes:</b>", styles["CapaSub"]))
story.append(Paragraph("Julia Brenda Souza da Rosa", styles["CapaSub"]))
story.append(Paragraph("Eduarda dos Santos da Silva", styles["CapaSub"]))
story.append(Spacer(1, 1 * cm))
story.append(Paragraph("<b>Disciplina:</b> Algoritmos e Estrutura de Dados III", styles["CapaSub"]))
story.append(Paragraph("<b>Professor:</b> Ulisses Brisolara Corrêa", styles["CapaSub"]))
story.append(Paragraph("<b>Universidade Federal de Pelotas (UFPEL)</b>", styles["CapaSub"]))
story.append(Spacer(1, 2 * cm))
story.append(Paragraph(date.today().strftime("%d/%m/%Y"), styles["CapaSub"]))
story.append(PageBreak())

# =============================================================================
# 1. INTRODUCAO
# =============================================================================
story.append(Paragraph("1. Introdução", styles["H1"]))
story.append(Paragraph(
    "Este relatório documenta o processo completo de criptoanálise realizado "
    "para recuperar e decifrar uma mensagem confidencial, conforme o cenário "
    "proposto: um criptoanalista do Biuro Szyfrów que intercepta uma mensagem "
    "protegida por múltiplas camadas de criptografia. Foram fornecidos quatro "
    "arquivos:", styles["Corpo"]))
story.append(ListFlowable([
    ListItem(Paragraph("<b>message.en</b> — a mensagem secreta cifrada", styles["Corpo"])),
    ListItem(Paragraph("<b>key_for_message.en</b> — a chave de decifração da mensagem, "
                        "protegida por criptografia de chave pública (RSA)", styles["Corpo"])),
    ListItem(Paragraph("<b>key_public.en</b> — a chave pública RSA correspondente, "
                        "protegida por criptografia simétrica (senha)", styles["Corpo"])),
    ListItem(Paragraph("<b>key_for_rsa_public.hash</b> — hash criptográfico da senha de "
                        "acesso à chave pública", styles["Corpo"])),
], bulletType="bullet"))
story.append(Paragraph(
    "Nenhum algoritmo, modo de operação, tamanho de chave ou codificação foi "
    "informado previamente — tudo precisou ser deduzido ou descoberto por "
    "tentativa sistemática, exceto o início da senha (“gu”), fornecido como "
    "pista inicial. O processo foi dividido em quatro etapas sequenciais, "
    "cada uma dependente do resultado da anterior:", styles["Corpo"]))
story.append(ListFlowable([
    ListItem(Paragraph("<b>Etapa 1:</b> descobrir a senha a partir do hash fornecido", styles["Corpo"])),
    ListItem(Paragraph("<b>Etapa 2:</b> usar a senha para decifrar key_public.en e obter a chave pública RSA", styles["Corpo"])),
    ListItem(Paragraph("<b>Etapa 3:</b> fatorar o módulo RSA, recuperar a chave privada e decifrar key_for_message.en", styles["Corpo"])),
    ListItem(Paragraph("<b>Etapa 4:</b> usar o resultado da Etapa 3 para decifrar message.en e obter a mensagem final", styles["Corpo"])),
], bulletType="1"))
story.append(PageBreak())

# =============================================================================
# 2. PROCEDIMENTOS (passo a passo replicavel)
# =============================================================================
story.append(Paragraph("2. Procedimentos executados", styles["H1"]))

story.append(Paragraph("2.1. Etapa 1 — Descoberta da senha", styles["H2"]))
story.append(Paragraph(
    "O arquivo <i>key_for_rsa_public.hash</i> contém uma string de 64 "
    "caracteres hexadecimais, equivalente a 32 bytes — tamanho de digest "
    "compatível com vários algoritmos de hash de 256 bits (SHA-256, "
    "SHA3-256, Keccak-256, BLAKE2s, BLAKE2b truncado, SHA-512/256, SM3, "
    "GOST Streebog-256, entre outros). A pista fornecida indicava que a "
    "senha começa com “gu”.", styles["Corpo"]))
story.append(Paragraph(
    "Passo a passo executado:", styles["Corpo"]))
story.append(ListFlowable([
    ListItem(Paragraph("Confirmar o tamanho do hash: <font face='Courier'>wc -c</font> "
                        "no arquivo e contagem de caracteres hex (64 → 32 bytes).", styles["Corpo"])),
    ListItem(Paragraph("Montar dicionários combinando wordlists do sistema "
                        "(português, inglês, cracklib) e o wordlist público "
                        "<i>rockyou.txt</i> (14,3 milhões de senhas reais vazadas), "
                        "filtrando por prefixo “gu” (script "
                        "<font face='Courier'>crack_hash.py</font>).", styles["Corpo"])),
    ListItem(Paragraph("Aplicar mutações de senha (maiúsculas/minúsculas, sufixos "
                        "numéricos e símbolos comuns) e regras do hashcat "
                        "(best64, rockyou-30000, dive — até 99 mil regras por palavra).",
                        styles["Corpo"])),
    ListItem(Paragraph("Rodar força bruta com máscara (hashcat -a 3) fixando o "
                        "prefixo “gu”/“Gu”/“GU” e variando o sufixo em três "
                        "conjuntos de caracteres (minúsculas+dígitos, "
                        "+maiúsculas, ASCII completo com símbolos), para "
                        "vários tamanhos totais de senha.", styles["Corpo"])),
    ListItem(Paragraph("Testar a mesma cobertura contra 7 algoritmos de hash "
                        "de 256 bits diferentes, não apenas SHA-256.", styles["Corpo"])),
    ListItem(Paragraph("Usar pistas de contexto (nome do professor, disciplina, "
                        "universidade, regionalismos do Rio Grande do Sul, "
                        "temática do Biuro Szyfrów em polonês) para gerar "
                        "candidatos temáticos adicionais.", styles["Corpo"])),
    ListItem(Paragraph("Estender a força bruta usando GPU (Google Colab, notebook "
                        "<font face='Courier'>colab_quebra_senha.ipynb</font>) para "
                        "cobrir tamanhos maiores de forma viável em tempo.", styles["Corpo"])),
], bulletType="1"))
story.append(Paragraph(
    f"<b>Resultado:</b> {SENHA_DESCOBERTA}", styles["Destaque"]))

story.append(Paragraph("2.2. Etapa 2 — Decifrar key_public.en", styles["H2"]))
story.append(Paragraph(
    "Antes de ter a senha, foi feita uma análise estrutural dos arquivos "
    "cifrados (tamanhos e cabeçalhos), que não depende de nenhuma senha:",
    styles["Corpo"]))
story.append(Table([
    [head("Arquivo"), head("Ciphertext"), head("Dedução")],
    [cell("message.en"), cell("1520 bytes (múltiplo de 16)"),
     cell("Cifra de bloco 128-bit com padding (CBC/ECB)")],
    [cell("key_public.en"), cell("157 bytes (primo, não múltiplo de 8 nem 16)"),
     cell("Sem padding de bloco — modo stream (CTR/CFB/OFB)")],
    [cell("key_for_message.en"), cell("48 bytes = 384 bits"),
     cell("Tamanho típico de ciphertext RSA cru — módulo provavelmente de 384 bits")],
], colWidths=[3.3*cm, 5.0*cm, 7.7*cm], style=TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f8")]),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
])))
story.append(Spacer(1, 10))
story.append(Paragraph(
    "A conclusão de que key_public.en usa um modo stream (sem padding) foi "
    "decisiva: ela elimina de imediato as combinações CBC/ECB (que exigiriam "
    "um ciphertext múltiplo do tamanho de bloco) e restringe a busca a "
    "cifras CTR/CFB/OFB/fluxo. Com a senha em mãos, o script "
    "<font face='Courier'>etapa2_decifrar_key_public.sh</font> testa "
    "sistematicamente ~37 cifras desse tipo (AES, ChaCha20, RC4, Blowfish, "
    "CAST5, DES, SM4, Camellia, ARIA, SEED) combinadas com KDF legado ou "
    "PBKDF2 e três opções de digest (sha256/sha1/md5), verificando se a "
    "saída contém um cabeçalho PEM de chave pública válido.", styles["Corpo"]))
story.append(Paragraph(
    f"<b>Algoritmo/modo identificado:</b> {ALGORITMO_KEY_PUBLIC}", styles["Destaque"]))

story.append(Paragraph("2.3. Etapa 3 — Fatorar o RSA e decifrar key_for_message.en", styles["H2"]))
story.append(Paragraph(
    "Com a chave pública em mãos (módulo N de 382 bits e expoente e extraídos "
    "do PEM), o script <font face='Courier'>etapa3_fatorar_rsa.py</font> tenta "
    "fatorar N em ordem crescente de custo computacional: consulta ao banco "
    "público factordb.com, divisão por tentativa, fatoração de Fermat "
    "(eficiente quando os primos p e q são próximos — um erro clássico de "
    "geração de chave), Pollard's rho e Pollard p-1 (eficiente quando p-1 "
    "ou q-1 é suave). <b>Nenhuma dessas técnicas rápidas funcionou</b>: o "
    "factordb não tinha a fatoração, não há fatores pequenos, p e q não são "
    "próximos e p-1/q-1 não são suaves. Isso mostra que a chave, apesar de "
    "curta, não possui as fraquezas estruturais clássicas — os dois primos "
    "são equilibrados (191 bits cada) e aparentemente aleatórios.", styles["Corpo"]))
story.append(Paragraph(
    "A fatoração exigiu, então, um algoritmo de crivo de propósito geral. "
    "Tentou-se ainda PARI/GP (<font face='Courier'>factor()</font>, que "
    "abandonou o MPQS por “número grande demais”) e GMP-ECM com B1 = 43.000.000 "
    "(ineficaz, pois o ECM é lento para semiprimos equilibrados — ~13 h sem "
    "resultado). A solução veio com o <font face='Courier'>yafu v3.1.9</font> "
    "forçando o <b>SIQS</b> (Self-Initializing Quadratic Sieve) com "
    "<font face='Courier'>siqs(N)</font> em 12 threads, que fatorou N em "
    "aproximadamente 11 horas (39.946 s), coletando ~299 mil relações. Esse é "
    "exatamente o tipo de ataque que a própria mensagem final descreve: um "
    "módulo RSA pequeno o bastante para cair diante de um crivo em um desktop "
    "comum.", styles["Corpo"]))
story.append(Paragraph(
    "Após obter p, q e calcular phi(N) = (p-1)(q-1), o expoente privado d "
    "é obtido pelo inverso modular de e em phi(N). Com (n, d) recuperados, "
    "o ciphertext hexadecimal de key_for_message.en é decifrado via RSA "
    "(m = c^d mod n). O bloco resultante começa com <font face='Courier'>00 02</font> "
    "seguido de bytes de preenchimento não-nulos, um separador "
    "<font face='Courier'>00</font> e, só então, a mensagem — isto é, "
    "<b>padding PKCS#1 v1.5</b> (tipo 2). Removendo o padding, obtém-se a "
    "senha em ASCII usada para cifrar message.en.", styles["Corpo"]))
story.append(Table([
    [label("Módulo N"), cell(MODULO_RSA_N)],
    [label("Expoente e"), cell(EXPOENTE_RSA_E)],
    [label("Fatores p, q"), cell(FATORES_RSA_P_Q)],
    [label("Senha/texto recuperado"), cell(SENHA_MESSAGE_EN)],
], colWidths=[4*cm, 12*cm], style=TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f4f4f8")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
])))

story.append(Paragraph("2.4. Etapa 4 — Decifrar message.en", styles["H2"]))
story.append(Paragraph(
    "message.en é um arquivo binário puro (sem base64), com cabeçalho "
    "“Salted__” + salt de 8 bytes idêntico ao formato usado em "
    "key_public.en — ou seja, também foi cifrado por senha via OpenSSL. "
    "Como a Etapa 3 produz uma senha/texto (não uma chave bruta), essa "
    "senha é usada diretamente. A análise estrutural indicou um ciphertext "
    "múltiplo exato de 16 bytes (ao contrário de key_public.en), apontando "
    "para uma cifra de bloco com padding (CBC/ECB) em vez de stream. O "
    "script <font face='Courier'>etapa4_decifrar_message.sh</font> testa "
    "~34 cifras de bloco (AES, DES/3DES, Blowfish, CAST5, Camellia, ARIA, "
    "SM4, SEED, RC2) x KDF legado/PBKDF2 x três digests, verificando "
    "automaticamente se a saída contém os nomes dos integrantes do grupo "
    "(garantido pelo enunciado).", styles["Corpo"]))
story.append(Paragraph(
    f"<b>Algoritmo/modo identificado:</b> {ALGORITMO_MESSAGE_EN}", styles["Destaque"]))
story.append(PageBreak())

# =============================================================================
# 3. RESULTADOS FINAIS
# =============================================================================
story.append(Paragraph("3. Resultados finais", styles["H1"]))
story.append(Paragraph("3.1. Senha descoberta (Etapa 1)", styles["H2"]))
story.append(Paragraph(SENHA_DESCOBERTA, styles["Destaque"]))
story.append(Paragraph(f"Algoritmo de hash: {ALGORITMO_HASH_SENHA}", styles["Corpo"]))

story.append(Paragraph("3.2. Algoritmos e codificações identificados", styles["H2"]))
story.append(Table([
    [head("Arquivo"), head("Algoritmo/modo"), head("Codificação")],
    [cell("key_for_rsa_public.hash"), cell(ALGORITMO_HASH_SENHA), cell("hexadecimal")],
    [cell("key_public.en"), cell(ALGORITMO_KEY_PUBLIC), cell("base64 (openssl enc)")],
    [cell("key_for_message.en"), cell("RSA 382 bits, padding PKCS#1 v1.5"), cell("hexadecimal")],
    [cell("message.en"), cell(ALGORITMO_MESSAGE_EN), cell("binário (openssl enc)")],
], colWidths=[4.0*cm, 7.5*cm, 4.5*cm], style=TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f8")]),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
])))
story.append(Spacer(1, 10))

story.append(Paragraph("3.3. Mensagem decifrada (completa)", styles["H2"]))
_msg_style = ParagraphStyle(
    "MensagemFinal", parent=styles["Normal"], fontName="Courier", fontSize=8,
    leading=11, textColor=colors.HexColor("#1a1a2e"),
    backColor=colors.HexColor("#f4f4f8"),
    borderColor=colors.HexColor("#1a1a2e"), borderWidth=0.8, borderPadding=10,
    spaceBefore=6, spaceAfter=6,
)
story.append(XPreformatted(MENSAGEM_FINAL, _msg_style))
story.append(PageBreak())

# =============================================================================
# 4. CAMINHOS QUE NAO FUNCIONARAM
# =============================================================================
story.append(Paragraph("4. Caminhos tentados que não funcionaram", styles["H1"]))
story.append(Paragraph(
    "Diversas abordagens foram tentadas e eliminadas sistematicamente "
    "antes de se chegar aos resultados finais, nas três etapas de "
    "criptoanálise (descoberta da senha, decifração de key_public.en e "
    "fatoração do RSA). As três primeiras são detalhadas individualmente "
    "abaixo; em seguida, resumem-se as demais tentativas da Etapa 1 (4.4) e "
    "da Etapa 3 (4.5), sempre com a explicação técnica do motivo da falha.",
    styles["Corpo"]))

story.append(Paragraph(
    "4.1. Força bruta combinando tamanhos 10 a 12 em um único comando hashcat",
    styles["H2"]))
story.append(Paragraph(
    "<b>O que foi tentado:</b> rodar <font face='Courier'>hashcat --increment "
    "--increment-min=10 --increment-max=12</font> em uma única execução, "
    "assumindo que estender a cobertura de tamanho da senha de 10 para 12 "
    "caracteres seria uma extensão incremental barata.", styles["Corpo"]))
story.append(Paragraph(
    "<b>Por que falhou (ficou impraticável):</b> o espaço de busca cresce "
    "exponencialmente com o tamanho. Para o alfabeto minúsculas+dígitos "
    "(36 símbolos), o tamanho 10 tem 36^8 ≈ 2,8 trilhões de combinações "
    "(levou ~19 minutos numa GPU a 2,47 GH/s), mas o tamanho 11 tem "
    "36^9 ≈ 101 trilhões (~11-12 horas) e o tamanho 12 tem 36^10 ≈ 3,6 "
    "quatrilhões (~17 dias) — na MESMA GPU. Como o hashcat processa os "
    "tamanhos em ordem crescente dentro de um único comando, o tamanho 12 "
    "só começaria a ser testado depois de completar o 10 e o 11, tornando a "
    "execução conjunta inviável. A lição técnica é que o tempo de uma "
    "força bruta por máscara cresce multiplicativamente a cada caractere "
    "adicional do alfabeto (fator 36x por posição, nesse caso), então "
    "somar vários tamanhos “grandes” no mesmo comando não é uma extensão "
    "linear e pode facilmente ultrapassar o tempo disponível. A solução foi "
    "isolar cada tamanho em comandos separados e avaliar o custo "
    "individualmente antes de rodar.", styles["Corpo"]))

story.append(Paragraph(
    "4.2. Colisão de instâncias do hashcat ao rodar ataques em paralelo",
    styles["H2"]))
story.append(Paragraph(
    "<b>O que foi tentado:</b> disparar duas execuções do hashcat "
    "simultaneamente em segundo plano (uma testando o alfabeto "
    "minúsculas+dígitos e outra minúsculas+MAIÚSCULAS+dígitos) para "
    "paralelizar o trabalho e economizar tempo total.", styles["Corpo"]))
story.append(Paragraph(
    "<b>Por que falhou:</b> o hashcat usa, por padrão, um arquivo de lock "
    "de instância única (verificado pela mensagem de erro “Already an "
    "instance '/usr/bin/hashcat' running”). A segunda execução encerrou "
    "imediatamente com código de saída 1, sem processar nenhuma "
    "combinação, enquanto a primeira ainda estava rodando — o que, sem "
    "verificação cuidadosa dos logs, poderia ter sido confundido com uma "
    "faixa de senha genuinamente “esgotada sem sucesso” quando na "
    "verdade ela nunca chegou a ser testada. A lição técnica é que "
    "ferramentas de GPU/OpenCL frequentemente assumem acesso exclusivo ao "
    "dispositivo e não paralelizam automaticamente entre processos "
    "separados; a solução foi rodar as tentativas estritamente em "
    "sequência, sempre conferindo o log completo (não só o código de saída) "
    "antes de considerar uma faixa como “testada”.", styles["Corpo"]))

story.append(Paragraph(
    "4.3. Falso negativo na Etapa 2: bug do OpenSSL ao combinar -a/-A com -provider",
    styles["H2"]))
story.append(Paragraph(
    "<b>O que foi tentado:</b> depois de obter a senha (Etapa 1), o script "
    "de decifração de key_public.en combinava as flags <font face='Courier'>"
    "-a -A</font> (decodificação base64 embutida no próprio comando "
    "<font face='Courier'>openssl enc</font>) com <font face='Courier'>"
    "-provider legacy -provider default</font> (necessário para habilitar "
    "cifras mais antigas como RC4/DES/Blowfish, movidas para um provider "
    "separado desde o OpenSSL 3.0).", styles["Corpo"]))
story.append(Paragraph(
    "<b>Por que falhou:</b> essa combinação específica de flags produz o "
    "erro silencioso “error reading input file” em todas as 259 "
    "combinações de cifra/KDF testadas - inclusive para cifras padrão como "
    "AES, que definitivamente não deveriam falhar. Como o script apenas "
    "verificava se o arquivo de saída continha uma chave PEM válida (sem "
    "checar o código de retorno do openssl), todas as tentativas "
    "simplesmente produziam arquivos vazios e eram silenciosamente "
    "contadas como “não bateu”, quando na verdade nenhuma delas chegou a "
    "executar de fato. Isso é particularmente traiçoeiro: o resultado "
    "(0 sucessos) é indistinguível de uma senha errada, levando a se "
    "questionar a senha descoberta na Etapa 1 quando na verdade o "
    "problema era puramente operacional. A causa raiz parece ser uma "
    "incompatibilidade entre o parser de base64 embutido do "
    "<font face='Courier'>openssl enc</font> e o carregamento explícito de "
    "providers nesta versão (OpenSSL 3.0.13). A solução foi decodificar o "
    "base64 manualmente com <font face='Courier'>base64 -d</font> antes de "
    "invocar o <font face='Courier'>openssl enc</font> diretamente sobre o "
    "binário já decodificado (sem as flags -a/-A), o que eliminou o "
    "erro. A lição técnica, reforçada aqui, é sempre verificar o código de "
    "saída e o stderr de cada tentativa automatizada, não apenas o "
    "resultado esperado - um “não encontrado” pode ser um falso negativo "
    "por falha de execução, não por hipótese incorreta.", styles["Corpo"]))

story.append(Paragraph(
    "4.4. Resumo de outras tentativas sem sucesso (Etapa 1)", styles["H2"]))
story.append(Paragraph(
    "Além dos dois casos detalhados acima, as seguintes abordagens também "
    "foram testadas e eliminadas, sem apresentar uma falha técnica "
    "“interessante” em si (apenas não bateram com o hash-alvo):",
    styles["Corpo"]))
story.append(ListFlowable([
    ListItem(Paragraph("Dicionário rockyou.txt completo (14,3 milhões de senhas "
                        "reais vazadas), filtrado por prefixo “gu”, combinado "
                        "com até 99 mil regras de mutação do hashcat (~3 "
                        "bilhões de variações testadas).", styles["Corpo"])),
    ListItem(Paragraph("7 algoritmos de hash de 256 bits diferentes (SHA-256, "
                        "SHA3-256, Keccak-256, BLAKE2s, BLAKE2b truncado, "
                        "SHA-512/256, SM3, GOST Streebog-256).", styles["Corpo"])),
    ListItem(Paragraph("Candidatos temáticos manuais em português, inglês, "
                        "alemão e polonês relacionados ao contexto do "
                        "enunciado (Biuro Szyfrów, nomes do grupo, nome do "
                        "professor/disciplina/universidade, regionalismos do "
                        "Rio Grande do Sul).", styles["Corpo"])),
    ListItem(Paragraph("Variações de encoding (senha com/sem quebra de linha "
                        "antes do hash, UTF-8) e de hash truncado/duplo/"
                        "salgado com o nome do arquivo.",
                        styles["Corpo"])),
], bulletType="bullet"))

story.append(Paragraph(
    "4.5. Tentativas de fatoração que falharam (Etapa 3)", styles["H2"]))
story.append(Paragraph(
    "A fatoração do módulo RSA de 382 bits foi a parte mais custosa do "
    "trabalho. Antes de chegar à técnica que funcionou (SIQS), várias "
    "abordagens mais baratas foram tentadas e descartadas — cada uma por um "
    "motivo técnico específico, documentado abaixo:", styles["Corpo"]))
story.append(ListFlowable([
    ListItem(Paragraph("<b>factordb.com:</b> o módulo não constava no banco "
                        "público de fatorações (status “C”, composto não "
                        "fatorado). Não é um módulo reaproveitado/conhecido.",
                        styles["Corpo"])),
    ListItem(Paragraph("<b>Divisão por tentativa (até 2 milhões):</b> não há "
                        "fatores pequenos — os dois primos têm 191 bits.",
                        styles["Corpo"])),
    ListItem(Paragraph("<b>Fatoração de Fermat (5 milhões de iterações):</b> "
                        "falhou porque p e q não são próximos entre si "
                        "(|p − q| é da ordem de 10^56). Fermat só é eficiente "
                        "quando os primos estão muito próximos de √N.",
                        styles["Corpo"])),
    ListItem(Paragraph("<b>Pollard's rho e Pollard p−1:</b> ineficazes para "
                        "fatores de 191 bits; o p−1 em particular exigiria que "
                        "p−1 ou q−1 fosse “suave” (só fatores pequenos), o que "
                        "não ocorre.", styles["Corpo"])),
    ListItem(Paragraph("<b>PARI/GP factor():</b> abandonou o crivo MPQS com a "
                        "mensagem “number too big to be factored with MPQS, "
                        "giving up” — a implementação do MPQS no PARI tem um "
                        "teto de tamanho abaixo do nosso N.", styles["Corpo"])),
    ListItem(Paragraph("<b>GMP-ECM (B1 = 43.000.000, curvas ilimitadas):</b> "
                        "rodou ~13 h sem achar fator. O método das curvas "
                        "elípticas é rápido quando existe um fator "
                        "relativamente pequeno, mas é ineficiente para "
                        "semiprimos equilibrados (dois fatores do mesmo "
                        "tamanho), que é justamente o nosso caso.",
                        styles["Corpo"])),
    ListItem(Paragraph("<b>yafu com GNFS (tentativa inicial):</b> o binário "
                        "pré-compilado do yafu não inclui o <i>lattice "
                        "siever</i> externo (<font face='Courier'>"
                        "gnfs-lasieve4I12e</font>) do projeto GGNFS; sem ele, "
                        "a etapa de sieving do GNFS aborta "
                        "(<font face='Courier'>ggnfs returned code 32512</font>). "
                        "A saída foi forçar o SIQS, que é autocontido.",
                        styles["Corpo"])),
], bulletType="bullet"))
story.append(Paragraph(
    "Conclusão: o módulo não é “fraco” no sentido clássico (sem primos "
    "próximos, sem suavidade, sem fator pequeno). Ele é simplesmente "
    "<b>curto demais</b> (382 bits) para os padrões atuais, e por isso cedeu "
    "a um crivo quadrático de propósito geral rodando poucas horas num "
    "computador comum.", styles["Corpo"]))
story.append(PageBreak())

# =============================================================================
# 5. APENDICE - CODIGO-FONTE COMPLETO
# =============================================================================
story.append(Paragraph("5. Apêndice — Código-fonte completo", styles["H1"]))

SCRIPTS = [
    ("crack_hash.py", "Etapa 1 — ataque de dicionário em Python"),
    ("etapa1_descobrir_senha.sh", "Etapa 1 — roteiro de força bruta/dicionário (hashcat)"),
    ("etapa2_analise_estrutural.sh", "Etapa 2 — análise estrutural dos arquivos cifrados"),
    ("etapa2_decifrar_key_public.sh", "Etapa 2 — decifração automática de key_public.en"),
    ("etapa3_fatorar_rsa.py", "Etapa 3 — fatoração do módulo RSA e decifração de key_for_message.en"),
    ("etapa4_decifrar_message.sh", "Etapa 4 — decifração automática de message.en"),
]

WRAP_WIDTH = 100

for idx, (fname, desc) in enumerate(SCRIPTS, start=1):
    path = BASE_DIR / fname
    story.append(Paragraph(f"5.{idx}. {fname}", styles["H2"]))
    story.append(Paragraph(desc, styles["Legenda"]))
    story.append(Spacer(1, 4))
    if path.exists():
        raw = path.read_text(encoding="utf-8")
        wrapped_lines = []
        for line in raw.split("\n"):
            if len(line) <= WRAP_WIDTH:
                wrapped_lines.append(line)
            else:
                wrapped_lines.extend(textwrap.wrap(
                    line, WRAP_WIDTH, subsequent_indent="    ",
                    break_long_words=True, break_on_hyphens=False))
        code_text = "\n".join(wrapped_lines)
        story.append(Preformatted(code_text, styles["Codigo"]))
    else:
        story.append(Paragraph(f"[arquivo {fname} não encontrado]", styles["Corpo"]))
    story.append(PageBreak())


# =============================================================================
# BUILD
# =============================================================================
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawRightString(A4[0] - 2 * cm, 1.3 * cm, f"Página {doc.page}")
    canvas.drawString(2 * cm, 1.3 * cm, "Trabalho de Criptoanálise — Grupo 14")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUT_PATH), pagesize=A4,
    topMargin=2.2 * cm, bottomMargin=2.2 * cm,
    leftMargin=2.2 * cm, rightMargin=2.2 * cm,
    title="Trabalho de Criptoanálise — Grupo 14",
    author="Julia Brenda Souza da Rosa, Eduarda dos Santos da Silva",
)
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"PDF gerado em: {OUT_PATH}")
