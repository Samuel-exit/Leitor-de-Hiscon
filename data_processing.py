# data_processing.py
import re

def format_valor(valor_str):
    valor_str = valor_str.replace(" ", "").replace(".", "")
    if "," in valor_str:
        integer_part, decimal_part = valor_str.split(",", 1)
    else:
        integer_part = valor_str
        decimal_part = "00"
    groups = []
    while integer_part:
        groups.insert(0, integer_part[-3:])
        integer_part = integer_part[:-3]
    formatted_integer = ".".join(groups)
    return f"R$ {formatted_integer},{decimal_part}"

def detect_sexo(nacionalidade, estadoCivil, nome):
    nome = nome.strip().upper() if nome else ""
    estadoCivil = estadoCivil.strip().upper() if estadoCivil else ""
    nacionalidade = nacionalidade.strip().upper() if nacionalidade else ""
    
    if nome.startswith("SRA") or nome.startswith("DRA"):
        return "FEMININO"
    if nome.startswith("SR"):
        return "MASCULINO"
    if estadoCivil:
        if any(suf in estadoCivil for suf in ["ADA", "IVA"]):
            return "FEMININO"
        elif any(suf in estadoCivil for suf in ["ADO", "CASADO"]):
            return "MASCULINO"
    if nacionalidade:
        if nacionalidade[-1] == "A":
            return "FEMININO"
        elif nacionalidade[-1] == "O":
            return "MASCULINO"
    if nome and nome[-1] == "A":
        return "FEMININO"
    return "MASCULINO"
