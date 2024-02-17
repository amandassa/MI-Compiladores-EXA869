# Analisador Semântico
O analisador sintático-semântico relaciona os símbolos do código com seu significado.
- Variáveis e constantes globais:
    - Reconhece a duplicidade de identificadores
- Blocos de classe:
    - Reconhece a duplicidade de identificador de classe
    - Herança de classe: Uma classe só pode extender de outra declarada anteriormente a ela.
    - Variáveis de classe (atributos): Reconhece a duplicidade na classe, ou seja, é possível ter variável local de classe e global com o mesmo nome. 
    - Objetos de classe: Só é possível instanciar objetos de classes declaradas anteriormente.

## Como executar:
python3 main_sintatico_semantico.py

#### O analisador sintático-semântico testa todos os arquivos contendo código-fonte de entrada na pasta _files_
#### O resultado da análise sintática do projeto estará no arquivo _project_analysis_output_ na raiz do projeto.


# Analisador léxico

## Como executar:
python3 mef.py

#### O resultado da análise léxica será um arquivo do tipo _arquivo_n-saída.txt_

## Configurações testadas:
- Python 3.10.12
- Ubuntu 22.04
