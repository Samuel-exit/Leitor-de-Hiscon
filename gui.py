# gui.py
import tkinter as tk
import tkinter as ttk
from tkinter import messagebox, ttk
import ast
import json
import os
from extraction import extract_data, carregar_banco  # funções para extração de JSON e para carregar a base
from utils import log_message
from utils import get_caminho_arquivo
# Importa as funções para operações com o banco de dados (editar, buscar, cadastrar)
from extraction import buscar_info_banco, editar_banco, cadastrar_banco, carregar_base_bancos
from salvar_em_json_gerado import salvar_em_arquivo_geral

def generate_json(text_input, text_output, copy_button, logs_text, root):
    input_text = text_input.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showerror("Erro", "Por favor, insira o texto ou lista.")
        return

    try:
        data_list = ast.literal_eval(input_text)
        if isinstance(data_list, list):
            texts = []
            for item in data_list:
                if isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                elif isinstance(item, str):
                    texts.append(item)
                else:
                    texts.append(str(item))
            full_text = " ".join(texts)
        else:
            full_text = input_text
    except Exception as e:
        log_message(f"Erro ao converter entrada: {e}", logs_text)
        full_text = input_text

    extracted_data = extract_data(full_text, logs_text)
    salvar_em_arquivo_geral(extracted_data)
    json_str = json.dumps(extracted_data, indent=2, ensure_ascii=False)

    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, json_str)
    text_output.config(state=tk.DISABLED)

    copy_button.config(state=tk.NORMAL)
    copy_button.grid()

    log_message("JSON gerado com sucesso.", logs_text)

#Abre o ultimo Json gerado pelo sistema.
def abrir_json_gerado(text_output, logs_text):
    try:
        caminho_json = get_caminho_arquivo("json_gerado.json")
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)
        conteudo = json.dumps(dados, indent=2, ensure_ascii=False)
        text_output.config(state=tk.NORMAL)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, conteudo)
        text_output.config(state=tk.DISABLED)
        log_message("JSON final carregado com sucesso.", logs_text)
    except Exception as e:
        log_message(f"Erro ao abrir json_gerado.json: {e}", logs_text)

def copy_json(text_output, text_input, copy_button, logs_text, root):
    json_text = text_output.get("1.0", tk.END).strip()
    if json_text:
        root.clipboard_clear()
        root.clipboard_append(json_text)
    text_input.delete("1.0", tk.END)
    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.config(state=tk.DISABLED)
    copy_button.config(state=tk.DISABLED)
    copy_button.grid_remove()
    log_message("JSON copiado e campos limpos.", logs_text)

