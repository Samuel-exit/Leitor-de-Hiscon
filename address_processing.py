# address_processing.py
import re
from utils import normalize_endereco_str, format_cep, normalize_city, log_message

def process_address(address_str):
    try:
        address_str = " ".join(address_str.split())
        cep_match = re.search(r'CEP\s*([\d]{5}\s*-\s*[\d]{2,3})', address_str, re.IGNORECASE)
        cep = format_cep(cep_match.group(1)) if cep_match else ""
        address_no_cep = re.sub(r'CEP\s*[\d]{5}\s*-\s*[\d]{2,3}', '', address_str, flags=re.IGNORECASE)
        
        # Extração do bairro
        bairro_match = re.search(r'Bairro\s+([A-ZÀ-Ú\s]+)', address_str, re.IGNORECASE)
        if bairro_match:
            bairro = bairro_match.group(1).strip().upper()
        else:
            bairro_match2 = re.search(r',\s*([^,]+),\s*cidade de', address_str, re.IGNORECASE)
            bairro = bairro_match2.group(1).strip().upper() if bairro_match2 else ""
            if not bairro:
                partes = address_no_cep.split(',')
                if len(partes) > 1:
                    candidato = partes[-1].strip()
                    bairro = candidato.upper() if len(candidato.split()) > 1 else ""
                else:
                    bairro = ""
        
        # Extração de cidade e UF
        cidade_match = re.search(r'cidade de\s+([A-ZÀ-Ú\s]+)[\/-]\s*([A-Z]{2})', address_str, re.IGNORECASE)
        if not cidade_match:
            cidade_match = re.search(r',\s*([A-ZÀ-Ú\s]+)[\/-]\s*([A-Z]{2})', address_str, re.IGNORECASE)
        if cidade_match:
            cidade = normalize_city(cidade_match.group(1))
            uf = cidade_match.group(2).strip().upper()
        else:
            cidade = ""
            uf = "SP"
        
        # Extração da rua e número
        stop_index = None
        m = re.search(r'Bairro\s+', address_str, re.IGNORECASE)
        if m:
            stop_index = m.start()
        else:
            m = re.search(r'cidade de\s+', address_str, re.IGNORECASE)
            if m:
                stop_index = m.start()
        rua_num_str = address_str[:stop_index].strip() if stop_index else address_str.strip()
        rua_num_str = re.sub(r'(?i)^(com\s+)?end[eé]reço\s*(na)?\s+', '', rua_num_str)
        rua_num_match = re.search(r'^(.*?)(\d+)', rua_num_str)
        if rua_num_match:
            rua = normalize_endereco_str(rua_num_match.group(1))
            numero = str(int(rua_num_match.group(2)))
        else:
            rua = normalize_endereco_str(rua_num_str)
            numero = "S/N"
        
        result = {"rua": rua, "numero": numero, "bairro": bairro, "cidade": cidade, "uf": uf, "cep": cep}
        
        # Fallback para extração adicional
        fallback_desfavor = {}
        if (not result.get("cidade") or not result.get("uf") or not result.get("cep")):
            parts = address_str.split(',')
            if parts:
                last_part = parts[-1]
                fallback_match = re.search(r'([A-ZÀ-Ú\s]+)[\/-]\s*([A-Z]{2}).*CEP\s*([\d\-]+)', last_part, re.IGNORECASE)
                if fallback_match:
                    fallback_desfavor["cidade"] = normalize_city(fallback_match.group(1))
                    fallback_desfavor["uf"] = fallback_match.group(2).strip().upper()
                    fallback_desfavor["cep"] = format_cep(fallback_match.group(3))
        for key in ["cidade", "uf", "cep"]:
            if not result.get(key) and fallback_desfavor.get(key):
                result[key] = fallback_desfavor[key]
                
        return result
    except Exception as e:
        log_message(f"Erro ao processar endereço: {e}")
        return {"rua": "", "numero": "S/N", "bairro": "", "cidade": "", "uf": "SP", "cep": ""}
