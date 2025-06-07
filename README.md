+# Leitor de Hiscon
+
+Este repositório contém um conjunto de scripts em Python para extração de
+informações de documentos jurídicos em português e geração de um arquivo JSON
+estruturado. A aplicação possui uma interface gráfica simples desenvolvida com
+Tkinter, permitindo colar trechos de texto, gerar o JSON correspondente e
+armazenar os dados coletados em arquivos locais.
+
+## Principais Funcionalidades
+
+- **Extração de dados**: o módulo `extraction.py` analisa o texto de entrada e
+  identifica dados do cliente e do "desfavor" (geralmente instituições
+  financeiras), incluindo nome, documentos (CPF/CNPJ, RG), endereço e valores da
+  ação.
+- **Processamento de endereço**: `address_processing.py` possui rotinas para
+  normalizar e separar rua, número, bairro, cidade, UF e CEP a partir de uma
+  descrição textual.
+- **Normalização de dados**: utilitários em `utils.py` padronizam nomes,
+  CNPJ/CPF e outras informações, além de manter bancos de dados auxiliares em
+  `bancos_maps.json` e `foro.json`.
+- **Interface gráfica**: `gui.py` disponibiliza uma janela com abas para gerar
+  o JSON, editar/cadastrar bancos e gerenciar a lista de foros. O resultado pode
+  ser salvo em `json_gerado.json`.
+
+## Estrutura do JSON
+
+O resultado da extração segue o formato abaixo:
+
+```json
+{
+  "cliente": {
+    "nome": "...",
+    "cpf": "...",
+    "rg": "...",
+    "nacionalidade": "...",
+    "estadoCivil": "...",
+    "sexo": "...",
+    "profissao": "...",
+    "endereco": {
+      "rua": "...",
+      "numero": "...",
+      "bairro": "...",
+      "cidade": "...",
+      "uf": "...",
+      "cep": "..."
+    }
+  },
+  "producaoAntecipadaDeProvas": {
+    "desfavor": {
+      "nome": "...",
+      "cidade": "...",
+      "uf": "...",
+      "cnpj": "...",
+      "endereco": {
+        "rua": "...",
+        "numero": "...",
+        "bairro": "...",
+        "cep": "..."
+      },
+      "valorAcao": "...",
+      "foroDeCompetencia": "..."
+    }
+  }
+}
+```
+
+## Como Executar
+
+1. Certifique‑se de ter o **Python 3** instalado.
+2. No diretório do projeto, execute:
+
+```bash
+python gui.py
+```
+
+3. Na janela que será aberta, cole o texto desejado ou a lista de textos,
+   clique em **"Gerar JSON"** e acompanhe o log de processamento.
+   É possível ainda editar ou cadastrar novos bancos e foros pelas abas
+   correspondentes.
+
+Os dados extraídos podem ser consultados no arquivo `json_gerado.json`, que é
+atualizado a cada nova geração.
+
+## Licença
+
+Este projeto foi disponibilizado sem um arquivo de licença específico.
+Consulte o autor caso deseje utilizá‑lo em outros projetos.
 
EOF
)
