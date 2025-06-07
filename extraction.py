import os
import re
import json
from utils import normalize_input, normalize_nome, normalize_cnpj
from address_processing import process_address
from data_processing import detect_sexo, format_valor
from constants import cnpj_regex
from utils import normalizar_foro
from utils import log_message
from utils import buscar_cliente_por_cpf
from utils import buscar_no_bancos_maps, buscar_no_json_gerado, logar_correcao_de_campo


def obter_caminho_json(nome_arquivo='bancos_maps.json'):
    """Retorna o caminho absoluto para o arquivo JSON, na pasta do módulo."""
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(diretorio_atual, nome_arquivo)

def carregar_base_bancos(caminho_json=None):
    """
    Carrega a base de dados a partir do arquivo JSON.
    Se o arquivo não existir, cria-o com um dicionário vazio.
    """
    if caminho_json is None:
        caminho_json = obter_caminho_json()
    if not os.path.exists(caminho_json):
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}
    with open(caminho_json, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)

def carregar_banco(log_func=None):
    """
    Carrega a base de dados do arquivo 'dados_bancos.json' e, se log_func for fornecido,
    envia uma mensagem de sucesso ou erro.
    """
    global _bancos_db
    try:
        caminho_json = obter_caminho_json()
        _bancos_db = carregar_base_bancos(caminho_json)
        message = "Base de dados carregada com sucesso"
    except Exception as e:
        _bancos_db = {}
        message = "Erro ao carregar a base de dados: " + str(e)
    if log_func and callable(log_func):
        log_func(message)
    else:
        print(message)
    return _bancos_db

def buscar_info_banco(nome_ou_cnpj, base=None):
    """
    Busca informações de um banco utilizando parte do nome ou o CNPJ.
    Se a base não for fornecida, recarrega o arquivo atualizado.
    """
    if base is None:
        base = carregar_base_bancos()
    for nome_banco, dados in base.items():
        if nome_ou_cnpj.upper() in nome_banco.upper() or dados["cnpj"] == nome_ou_cnpj:
            resultado = dados.copy()
            resultado["nome"] = nome_banco
            return resultado
    return {}

def editar_banco(cnpj, novos_dados, caminho_json=None):
    """
    Edita os dados de um banco no arquivo JSON com base no CNPJ.
    """
    if caminho_json is None:
        caminho_json = obter_caminho_json()
    bancos = carregar_base_bancos(caminho_json)
    for nome_banco, dados in bancos.items():
        if dados["cnpj"] == cnpj:
            dados.update(novos_dados)
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(bancos, f, ensure_ascii=False, indent=2)
            return True
    return False

def cadastrar_banco(nome_banco, dados_banco, caminho_json=None):
    """
    Cadastra um novo banco no arquivo JSON.
    """
    if caminho_json is None:
        caminho_json = obter_caminho_json()
    bancos = carregar_base_bancos(caminho_json)
    if nome_banco not in bancos:
        bancos[nome_banco] = dados_banco
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(bancos, f, ensure_ascii=False, indent=2)
        return True
    return False

def preencher_dados_desfavor(desfavor):
    """
    Verifica e preenche TODOS os campos do desfavor que estejam vazios ou com espaços,
    utilizando os dados do arquivo atualizado de bancos.
    
    Preenche:
      - Campos de nível superior: cidade, uf, complemento, telefone, email.
      - Dados do endereço: rua, numero, bairro e cep.
    """
    if not desfavor.get("cnpj", "").strip():
         return desfavor

    base = carregar_base_bancos()
    cnpj_extraido = normalize_cnpj(desfavor["cnpj"])
    for bank_name, bank_info in base.items():
         if normalize_cnpj(bank_info.get("cnpj", "")) == cnpj_extraido:
             for campo in ["cidade", "uf"]:
                 if not desfavor.get(campo, "").strip():
                     desfavor[campo] = bank_info.get(campo, "").strip().upper()
             
             endereco = desfavor.get("endereco", {})
             for campo, banco_campo in [("rua", "logradouro"),
                                        ("numero", "numero"),
                                        ("bairro", "bairro"),
                                        ("cep", "cep")]:
                 valor_atual = endereco.get(campo, "")
                 if not valor_atual.strip() or (campo == "numero" and valor_atual.strip() == "S/N"):
                     valor = bank_info.get(banco_campo, "").strip()
                     if campo in ["rua", "bairro"]:
                         valor = valor.upper()
                     endereco[campo] = valor
             desfavor["endereco"] = endereco
             
             for campo in ["complemento", "telefone", "email"]:
                 if not desfavor.get(campo, "").strip():
                     desfavor[campo] = bank_info.get(campo, "").strip()
             break
    return desfavor

