# Quebra da senha por forca bruta na GPU (Google Colab)
#
# A ideia foi usar a GPU gratis do Colab (Tesla T4) pra rodar o hashcat bem
# mais rapido do que no nosso notebook. Como a senha comeca com "gu" e a gente
# ja tinha descartado os tamanhos menores rodando no CPU/GPU local, aqui a
# gente focou na mascara de 10 minusculas depois do "gu".
#
# Isso aqui veio de um notebook do Colab (.ipynb), as linhas que comecam com
# "!" sao comandos de shell e o resto e Python. Pra rodar: Ambiente de
# execucao -> Alterar tipo -> GPU, e ir rodando celula por celula.

# ver qual GPU o Colab deu dessa vez
get_ipython().system('nvidia-smi')

# instala o hashcat
get_ipython().system('apt-get install -y hashcat')

# confere se ele enxerga a GPU (tem que aparecer a Tesla T4 no OpenCL)
get_ipython().system('hashcat -I')

# grava o hash alvo num arquivo
with open("hash.txt", "w") as f:
    f.write("befb7036fb77a8517e95d9dbb797031850fce2ecdb988e96d7f040a2608e87e4")

get_ipython().system('cat hash.txt')

# monta o Drive pra salvar o progresso (se a sessao do Colab cair, da pra retomar)
from google.colab import drive
drive.mount('/content/drive')

get_ipython().system('mkdir -p /content/drive/MyDrive/hashcat_progresso')
get_ipython().system('ls /content/drive/MyDrive/hashcat_progresso')

# ataque de mascara: "gu" + 10 minusculas (?l)
#   -m 1400  -> SHA-256
#   -a 3     -> mascara (forca bruta)
#   -O       -> kernel otimizado (mais rapido)
#   -w 3     -> workload alto
#   --session + --restore-file-path -> salva o estado pra conseguir retomar
get_ipython().system('hashcat -m 1400 -a 3 hash.txt "gu?l?l?l?l?l?l?l?l?l?l" -O -w 3 -d 1 '
                      '--session=gpu_colab '
                      '--restore-file-path=/content/drive/MyDrive/hashcat_progresso/gpu_colab.restore')