def main():
    root = tk.Tk()
    root.title("Gerador de JSON")
    
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")
    
    # Aba Principal (Geração de JSON)
    main_frame = tk.Frame(notebook)
    notebook.add(main_frame, text="Principal")
    
    label_input = tk.Label(main_frame, text="Insira o texto ou lista:")
    label_input.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    text_input = tk.Text(main_frame, height=15, width=80)
    text_input.grid(row=1, column=0, padx=10, pady=5)
    
    generate_button = tk.Button(main_frame, text="Gerar JSON", 
                                command=lambda: generate_json(text_input, text_output, copy_button, logs_text, root), 
                                bg="red", fg="white")
    generate_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    
    abrir_button = tk.Button(main_frame, text="Abrir JSON Final",
                         command=lambda: abrir_json_gerado(text_output, logs_text),
                         bg="blue", fg="white")
    abrir_button.grid(row=2, column=0, padx=150, pady=5, sticky="w")

    label_output = tk.Label(main_frame, text="JSON Gerado:")
    label_output.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    
    text_output = tk.Text(main_frame, height=15, width=80, state=tk.DISABLED)
    text_output.grid(row=4, column=0, padx=10, pady=5)
    
    copy_button = tk.Button(main_frame, text="COPIAR", 
                            command=lambda: copy_json(text_output, text_input, copy_button, logs_text, root), 
                            fg="white", bg="green")
    copy_button.grid(row=5, column=0, padx=10, pady=5, sticky="w")
    copy_button.config(state=tk.DISABLED)
    
    # Aba Editar Banco
    frame_editar = tk.Frame(notebook)
    notebook.add(frame_editar, text="Editar Banco")
    
    campos = ["cnpj", "nome", "logradouro", "numero", "complemento", "cep", "bairro", "cidade", "uf", "telefone", "email"]
    vars_editar = {campo: tk.StringVar() for campo in campos}
    
    for i, campo in enumerate(campos):
        tk.Label(frame_editar, text=f"{campo.capitalize()}:").grid(row=i, column=0, padx=10, pady=3, sticky="e")
        tk.Entry(frame_editar, textvariable=vars_editar[campo], width=50).grid(row=i, column=1, padx=10, pady=3)
    
    def buscar_banco():
        cnpj = vars_editar["cnpj"].get().strip()
        # Recarrega a base de dados atualizada do arquivo
        base_atual = carregar_base_bancos()
        banco = buscar_info_banco(cnpj, base_atual)
        if banco:
            for campo in campos:
                vars_editar[campo].set(banco.get(campo, ""))
            log_message(f"Banco encontrado: {banco.get('nome')}", logs_text)
        else:
            messagebox.showerror("Erro", "Banco não encontrado.")
            log_message(f"Banco não encontrado: {cnpj}", logs_text)
    
    def salvar_edicao():
        cnpj = vars_editar["cnpj"].get().strip()
        dados_atualizados = {campo: vars_editar[campo].get() for campo in campos if campo != "cnpj"}
        if editar_banco(cnpj, dados_atualizados):
            log_message(f"Banco editado com sucesso: {cnpj}", logs_text)
            for var in vars_editar.values():
                var.set("")
        else:
            messagebox.showerror("Erro", "Erro ao editar banco.")
            log_message(f"Erro ao editar banco: {cnpj}", logs_text)
    
    tk.Button(frame_editar, text="Buscar", command=buscar_banco, bg="blue", fg="white").grid(row=0, column=2, padx=5)
    tk.Button(frame_editar, text="Salvar", command=salvar_edicao, bg="green", fg="white").grid(row=len(campos), column=1, pady=10)
    
    # Aba Cadastrar Banco
    frame_cadastrar = tk.Frame(notebook)
    notebook.add(frame_cadastrar, text="Cadastrar Banco")
    
    vars_cadastrar = {campo: tk.StringVar() for campo in campos}

    for i, campo in enumerate(campos):
        tk.Label(frame_cadastrar, text=f"{campo.capitalize()}:").grid(row=i, column=0, padx=10, pady=3, sticky="e")
        tk.Entry(frame_cadastrar, textvariable=vars_cadastrar[campo], width=50).grid(row=i, column=1, padx=10, pady=3)
    
    def cadastrar_novo_banco():
        nome = vars_cadastrar["nome"].get().strip()
        dados = {campo: vars_cadastrar[campo].get() for campo in campos if campo != "nome"}
        if cadastrar_banco(nome, dados):
            log_message(f"Banco cadastrado com sucesso: {nome}", logs_text)
            for var in vars_cadastrar.values():
                var.set("")
        else:
            messagebox.showerror("Erro", "Banco já existe.")
            log_message(f"Erro: Banco já existe: {nome}", logs_text)
    
    tk.Button(frame_cadastrar, text="Cadastrar", command=cadastrar_novo_banco, bg="purple", fg="white")\
        .grid(row=len(campos), column=1, pady=10)
    
    # === ABA DE EDIÇÃO DE FOROS ===
    aba2 = ttk.Frame(notebook)
    notebook.add(aba2, text="📘 Editar Foros")

    # Caminho do arquivo JSON de foros
    FORO_PATH = os.path.join(os.path.dirname(__file__), "foro.json")

    # === Funções para manipular o dicionário de foros ===
    def carregar_foros():
        try:
            with open(FORO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def salvar_foros(foros_dict):
        with open(FORO_PATH, "w", encoding="utf-8") as f:
            json.dump(foros_dict, f, ensure_ascii=False, indent=2)

    def atualizar_lista_foros(listbox, foros_dict):
        listbox.delete(0, tk.END)
        for value in foros_dict.values():
            listbox.insert(tk.END, value)

    def adicionar_foro(entry, listbox, foros_dict):
        novo = entry.get().strip()
        if novo and novo not in foros_dict.values():
            novo_id = f"FORO_{len(foros_dict) + 1}"
            foros_dict[novo_id] = novo
            atualizar_lista_foros(listbox, foros_dict)
            entry.delete(0, tk.END)

    def editar_foro(entry, listbox, foros_dict):
        idx = listbox.curselection()
        if idx:
            novo = entry.get().strip()
            if novo:
                chave = list(foros_dict.keys())[idx[0]]
                foros_dict[chave] = novo
                atualizar_lista_foros(listbox, foros_dict)

    def remover_foro(listbox, foros_dict):
        idx = listbox.curselection()
        if idx:
            chave = list(foros_dict.keys())[idx[0]]
            del foros_dict[chave]
            atualizar_lista_foros(listbox, foros_dict)

        # Dados
    foros_dict = carregar_foros()

    # Layout
    frame_principal = ttk.Frame(aba2)
    frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

    # Frame que segura Listbox + Scrollbar
    listbox_frame = ttk.Frame(frame_principal)
    listbox_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(listbox_frame, height=20, font=("Segoe UI", 10), yscrollcommand=scrollbar.set)
    listbox.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=listbox.yview)

    frame_controles = ttk.Frame(frame_principal)
    frame_controles.pack(side="right", fill="y")

    entry_foro = ttk.Entry(frame_controles, font=("Segoe UI", 10))
    entry_foro.pack(fill="x", pady=(0, 10))

    ttk.Button(frame_controles, text="Adicionar", command=lambda: adicionar_foro(entry_foro, listbox, foros_dict)).pack(fill="x", pady=2)
    ttk.Button(frame_controles, text="Editar Selecionado", command=lambda: editar_foro(entry_foro, listbox, foros_dict)).pack(fill="x", pady=2)
    ttk.Button(frame_controles, text="Remover Selecionado", command=lambda: remover_foro(listbox, foros_dict)).pack(fill="x", pady=2)
    ttk.Button(frame_controles, text="Salvar Alterações", command=lambda: salvar_foros(foros_dict)).pack(fill="x", pady=(10, 2))

    atualizar_lista_foros(listbox, foros_dict)
    
    # Aba Logs
    logs_frame = tk.Frame(notebook)
    notebook.add(logs_frame, text="Logs")
    
    logs_text = tk.Text(logs_frame, height=20, width=80, state=tk.DISABLED, bg="black", fg="white")
    logs_text.pack(padx=10, pady=10, fill="both", expand=True)
    
    # Chama carregar_banco somente após a criação do widget logs_text
    carregar_banco(lambda msg: log_message(msg, logs_text))
    
    root.mainloop()

if __name__ == "__main__":
    main()
