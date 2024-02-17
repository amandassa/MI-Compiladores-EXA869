import os
from inspections import *

def start (n_line, line, token):
    global right_comment
    global had_comment 
    line_len = len(line)
    
    double = False
    nao_duplo = False 
    for i_curr in range(line_len):
        #print(f"letra - {line[i_curr]}")
        if double == True:
            double = False
            continue
        else:
            if token['state'] == 0: #estado inicial, pode receber qualquer coisa 
                if isLetter(line[i_curr]):
                    token["ac"]+=line[i_curr]
                    token["state"]=1
                elif isDigit(line[i_curr]):
                    token["ac"]+=line[i_curr]
                    token["state"]=3
                elif isDel(line[i_curr]):
                    token["ac"]+=line[i_curr]
                    write_token(n_line,token["ac"],'DEL',errors_tokens)
                    clear_token(token)
                elif isMfr(line[i_curr]):
                    token["ac"]+=line[i_curr]
                    token["state"] = 11
                elif line[i_curr] == "+":
                    if i_curr < line_len - 1:
                        if line[i_curr+1] == "+":
                            double = True
                            token["ac"] = line[i_curr]+line[i_curr+1]
                            write_token(n_line,token["ac"],'ART',errors_tokens)
                            clear_token(token)
                        else:
                            token["ac"] += line[i_curr]
                            write_token(n_line,token["ac"],'ART',errors_tokens)
                            clear_token(token)
                    else:
                        token["ac"] += line[i_curr]
                        write_token(n_line,token["ac"],'ART',errors_tokens)
                        clear_token(token)  
                elif line[i_curr] == "/":
                    if i_curr < line_len - 1:
                        if line[i_curr+1] == "/":
                            double = True 
                            token["state"] = 9
                        elif line[i_curr+1] == "*":
                            double = True 
                            token["state"] = 10
                        else:
                            #TODO mandar para estado que salva ART /
                            token["ac"] += line[i_curr]
                            write_token(n_line,token["ac"],'ART',errors_tokens)
                            clear_token(token)
                    else:
                        token["ac"] += line[i_curr]
                        write_token(n_line,token["ac"],'ART',errors_tokens)
                        clear_token(token)
                elif line[i_curr] == '*':
                    token["ac"] += line[i_curr]
                    write_token(n_line,token["ac"],'ART',errors_tokens)
                    clear_token(token)
                elif isEsp(line[i_curr]):   #####
                    clear_token(t)
                elif line[i_curr] == "-":
                    if i_curr < line_len - 1:
                        if line[i_curr+1] == "-":
                            double = True
                            token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                            write_token(n_line,token["ac"],'ART',errors_tokens)
                            clear_token(token)
                        elif line[i_curr+1] == ">":
                            double = True
                            token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                            write_token(n_line,token["ac"],'DEL',errors_tokens)
                            clear_token(token)
                        else:
                            token["ac"] += line[i_curr]
                            write_token(n_line,token["ac"],'ART',errors_tokens)
                            clear_token(token)
                    else:
                        token["ac"] += line[i_curr]
                        write_token(n_line,token["ac"],'ART',errors_tokens)
                        clear_token(token)
                elif line[i_curr] == "=" or line[i_curr] == ">" or line[i_curr] == "<" or line[i_curr] == "!":
                    if i_curr < line_len - 1:
                        if isRel(f'{line[i_curr]}{line[i_curr+1]}'):
                            double = True
                            token["ac"] = line[i_curr]+line[i_curr+1]
                            write_token(n_line,token["ac"],'REL',errors_tokens)
                            clear_token(token)
                        else:
                            token["ac"] += line[i_curr]
                            write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                            clear_token(token)
                    else:
                        token["ac"] += line[i_curr]
                        write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                        clear_token(token)
                elif isPossibleLog(line[i_curr]):
                    if i_curr < line_len - 1:
                        token_class = isNextSymbolDouble(line[i_curr], line[i_curr+1])
                        if token_class:
                            token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                            write_token(n_line,token["ac"],token_class,errors_tokens)
                            clear_token(token)
                            double = True
                        else:
                            token["ac"] += line[i_curr]
                            write_token(n_line,token["ac"],'TMF',errors_tokens)
                            clear_token(token)
                    else:
                        token["ac"] += line[i_curr]
                        write_token(n_line,token["ac"],'TMF',errors_tokens)
                        clear_token(token)
                elif line[i_curr] == '"':
                    token["ac"] += line[i_curr]
                    token["state"] = 7 
                elif isErrTMF(line[i_curr]):
                    token["ac"] = line[i_curr]
                    write_token(n_line,token["ac"],'TMF',errors_tokens)
                    clear_token(token)

            elif token["state"]==1: #recebeu uma letra 
                if isLetter(line[i_curr]) or isDigit(line[i_curr]) or line[i_curr] == "_":
                    token["ac"]+=line[i_curr]
                elif (not isInRange(line[i_curr]) and line[i_curr]!='"') or isErrIMF(line[i_curr]):   # IMF
                    token['ac'] += line[i_curr]
                    token['state'] = 6 
                    continue
                elif isEsp(line[i_curr]):
                    write_token(n_line,token["ac"],'IDE',errors_tokens)
                    clear_token(token)
                elif isSepNotEsp(line[i_curr]):
                    write_token(n_line,token["ac"],'IDE',errors_tokens)
                    clear_token(token)
                    #Agora precisa: identificar qual tipo é o separador e 
                    # 1. ou acumular e mandar p/ estado CAC ou CMF (caso ASPAS)
                    # 2. ou identificar possivel simbolo duplo (caso REL LOG ART)
                    # 3. ou ver que é delimitador
                    if (line[i_curr] == '"'):
                        token['ac'] += line[i_curr]
                        token['state'] = 7      # CAC ou CMF
                    elif isPossibleDouble(line[i_curr]):
                        if i_curr < line_len - 1:
                            token_class = isNextSymbolDouble(line[i_curr], line[i_curr+1])
                            if token_class:
                                double = True
                                token['ac'] += f'{line[i_curr]}{line[i_curr+1]}'
                                write_token(n_line,token["ac"],token_class,errors_tokens)
                                clear_token(token)
                            else:
                                token['ac'] += line[i_curr]
                                write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                                clear_token(token)
                                continue
                        else:
                            token['ac'] += line[i_curr]
                            write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                            clear_token(token)
                    elif currentSymbolClass(line[i_curr]): # vai pegar ART REL LOG DEL que nao sao possiveis duplos
                        token['ac'] += line[i_curr]
                        write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                        clear_token(token)
                        nao_duplo = True 
                else: pass
                if double == False:
                    if nao_duplo == False:
                        if i_curr < line_len - 1:  
                            if isSep(line[i_curr+1]):
                                if isPre(token["ac"]):
                                    write_token(n_line,token["ac"],'PRE',errors_tokens)
                                    clear_token(token)
                                else:
                                    write_token(n_line,token["ac"],'IDE',errors_tokens)
                                    clear_token(token)
                                token_class = isNextSymbolDouble(line[i_curr],line[i_curr+1])
                                if token_class:
                                    token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                                    write_token(n_line,token["ac"],token_class,errors_tokens)
                                    clear_token(token)
                                    double = True
                                else:
                                    if (f'{line[i_curr]}{line[i_curr+1]}' == "//"):
                                        # estado de comentario de linha pulando 1 iteracao
                                        double=True
                                        token['ac'] = ''
                                        token["state"] = 9
                                    elif (f'{line[i_curr]}{line[i_curr+1]}' == "/*"):
                                        # estado de comentario de bloco pulando 1 iteracao
                                        token["ac"] = ''
                                        token["state"] = 10
                                    else:
                                        # nao é duplo, porem e aritmetico ou relacional, portanto:
                                        token_class = currentSymbolClass(line[i_curr])
                                        if token_class: 
                                            token['ac'] += line[i_curr]
                                            write_token(n_line,token["ac"],token_class,errors_tokens)
                                            clear_token(token)
                        else: 
                            continue # caso delimitador simples TODO confirmar dps se é mesmo
                    else:
                        nao_duplo = False
            elif token['state'] == 3: #recebeu um numero 
                if isDigit(line[i_curr]):
                    token['ac'] += line[i_curr]
                elif isEsp(line[i_curr]) or line[i_curr]=='':   # Separador espaço
                    write_token(n_line,token["ac"],'NRO',errors_tokens)
                    clear_token(token)
                elif line[i_curr] == ".":
                    token['ac'] += line[i_curr]
                    token['state'] = 4
                elif isSepNotEsp(line[i_curr]) or isPossibleLog(line[i_curr]):   # Separador != espaço
                    if (i_curr < line_len - 1):
                        token_class = isNextSymbolDouble(line[i_curr],line[i_curr+1])
                        if token_class:
                            write_token(n_line,token["ac"],'NRO',errors_tokens)
                            token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                            write_token(n_line,token["ac"],token_class,errors_tokens)
                            clear_token(token)
                            double = True
                        else:
                            write_token(n_line,token["ac"],'NRO',errors_tokens)
                            token["ac"] = line[i_curr]
                            write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)        # atenção para se isso resulta None alguma vez
                            clear_token(token)
                    else: 
                        write_token(n_line,token["ac"],'NRO',errors_tokens)
                        token["ac"] = line[i_curr]
                        write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                        clear_token(token)
                elif line[i_curr] != "." and (not isDigit(line[i_curr])):   # NMF
                    token['ac'] += line[i_curr]
                    token['state'] = 5
            elif token['state'] == 4:       # NRO com 1 ponto
                if isDigit(line[i_curr]):
                    token['ac'] += line[i_curr]
                elif line[i_curr] == "." or isLetter(line[i_curr]) or not isInRange(line[i_curr]) or isMfr(line[i_curr]): # segundo ponto ou letra (NMF)
                    token['ac'] += line[i_curr]
                    token['state'] = 5
                elif isEsp(line[i_curr]):   # Separador espaço
                    if isDigit(line[i_curr-1]):
                        write_token(n_line,token["ac"],'NRO',errors_tokens)
                        clear_token(token)
                    else:
                        write_token(n_line,token["ac"],'NMF',errors_tokens)
                        clear_token(token)
                elif isSepNotEsp(line[i_curr]) or isPossibleLog(line[i_curr]):   # Separador != espaço
                    if isDigit(line[i_curr-1]):
                        if (i_curr < line_len - 1):
                            token_class = isNextSymbolDouble(line[i_curr],line[i_curr+1])
                            if token_class:
                                write_token(n_line,token["ac"],'NRO',errors_tokens)
                                token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                                write_token(n_line,token["ac"],token_class,errors_tokens)
                                clear_token(token)
                                double = True
                            else:
                                write_token(n_line,token["ac"],'NRO',errors_tokens)
                                token["ac"] = line[i_curr]
                                write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)        # atenção para se isso resulta None alguma vez
                                clear_token(token)
                        else: 
                            write_token(n_line,token["ac"],'NRO',errors_tokens)
                            token["ac"] = line[i_curr]
                            write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                            clear_token(token)
                    else:
                        token['ac'] += line[i_curr]
                        token['state'] = 5
                        
            elif token['state'] == 5:       # Estado de "acumulação" do NMF!
                if (line[i_curr] == ".") or (not isSep(line[i_curr])):
                    token['ac'] += line[i_curr]
                elif (line[i_curr] == '"'):
                    write_token(n_line,token["ac"],'NMF',errors_tokens)
                    token["ac"] = line[i_curr]
                    token['state'] = 7     # cac ou cmf
                elif isSepNotEsp(line[i_curr]):
                    if (i_curr < line_len - 1):
                        token_class = isNextSymbolDouble(line[i_curr],line[i_curr+1])
                        if token_class:
                            write_token(n_line,token["ac"],'NMF',errors_tokens)
                            token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                            write_token(n_line,token["ac"],token_class,errors_tokens)
                            clear_token(token)
                            double = True
                        else:
                            write_token(n_line,token["ac"],'NMF',errors_tokens)
                            token["ac"] = line[i_curr]
                            write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)        # atenção para se isso resulta None alguma vez
                            clear_token(token)
                    else: 
                        write_token(n_line,token["ac"],'NMF',errors_tokens)
                        token["ac"] = line[i_curr]
                        write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                        clear_token(token)
                elif isEsp(line[i_curr]):
                    write_token(n_line, token["ac"], 'NMF',errors_tokens)
                    clear_token(token)
            elif token['state'] == 6:
                if not isSep(line[i_curr]):
                    token["ac"] += line[i_curr]
                else:
                    write_token(n_line, token['ac'], "IMF",errors_tokens)   # salva token acumulado
                    clear_token(token)
                    if isSepNotEsp(line[i_curr]):
                        if (i_curr < line_len - 1):
                            token_class = isNextSymbolDouble(line[i_curr],line[i_curr+1])
                            if token_class:
                                write_token(n_line,token["ac"],'IMF',errors_tokens)
                                token["ac"] = f'{line[i_curr]}{line[i_curr+1]}'
                                write_token(n_line,token["ac"],token_class,errors_tokens)
                                clear_token(token)
                                double = True
                            else:
                                if token["ac"]: write_token(n_line,token["ac"],'IMF',errors_tokens)
                                token["ac"] = line[i_curr]
                                write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)        # atenção para se isso resulta None alguma vez
                                clear_token(token)
                        else: 
                            write_token(n_line,token["ac"],'IMF',errors_tokens)
                            token["ac"] = line[i_curr]
                            write_token(n_line,token["ac"],currentSymbolClass(line[i_curr]),errors_tokens)
                            clear_token(token)
                    else:   # isEspaco
                        write_token(n_line, token["ac"], "IMF",errors_tokens)
                        clear_token(token)


            elif token["state"] == 7: #pode ser cadeia de caracteres ou cadeia mal formada  
                if isInRange(line[i_curr]) and (line[i_curr] != '"') and (i_curr<line_len-1):
                    token["ac"] += line[i_curr]
                elif line[i_curr] == '"':
                    token["ac"] += line[i_curr]
                    write_token(n_line, token['ac'], "CAC",errors_tokens)
                    clear_token(token)
                elif not isInRange(line[i_curr]):
                    token['ac'] += line[i_curr]
                    token['state'] = 8
                else: # \n
                    ''' como e q ele pega isso se a linha ja e quebrada na leitura??? '''
                    write_token(n_line, token['ac'], "CMF",errors_tokens)
                    clear_token(token)
            elif token['state'] == 8: # acumular erro de CAC
                if line[i_curr] != '"' and i_curr < line_len-1:
                    token['ac'] += line[i_curr]
                else:
                    if line[i_curr] == '"': token['ac'] += line[i_curr]
                    write_token(n_line, token['ac'], "CMF",errors_tokens)
                    clear_token(token)
            elif token["state"] == 9:
                if i_curr < line_len - 1:
                    continue
                else: 
                    token['state'] = 0
            elif token["state"] == 10: 
                comment_line(n_line, token["ac"])
                had_comment = 2 
                if i_curr < line_len - 1:
                    if line[i_curr] == "*" and line[i_curr+1] == "/":
                        right_comment = 2 # significa que o comentario foi certo 
                        double=True
                        clear_token(token)
                    else:
                        right_comment = 1
                        token['ac'] += line[i_curr] 
            elif token["state"] == 11:
                if not isSep(line[i_curr]):
                    token["ac"] += line[i_curr] 
                else:
                    write_token(n_line, token['ac'], "TMF",errors_tokens)
                    clear_token(token)

                
                