def extrair_dados_cliente(texto):
    texto = normalize_input(texto)
    client_text = texto.split("inscrito no RG de nº")[0]
    if not client_text.strip():
        client_text = texto
    name_matches = re.findall(r"([A-Z][A-ZÀ-Ú\s]+?)(?=,\s*BRASILEIR[OA])", client_text, re.IGNORECASE)
    client_name = normalize_nome(name_matches[-1]) if name_matches else ""
    if not client_name:
        alt_name = re.findall(r"([A-Z][A-ZÀ-Ú\s]+)", client_text)
        client_name = normalize_nome(alt_name[0]) if alt_name else ""
    info_match = re.search(
        r",\s*(BRASILEIR[OA]|PORTUGU[EÉ]S[OA]?|ARGENTIN[OA]?)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,",
        client_text, re.IGNORECASE
    )
    if info_match:
        nacionalidade = info_match.group(1).strip().upper()
        estadoCivil = info_match.group(2).strip().upper()
        profissao = info_match.group(3).strip().upper()
    else:
        parts = client_text.split(',')
        if len(parts) >= 4:
            nacionalidade = parts[1].strip().upper()
            estadoCivil = parts[2].strip().upper()
            profissao = parts[3].strip().upper()
        else:
            nacionalidade = estadoCivil = profissao = ""
    rg_match = re.search(r'RG de nº\s*([\d\.\-Xx]+)', texto)
    rg = rg_match.group(1).strip().upper() if rg_match else ""
    cpf_match = re.search(r'CPF(?:\s*/MF)?\s*sob o nº\s*([\d\.]+-\s*\d{2})', texto, re.IGNORECASE)
    cpf = cpf_match.group(1).replace(" ", "").upper() if cpf_match else ""
    client_addr_match = re.search(r"domiciliado na\s+(.*?)(?=,\s+neste ato)", texto, re.IGNORECASE | re.DOTALL)
    if client_addr_match:
        client_addr_str = client_addr_match.group(1)
        client_address = process_address(client_addr_str)
    else:
        client_address = {"rua": "", "numero": "", "bairro": "", "cidade": "", "uf": "SP", "cep": ""}
    alt_match = re.search(r"domiciliado na\s+(.*?)(?=,\s+procurador)", texto, re.IGNORECASE | re.DOTALL)
    if alt_match:
        alt_address = process_address(alt_match.group(1))
        for key, value in alt_address.items():
            if not client_address.get(key):
                client_address[key] = value
    sexo = detect_sexo(nacionalidade, estadoCivil, client_name)
    cliente = {
        "nome": client_name,
        "cpf": cpf,
        "rg": rg,
        "nacionalidade": nacionalidade,
        "estadoCivil": estadoCivil,
        "sexo": sexo,
        "profissao": profissao,
        "endereco": client_address
    }
    
    cliente_salvo = buscar_cliente_por_cpf(cpf)

    if cliente_salvo:
        for campo in cliente:
            if not cliente[campo] and campo in cliente_salvo:
                cliente[campo] = cliente_salvo[campo]

        # Subcampos do endereço
        if "endereco" in cliente_salvo and isinstance(cliente_salvo["endereco"], dict):
            for subcampo in cliente["endereco"]:
                if not cliente["endereco"].get(subcampo) and subcampo in cliente_salvo["endereco"]:
                    cliente["endereco"][subcampo] = cliente_salvo["endereco"][subcampo]
    return cliente

