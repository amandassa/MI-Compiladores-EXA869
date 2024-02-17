import os
from mef import analisar_lexico
from sintatico_semantico import AnaliseSintatica_Semantica

# executar analise lexica
analisar_lexico()

# gerar coleção de tokens [lista de dicionarios]
directory = f'{os.getcwd()}/files'
def get_token_collection():
    list = []
    for file_path in (os.listdir(directory)):
        if ((not (file_path.endswith('-saida.txt') or file_path.endswith('-saida0.txt'))) or not file_path.endswith(".txt")): 
            continue
        token_collection = []
        with open(f'{directory}/{file_path}','r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                line = line.split(' ')
                if (len(line) < 3 or line[2].startswith('//')): continue
                token = dict(
                    n_line = line[0],
                    token_class = line[1],
                    token_text = line[2]
                )
                token_collection.append(token)
                list.append(token_collection)
    return list

# print(*get_token_collection()[0], sep='\n')

def generate_analysis_output():
    global sintatico;
    sintatico = AnaliseSintatica_Semantica(get_token_collection()[0])
    result = sintatico.start()
    success = ('A análise sintática-semântica foi concluída com sucesso =)')
    newfile = open('project_analysis_output.txt', 'w')
    if result == '': newfile.write(success)
    else: newfile.write(result)
    print(result)

generate_analysis_output()