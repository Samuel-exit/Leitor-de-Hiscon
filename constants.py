# constants.py

estado_civil_map = {
    "AMASIADO": "SOLTEIRO",
    "AMASIADA": "SOLTEIRA",
}

bancos_map = {
    "BANCO PAN S.A": "BANCO PAN S.A",
    "BANCO BRB": "BRB BANCO DE BRASÍLIA S.A.",
    "ITAÚ": "ITAÚ UNIBANCO HOLDING S.A.",
    "BANCO DO BRASIL": "BANCO DO BRASIL S.A."
}

foro_map = {
    "FORO DE CUBATAO": "FORO DE CUBATÃO",
    "FORO DE RIBEIRAO PRETO": "FORO DE RIBEIRÃO PRETO"
}

cnpj_regex = r'(?:inscrita\s+no\s+)?(?:CNPJ(?:\/MF)?)\s*(?:sob\s+o\s+nº|nº|no\s+)?\s*(\d{2}\.\d{3}\.\d{3}\/\d{4}-\s*\d{2})'

cidades_conhecidas = [
    "MARÍLIA", "PALMEIRA D’OESTE", "RIBEIRÃO PRETO", "SÃO PAULO", "CAMPINAS", "PRESIDENTE PRUDENTE",
    "SÃO JOSÉ DOS CAMPOS", "SANTO ANDRÉ", "SANTOS", "MAUÁ", "ARARAQUARA", "FRANCA", "CATANDUVA", "CUBATÃO"
]
