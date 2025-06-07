#utils.py
import re
import difflib
import json
import os
from constants import cidades_conhecidas
import sys

def get_caminho_arquivo(nome_arquivo):
    if hasattr(sys, '_MEIPASS'):
        # Rodando via PyInstaller
        base_path = sys._MEIPASS
    else:
        # Rodando como script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, nome_arquivo)

def log_message(msg, widget=None):
    if widget:
        try:
            widget.config(state="normal")
            widget.insert("end", msg + "\n")
            widget.config(state="disabled")
            widget.see("end")
        except Exception as e:
            print("Erro ao escrever no log:", e)
    else:
        print(msg)

def normalize_input(text):
    return " ".join(text.split())

def normalize_nome(nome):
    return nome.strip().upper() if nome else ""

def normalize_endereco_str(rua):
    rua = rua.strip()
    if rua.upper().startswith("R "):
        rua = rua[2:]
    rua = rua.replace("AV.", "AVENIDA").replace("R.", "RUA")
    rua = re.sub(r'\s*,\s*', ' ', rua)
    return rua.upper().strip()

def format_cep(cep):
    cep = cep.replace(" ", "")
    if "-" not in cep and len(cep) == 8:
        cep = cep[:5] + "-" + cep[5:]
    if len(cep) < 9:
        cep = cep.ljust(9, "0")
    return cep

def normalize_city(city):
    if city:
        city = city.strip().upper().strip("'")
        if city == "SANTO ANDRE":
            return "SANTO ANDRÉ"
        return city
    return ""

def normalize_cnpj(cnpj):
    if cnpj:
        if not isinstance(cnpj, str):
            cnpj = str(cnpj)
        # Remove todos os caracteres que não sejam dígitos
        digits = re.sub(r'\D', '', cnpj.strip())
        if len(digits) == 14:
            # Formata como XX.XXX.XXX/XXXX-XX
            return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"
        return digits  # Se não tiver 14 dígitos, retorna apenas os dígitos
    return ""

def corrigir_nome_cidade(nome_raw):
    if not nome_raw:
        return ""
    
    nome_raw = nome_raw.strip().upper()
    
    nome_corrigido = (
        nome_raw.replace("0", "O")
                .replace("1", "I")
                .replace("3", "E")
                .replace("5", "S")
                .replace("6", "G")
                .replace("8", "B")
                .replace("4", "A")
    )

    matches = difflib.get_close_matches(nome_corrigido, cidades_conhecidas, n=1, cutoff=0.75)
    
    if matches:
        return matches[0]
    
    # ⚠️ Cidade não reconhecida — pode registrar para análise futura
    log_message(f"Aviso: cidade não reconhecida — '{nome_corrigido}'")
    return nome_corrigido

def carregar_lista_foros(caminho=None):
    if caminho is None:
        caminho = os.path.join(os.path.dirname(__file__), 'foro.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return list(data.values())  # Retorna apenas os nomes dos foros
    except Exception as e:
        print(f"Erro ao carregar foros: {e}")
        return []

def normalizar_foro(foro_extraido, lista_oficial=None, log_func=None):
    if not foro_extraido:
        return ""

    foro_base = foro_extraido.strip().upper()

    if lista_oficial is None:
        lista_oficial = carregar_lista_foros()

    mapa_foro = {item.upper(): item for item in lista_oficial}
    correspondencias = difflib.get_close_matches(foro_base, list(mapa_foro.keys()), n=1, cutoff=0.75)

    if correspondencias:
        resultado = mapa_foro[correspondencias[0]]
        if resultado != foro_extraido and log_func:
            log_func(f"✔ Foro corrigido: '{foro_extraido}' → '{resultado}'")
        return resultado
    else:
        if log_func:
            log_func(f"⚠ Foro não reconhecido: '{foro_extraido}'")
        return foro_extraido

def buscar_cliente_por_cpf(cpf, caminho=None):
    """
    Retorna os dados salvos do cliente com base no CPF.
    """
    if caminho is None:
        caminho = get_caminho_arquivo("json_gerado.json")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados.get("CLIENTES", {}).get(cpf)
    except Exception as e:
        print(f"Erro ao buscar cliente: {e}")
        return None

def buscar_no_bancos_maps(cnpj, caminho=None):
    """
    Busca os dados de um banco com base no CNPJ no arquivo bancos_maps.json.
    """
    if caminho is None:
        caminho = get_caminho_arquivo("bancos_maps.json")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        for nome, info in dados.items():
            if info.get("cnpj") == cnpj:
                # Retorna os dados + nome correto como campo
                info["nome"] = nome  # ← importante: adiciona o nome como referência
                return info

        return None  # se não encontrar
    except Exception as e:
        print(f"Erro ao buscar no bancos_maps: {e}")
        return None


def buscar_no_json_gerado(cnpj, caminho=None):
    """
    Busca os dados do desfavor com base no CNPJ no arquivo json_gerado.json.
    """
    if caminho is None:
        caminho = get_caminho_arquivo("json_gerado.json")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados.get("DESFAVORES", {}).get(cnpj)
    except Exception as e:
        print(f"Erro ao buscar no json_gerado: {e}")
        return None

def logar_correcao_de_campo(campo, original, corrigido, logs_widget=None):
    if logs_widget and original.strip() != corrigido.strip():
        log_message(f"✔ Campo '{campo}' corrigido: '{original}' → '{corrigido}'", logs_widget)
