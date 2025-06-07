import os
import json

def obter_caminho_arquivo(nome_arquivo='json_gerado.json'):
    """Retorna o caminho absoluto para o arquivo de dados finais."""
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(diretorio_atual, nome_arquivo)

def carregar_dados_existentes(caminho=None):
    """Carrega o conteúdo atual do JSON, se existir."""
    if caminho is None:
        caminho = obter_caminho_arquivo()
    if not os.path.exists(caminho):
        return {"CLIENTES": {}, "BANCOS": {}}
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_em_arquivo_geral(dados_extraidos, caminho=None):
    """
    Salva ou atualiza cliente e banco no arquivo json_gerado.json
    baseado no CPF e CNPJ.
    """
    if caminho is None:
        caminho = obter_caminho_arquivo()
    
    dados_atuais = carregar_dados_existentes(caminho)

    cliente = dados_extraidos.get("cliente", {})
    cpf = cliente.get("cpf")
    if cpf:
        dados_atuais["CLIENTES"][cpf] = cliente

    desfavor = dados_extraidos.get("producaoAntecipadaDeProvas", {}).get("desfavor", {})
    cnpj = desfavor.get("cnpj")
    if cnpj:
        dados_atuais["BANCOS"][cnpj] = desfavor

    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados_atuais, f, ensure_ascii=False, indent=2)