def comment_line(l, buffer):
    # TODO a linha ta pegando sempre a ultima :( 
    global had_comment
    global line_comment
    global ac_comment
    if had_comment == 1: 
        line_comment = l
    else:
        line_comment = l
    ac_comment = buffer 
  

def clear_token(t):
    t['state'] = 0
    t['ac'] = ''

def write_token(line_number, buffer, class_token, errors_t):
    errors = ['CMF', 'CoMF', 'NMF', 'IMF', 'TMF']
    # TODO escrever mensagem de sucesso caso nao haja erros
    if buffer == '':
        pass
    else:
        if ('\n' in buffer): buffer = buffer.replace('\n','')
        if class_token in errors:
            e_t = {
                'linha' : line_number, 
                'classe' : class_token ,
                'ac': buffer
            }
            errors_t.append(e_t)
        else: 
            t = {
                'linha' : line_number, 
                'classe' : class_token ,
                'ac': buffer
            }
            tokens.append(t)

def makeString(lista):
    string = ''
    for t in lista:
        string += f'{t.get("linha")} {t.get("classe")} {t.get("ac")}\n'
    return string

tokens = []
errors_tokens = []
t = {
        'ac': '',
        'state': 0
    }

had_comment = 1 #1 significa que nao teve comentario e 2 significa que teve 
right_comment = 1 