def extrair_dados_desfavor(texto, logs_widget=None):
    texto = normalize_input(texto)
    partes = re.split(r"(?:em\s+(?:face|desfavor)\s+(?:de|da)|m\s+face\s+de)", texto, flags=re.IGNORECASE)
    defendant_part = partes[-1]
    nome_desfavor = defendant_part.split(",")[0].strip()
    nome_desfavor = normalize_nome(nome_desfavor)
    cnpj_match = re.search(cnpj_regex, defendant_part, re.IGNORECASE)
    cnpj = normalize_cnpj(cnpj_match.group(1)) if cnpj_match else ""
    
        # Verifica dados do banco por CNPJ
    dados_corretos = buscar_no_bancos_maps(cnpj)
    if not dados_corretos:
        dados_corretos = buscar_no_json_gerado(cnpj)

    # Extrai endereço do texto
    desfavor_addr_match = re.search(
        r"(?:com\s+)?(?:sede|endereço(?:\s+na)?)\s+(.*?)(?=,\s*(?:inscrita|pelas))",
        defendant_part, re.IGNORECASE | re.DOTALL
    )

        # Se houver dados confiáveis, atualiza o que veio
        # Primeiro extrai o endereço
    if desfavor_addr_match:
        addr_str = desfavor_addr_match.group(1)
        endereco_data = process_address(addr_str)
    else:
        endereco_data = {"rua": "", "numero": "", "bairro": "", "cidade": "", "uf": "SP", "cep": ""}

    # Depois corrige se tiver dados confiáveis
    if dados_corretos:
        if "nome" in dados_corretos:
            nome_desfavor = dados_corretos["nome"]

        endereco_data["rua"] = dados_corretos.get("rua") or dados_corretos.get("logradouro") or endereco_data.get("rua")
        for campo in ["rua", "numero", "bairro", "cidade", "uf", "cep"]:
            valor_atual = endereco_data.get(campo, "")
            valor_novo = dados_corretos.get(campo)

            if valor_novo:
                logar_correcao_de_campo(campo, valor_atual, valor_novo, logs_widget)
                endereco_data[campo] = valor_novo

    endereco_desfavor = {
        "rua": endereco_data.get("rua"),
        "numero": endereco_data.get("numero"),
        "bairro": endereco_data.get("bairro"),
        "cep": endereco_data.get("cep")
    }
    cidade = endereco_data.get("cidade", "")
    uf = endereco_data.get("uf", "")
    value_match = re.search(r'Dá-se à causa, o valor de\s*(?:R\$\s*)+([\d\.,]+)', texto, re.IGNORECASE)
    valorAcao = format_valor(value_match.group(1)) if value_match else ""
    foro = ""
    foro = ""
    foro_match = re.search(
        r'(FORO(?:\s+(?:DE|REGIONAL|CENTRAL))?(?:\s+[IVXLCDM\d]{1,5})?(?:\s*[-–]?\s*)?(?:[A-ZÀ-Úa-zà-ú0-9´`\'’\-]+(?:\s+|$)){1,6})',
        texto,
        re.IGNORECASE
    )

    if foro_match:
        foro_bruto = foro_match.group(1).strip().upper()
        uf_match = re.search(r'^(.*?)(?:\s+)?(SP|RJ|MG|BA|CE|RS|PE|PR|PA|MA|GO|AM|ES|PB|RN|AL|MT|PI|DF|MS|SC|RO|TO|AC|AP)$', foro_bruto)
        if uf_match:
            foro_nome = uf_match.group(1).strip()
        else:
            foro_nome = foro_bruto

        foro_nome_limpo = re.sub(r'^FORO\s+(DE|REGIONAL|CENTRAL)?\s*', '', foro_nome, flags=re.IGNORECASE).strip()
        foro_corrigido = foro_nome_limpo  # já vem limpo no passo anterior
        foro = normalizar_foro(f"Foro de {foro_corrigido}", log_func=lambda msg: log_message(msg, logs_widget))
        
    if dados_corretos and isinstance(dados_corretos, dict) and "nome" in dados_corretos:
        if len(nome_desfavor) < 10 or "BANCO" not in nome_desfavor.upper():
            if logs_widget:
                log_message(f"✔ Nome do banco corrigido: '{nome_desfavor}' → '{dados_corretos['nome']}'", logs_widget)
            nome_desfavor = dados_corretos["nome"]

    desfavor = {
        "nome": nome_desfavor,
        "cidade": endereco_data.get("cidade", ""),
        "uf": endereco_data.get("uf", ""),
        "cnpj": cnpj,
        "endereco": {
            "rua": endereco_data.get("rua"),
            "numero": endereco_data.get("numero"),
            "bairro": endereco_data.get("bairro"),
            "cep": endereco_data.get("cep")
        },
        "valorAcao": valorAcao,
        "foroDeCompetencia": foro
    }

    desfavor = preencher_dados_desfavor(desfavor)
    return desfavor

def extract_data(text, logs_widget=None):
    text = normalize_input(text)
    cliente = extrair_dados_cliente(text)
    desfavor = extrair_dados_desfavor(text, logs_widget)
    
    result = {
        "cliente": cliente,
        "producaoAntecipadaDeProvas": {
            "desfavor": desfavor
        }
    }
    return result