def analisar_lexico():
    global had_comment
    global right_comment
    global tokens
    global errors_tokens
    global t

    # current = f'{os.getcwd()}/testes'
    current = f'{os.getcwd()}/files'
    for file_path in (os.listdir(current)):

        if (file_path.endswith('-saida.txt') or not file_path.endswith(".txt")): 
            continue
        file = open(f'{current}/{file_path}', 'r')
        newfile = open(f'{current}/{os.path.splitext(os.path.basename(file.name))[0]}-saida.txt', 'w')
        for index, line in enumerate(file.readlines(), start=1):
            if (line[-1] == '\u000a'):  # quebra de linha unicode
                line = " ".join([line[:-1], line[-1]])
            else:
                line = " ".join([line, '\n'])
            start(index, (line),t)
        # escrever string em newfile
        if had_comment == 2:
            if right_comment == 2: pass
            else:
                write_token(line_comment,ac_comment,'CoMF',errors_tokens)

        had_comment = 1 #1 significa que nao teve comentario e 2 significa que teve 
        right_comment = 1 

        t = {
            'ac': '',
            'state': 0
        }

        tks = makeString(tokens)
        errs = makeString(errors_tokens)
        if (len(errs) > 0):
            newfile.write(f'{tks}\n{errs}')
        else:
            newfile.write(f'{tks}')
        tokens = []
        errors_tokens = []
        file.close()
        newfile.close()