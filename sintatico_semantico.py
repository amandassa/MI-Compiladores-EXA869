'''
    table = [
        {
            "ide": str
            "type": str
            "categoria": str
            "escopo": str
        } 
        {
            "ide": str
            "type": str
            "categoria": str
            "escopo": str
        }
    ]
'''

'''
    current_scope: 'g' -> global
                    'IDE' -> escopo da classe <IDE>
'''

class Simbolos():
    def __init__(self):
        self.current_scope = 'g'
        self.current_method = False
        self.classes = []
        self.tabela = []
        self.last_type = None
    
    def inserir(self, token, type=str, categoria=str, escopo=str, params=list):
        self.tabela.append({"ide":token['token_text'],"type":type, "categoria":categoria, "escopo":escopo, "params":params})

    def inserir_classe(self, ide, linha):
        if ide in self.classes:
            return False
        else:
            self.classes.append(ide)
            return True
    
    def set_current_method(self, ide=str):
        self.current_method = ide
    
    def get_current_method(self):
        return self.current_method

    def set_scope(self, name_scope):
        self.current_scope = name_scope
    
    def get_scope(self):
        return self.current_scope
    
    def set_type(self, type=str):
        self.last_type = type
    
    def get_type(self):
        return self.last_type
    
    def set_categoria(self, IDE=str, nova_categoria=str):
        self.tabela[IDE]['categoria'] = nova_categoria

    # Adiciona parametros ao simbolo na medida em que são lidos
    def set_params(self, IDE=str, param=dict):
        lexema = self.get_lexema(IDE, self.get_scope())
        if lexema != False: lexema['params'].append(param)

    #   verificando duplicidade de identificadores em um escopo
    def eh_unico(self, token, escopo=str):
        if self.get_lexema(token['token_text'], escopo) != False:
            return False
        else: return True

    def buscadicio(self, nome=str, scope=str):
        for it in self.tabela:
            if it['ide'] == nome and it['escopo'] == scope:
                print('há um item igual na lista.')
                return True


    def get_lexema(self, lexema_buscado=str, escopo_buscado=str):
        for simbolo in self.tabela:
            #   retorna o { simbolo } caso exista no escopo
            if simbolo['ide'] == lexema_buscado and simbolo['escopo'] == escopo_buscado: return simbolo
            else: return False

    def buscar(self, lexema, classe, escopo):
        pass

    def remover(self, lexema, escopo):
        pass

class AnaliseSintatica_Semantica():
    def __init__(self, token_collection):
        self.tokens = token_collection
        self.index = 0
        self.errors = []
        self.errors_string = ''

        self.semantic_errors = []
        self.semantic_errors_string = ''
        ## tabelas de simbolos
        self.table = Simbolos()
        # self.constants = []
        # self.global_variables = []

    def start(self):
        self.consts_block()
        self.variables_block()
        self.class_block()
        print(self.table.tabela)
        return self.semantic_errors_string
    
    ###############         Funções auxiliares para análise          ###############

    def next_token(self):
        self.index +=1

    #   refere-se ao token anterior com relação ao ponteiro
    def last_token(self):
        return self.tokens[self.index-1] if self.index > 0 else self.current_token()

    def current_token(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else dict(n_line = '',token_class = '',token_text = '')

    def current_token_line(self):
        return self.current_token()['n_line']

    def current_token_class(self):
        return self.current_token()['token_class']

    def current_token_text(self):
        return self.current_token()['token_text']
    
    def write_error(self, e: SyntaxError):
        message = f'{e.msg}, received: {self.current_token_text()} in line {self.tokens[self.index]["n_line"]}'
        self.errors.append(message)
        self.errors_string = f'{self.errors_string} \n {message}'
        # sincronizar/tratamento de erros

    def error(self, text):
        raise SyntaxError (text)
    
    def find_type_attribution(self, current_token):
        # recebe o token atual e verifica se é int ou float
        if current_token['token_class'] == 'NRO' and (current_token['token_text']).isdigit(): return 'int'
        elif current_token['token_class'] == 'NRO' and (not (current_token['token_text']).isdigit()): return 'real'
        else: return self.table.get_type() #TODO relacionais

    ###############         Produções da gramática          ###############

    # Terminais <TYPE>
    def match_TYPE(self):
        type = ['int','real','boolean','string']
        return bool(self.current_token_text() in type)
    
    # Terminais <ATTRIBUTION>
    def match_ATTRIBUTION(self):
        v = self.current_token_text()
        return isinstance(v, (int, float, complex, str, bool))
    
    #  Terminais ART_DOUBLE (classificacao)
    def match_ART_DOUBLE(self):
        return bool(self.current_token_text() == '++' or self.current_token_text() == '--')

    def match_Bool(self):
        return bool(self.current_token_text() == 'true' or self.current_token_text() == 'false')

    # Bloco <CONSTS_BLOCK>
    def consts_block(self):
        try: 
            if self.current_token_text() == 'const':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.consts()
                else:
                    self.error('Expected "{"')
            else:
                self.error('Expected "const"')
        except SyntaxError as e:
            self.write_error(e)

    #   CONSTS (recursao para gerar varias)
    def consts(self):
        try:
            if self.current_token_text() == "}":
                self.next_token()
            elif self.match_TYPE():
                self.const()
                self.consts()
            else:
                self.error('Expected "}" or <TYPE>')
        except SyntaxError as e:
            self.write_error(e)

    #   <CONST>
    def const(self):
        try: 
            if self.match_TYPE():
                self.table.set_type(self.current_token_text())  #salva o tipo atual
                self.next_token()
                self.const_attribution()
                self.multiple_consts()
                # não precisa de next aqui, o multiple_consts já consumiu
            else:
                self.error('Expected <TYPE>')
        except SyntaxError as e:
            self.write_error(e=e)

    #   <CONST_ATTRIBUTION>
    def const_attribution(self):
        try:
            if self.current_token_class() == 'IDE':
                # SEMANTICO: verificar se está numa declaração multipla
                if self.last_token()['token_text'] == ',':
                    current_type = self.table.get_type()
                    self.table.inserir(token=self.current_token(), type=current_type, categoria='const', escopo='g', params=None)
                else:
                    self.table.inserir(token=self.current_token(), type=self.last_token()['token_text'], categoria='const', escopo='g', params=None)
                self.next_token()
                if self.current_token_text() == '=':
                    self.next_token()
                    if self.match_ATTRIBUTION():
                        # SEMANTICO: verificação de tipos: 
                        # tipo da atribuição neste ponto deve ser igual a current_type
                        if self.find_type_attribution(self.current_token()) == self.table.get_type(): pass
                        else: self.semantic_errors_string += f'Erro de tipo na linha {self.current_token_line()}, atribuicao deve ser {self.table.get_type()}\n'
                        self.next_token()
                    else:
                        self.error('Expected "<NRO> or Bool or <CAC>"')
                else:
                    self.error('Expected "="')
            else:
                self.error('Expected <IDE>')
        except SyntaxError as e:
            self.write_error(e=e)

    #   Bloco <MULTIPLE_CONSTS>
    def multiple_consts(self):
        try:
            if self.current_token_text() == ',':
                self.next_token()
                self.const_attribution()
                self.multiple_consts()
            elif self.current_token_text() == ';':
                self.next_token()
            else:
                self.error('Expected "," or ";" ')
        except SyntaxError as e:
            self.write_error(e)

    # Bloco <VARIABLES_BLOCK>
    def variables_block (self):
        try:
            if self.current_token_text() == 'variables':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.variables()
                else:
                    raise SyntaxError ('Expected "{"')
            else: self.error('Expected "variables"')
        except SyntaxError as e:
            self.write_error(e)
    
    #   <VARIABLES>
    def variables(self):
        try:
            if self.current_token_text() == '}':
                self.next_token()
            elif self.match_TYPE():
                self.variable()
                self.variables()
            else:
                self.error('Expected "}" or <TYPE>')
        except SyntaxError as e:
            self.write_error(e)

    #   Bloco <VARIABLE>
    def variable(self):
        try:
            if self.match_TYPE():
                self.table.set_type(self.current_token_text())
                # print(f'current_type:{self.table.get_type()} current_scope:{self.table.get_scope()} current_line:{self.current_token_line()}')
                self.next_token()
                self.dec_var() #
                self.multiple_variables_line()  #
            else:
                self.error('Expected <TYPE>')
        except SyntaxError as e:
            self.write_error(e=e)
    
    # Bloco <DEC_VAR>   declaracao de variavel
    def dec_var(self):
        try:
            if (self.current_token_class() == "IDE"):   # SEMANTICO: Nome da variável
                if self.table.buscadicio(self.current_token_text(), self.table.get_scope()):
                # if (not self.table.get_lexema(self.current_token_text(), self.table.get_scope())):   #se nao existe no escopo
                    self.semantic_errors_string += f'Duplicidade de simbolos {self.current_token_text()} na linha {self.current_token_line()}.\n'
                    # print(f'ide:{self.current_token_text()}, scope:{self.table.get_scope()}')
                else: 
                    self.table.inserir(self.current_token(), self.table.get_type(),'var',self.table.get_scope())
                self.next_token()
                self.dimensions()
            else:
                self.error('Expected <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    #   Bloco <DIMENSIONS>
    #<DIMENSIONS> ::= '[' <SIZE_DIMENSION> ']' <DIMENSIONS>
                # |
    def dimensions(self):
        try:
            if self.current_token_text() == '[':
                # SEMANTICO: mudar a categoria para array? ainda nao acho necessario
                self.next_token()
                self.size_dimension()
                if self.current_token_text() == "]":
                    self.next_token()
                    self.dimensions()   # r a direita
                else:
                    self.error('Expected "]"')
            else:
                pass
        except SyntaxError as e:
            self.write_error(e)

    #   <SIZE_DIMENSION>
    def size_dimension(self):
        try:
            if self.current_token_class() == 'IDE' or self.current_token_class() == 'NRO':
                # verificar se o ide e o NRO se referem a inteiro:
                if self.find_type_attribution(self.current_token()) == 'int': pass
                else: self.semantic_errors_string += f'Erro de tipo na linha {self.current_token_line()}.\n'
                self.next_token()
            else:
                self.error("Expected <NRO> or <IDE>")
        except SyntaxError as e:
            self.write_error(e=e)

    #   <MULTIPLE_VARIABLES_LINE>
    def multiple_variables_line(self):
        try:
            if self.current_token_text() == ';':
                self.next_token()
            elif self.current_token_text() == ',':
                self.next_token()
                self.dec_var()
                self.multiple_variables_line()
            else:
                self.error('Expected ";" or ","')
        except SyntaxError as e:
            self.write_error(e=e)

    #   Bloco <CLASS_BLOCK>

    ###############         Produções da gramática          ###############

    #bloco de objetos 
    def objects_block(self):
        try:
            if self.current_token_text() == 'objects':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.objects()
                else:
                    self.error('Expected "{"')
        except SyntaxError as e:
            self.write_error(e)    
    

    def objects(self): #duvida nesse 
        try:
            if self.current_token_class() == 'IDE':
                self.object()
                self.objects()
            elif self.current_token_text() == '}':
                self.next_token() 
            else:
                self.error('Expected <IDE> or "}"')
        except SyntaxError as e:
            self.write_error(e)
    
    def object(self):
        try:
            #   SEMANTICO: Nessa altura o seguinte IDE deve referir a uma classe declarada.
            if self.current_token_class() == 'IDE':
                if self.current_token_text() in self.table.classes:
                    self.table.set_type(self.current_token_text())  # se o tipo existe, é o tipo atual.
                else: self.semantic_errors_string += f'Erro semantico na linha {self.current_token_line()}, {self.current_token_text()} não e uma classe declarada.\n'
                self.next_token()
                self.dec_var()
                self.multiple_objects()
            else:
                self.error('Expected <IDE>')
        except SyntaxError as e:
            self.write_error(e)
    
    def multiple_objects(self):
        try:
            if self.current_token_text() == ';':
                self.next_token()
            elif self.current_token_text() == ',':
                self.next_token()
                self.dec_var()
                self.multiple_objects()
            else:
                self.error('Expected ";" or ","')
        except SyntaxError as e:
            self.write_error(e)

# main

    def main_methods(self):
        try:
            if self.current_token_text() == 'methods':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.main_methods_body()
                    if self.current_token_text() == '}':
                        self.next_token()
                    else:
                        self.error('Expected "}"')
                else:
                    self.error('Expected "{"')
            else:
                self.error('Expected "methods"')
        except SyntaxError as e:
            self.write_error(e)
    
    def main_methods_body(self):
        try:
            self.main_type()
            if self.current_token_text() == 'main':
                self.next_token()
                if self.current_token_text() == '(':
                    self.next_token()
                    if self.current_token_text() == ')':
                        self.next_token()
                        if self.current_token_text() == '{':
                            self.next_token()
                            self.method_body()
                            self.methods()  
                        else:
                            self.error('Expected "{"')
                    else:
                        self.error('Expected ")"')
                else:
                    self.error('Expected "("')
            else:
                self.error('Expected "main"')
        except SyntaxError as e:
            self.write_error(e)
    
    #   <METHOD_BODY>
    def method_body(self):
        self.variables_block()
        self.objects_block()
        self.commands_method_body()
        
    def commands_method_body(self):
        try:
            self.commands()
            if self.current_token_text() == 'return':
                self.next_token()
                self.return_block()     # return_block equivalente a <RETURN>
                if self.current_token_text() == ';':
                    self.next_token()
                    if self.current_token_text() == '}':
                        self.next_token()
                    else:
                        self.error('Expected "}')
                else:
                    self.error('Expected ";"')
            else:
                self.error('Expected "return"')
        except SyntaxError as e:
            self.write_error(e=e)
    
    def match_value_firsts(self):
        return bool((self.current_token_text() in ["[" , "!" , "("]) or (self.current_token_class() in [ 'NRO' , 'CAC' , 'IDE']) or self.match_Bool())

    def return_block(self):
        try:
            if self.match_value_firsts():
                self.value()
            else:
                pass
        except:
            pass

    def init_expression(self):
        self.dec_object_attribute_access()
        self.arithmetic_or_logical_expression()
    
    def arithmetic_or_logical_expression(self):
        if self.current_token_class() == 'ART':
            self.simple_or_double_arithmethic_expression()
        # elif self.current_token_text() == '->' or self.current_token_class() == 'LOG' or self.current_token_class() == 'REL':
        else:
            self.optional_object_method_access()
            self.log_rel_optional()
            self.logical_expression_end()


    def value(self): #TODO parei de verificar blocos nessa função
        try:
            if self.current_token_text() == '[':
                self.vector_assign_block()
            elif self.current_token_class() == 'IDE':
                self.init_expression()
            elif self.current_token_text() == '!':
                self.logical_expression_begin()
                self.logical_expression_end()
            elif self.current_token_text() == '(':
                self.arithmethic_or_logical_expression_with_parentheses()
            elif self.current_token_class() == 'NRO':
                self.next_token()
                self.simple_or_double_arithmetic_expression_optional()
            elif self.match_Bool():
                self.next_token()
            elif self.current_token_class() == 'CAC':
                self.next_token()
            else:
                self.error('Expected any of the following: \n\t\t "[" , "!" , "(" , <BOOL> , <NRO> , <CAC> , <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    def vector_assign_block(self):
        try:
            if self.current_token_text() == '[':
                self.next_token()
                self.elements_assign()
                if self.current_token_text() == ']':
                    self.next_token()
                else:
                    self.error('Expected "]"')
            else:
                self.error('Expected "["')  # provavelmente inatingivel (value gera vazio)
        except SyntaxError as e:
            self.write_error(e)

    def elements_assign(self):
        self.element_assign()
        self.multiple_elements_assign()

    def multiple_elements_assign(self):
        if self.current_token_text() == ',':
            self.next_token()
            self.element_assign()
            self.multiple_elements_assign()
        else:
            pass
    
    def element_assign(self):
        try:
            if self.current_token_class() == 'IDE':
                self.next_token()
            elif self.current_token_class() == 'CAC':   #StringLiteral
                self.next_token()
            elif self.current_token_class() == 'NRO':
                self.next_token()
            elif self.current_token_text() == '[':
                self.n_dimensions_assign()
            else:
                self.error('Expected <IDE> , <CAC> , <NRO> or "["')
        except SyntaxError as e:
            self.write_error(e)
    
    def n_dimensions_assign(self):
        try:
            if self.current_token_text() == '[':
                self.next_token()
                self.elements_assign()
                if self.current_token_text() == ']':
                    self.next_token()
                else:
                    self.error('Expected "]"')
            else:
                pass    #prod. vazia
        except SyntaxError as e:
            self.write_error(e)


    def arithmethic_or_logical_expression_with_parentheses(self):
        try:
            if self.current_token_text() == '(':
                self.next_token()
                self.expressions()
                if self.current_token_text() == ')':
                    self.next_token()
                    self.expressions_without_parentheses_end()
                else:
                    self.error('Expected ")"')
            else:
                self.error('Expected "("')
        except SyntaxError as e:
            self.write_error(e)
    
    def expressions(self):
        try:
            if self.current_token_text() == '(':
                self.parentheses_begin()
            elif self.current_token_class() == 'NRO':
                self.simple_expression_without_parentheses()
            elif self.match_Bool():
                self.logical_expression_without_parentheses()
            elif self.current_token_class() == 'IDE':
                self.simple_or_logical_ide_begin()
            else:
                self.error('Expected "(" or <NRO> or "true","false" or <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    def simple_or_logical_ide_begin(self):
        try:
            if self.current_token_class() == 'IDE':
                self.dec_object_attribute_access()
                self.simple_or_logical_ide_end()
            else:
                self.error('Expected <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    def simple_or_logical_ide_end(self):
        try:
            if self.current_token_class() == 'ART':
                self.end_expression()
            elif self.current_token_text() == '->':
                self.optional_object_method_access()
                self.log_rel_optional()
                self.logical_expression_end()
            else:
                self.error('Expected <ART> or "->"')
        except SyntaxError as e:
            self.write_error(e)

    def logical_expression_without_parentheses(self):
        try:
            if self.match_Bool():
                self.next_token()
                self.logical_expression_end()
            elif self.current_token_text() == '!':
                self.next_token()
                self.logical_expression_begin()
                self.logical_expression_end()
            else:
                self.error('Expected "true", "false" or "!"')
        except SyntaxError as e:
            self.write_error(e=e)

    def simple_expression_without_parentheses(self):
        try:
            if self.current_token_class() == 'NRO':
                self.next_token()
                self.end_expression()
            else:
                self.error('Expected <NRO>')
        except SyntaxError as e:
            self.write_error(e)

    def parentheses_begin(self):
        try:
            if self.current_token_text() == '(':
                self.next_token()
                self.expressions()
                self.parentheses_end()
            else:
                self.error('Expected "("')
        except SyntaxError as e:
            self.write_error(e)
    
    def parentheses_end(self):
        try:
            if self.current_token_text() == ')':
                self.next_token()
                self.expressions_without_parentheses_end()
            else:
                self.error('Expected ")"')
        except SyntaxError as e:
            self.write_error(e)

    def expressions_without_parentheses_end(self):
        try:
            if self.current_token_class() == 'ART':
                self.end_expression()
            elif self.current_token_class() == 'LOG':
                self.next_token()
                self.logical_expression_begin()
                self.logical_expression_end()
            else:
                pass
        except:
            pass

    # bloco <SIMPLE_OR_DOUBLE_ARITHIMETIC_EXPRESSION_OPTIONAL>
    def simple_or_double_arithmetic_expression_optional(self):
        if self.match_ART_DOUBLE() or self.current_token_class() == 'ART':
            self.simple_or_double_arithmethic_expression()
        else: pass

    # <SIMPLE_OR_DOUBLE_ARITHIMETIC_EXPRESSION>
    def simple_or_double_arithmethic_expression(self):
        try:
            if self.match_ART_DOUBLE():
                self.next_token()
            elif self.current_token_class() == 'ART':
                self.end_expression()
            else:
                self.error('Expected "++" , "--" or <ART>')
        except SyntaxError as e:
            self.write_error(e)
    
    def end_expression(self):
        try:
            if self.current_token_class() == 'ART':
                self.next_token()
                self.part_loop()
            else:
                self.error("Expected '+' , '-' , '*' or '/'")
        except SyntaxError as e:
            self.write_error(e)

    def end_expression_optional(self):
        try:
            if self.current_token_class() == 'ART':
                self.end_expression()
            else:
                pass
        except:
            pass
    
    def simple_expression(self):
        try:
            if self.current_token_class() == 'NRO':
                self.part()
                self.end_expression()
            elif self.current_token_text() == '(':
                self.parenthesis_expression()
            else:
                self.error('Expected "(" or <NRO>')
        except SyntaxError as e:
            self.write_error(e)

    def parenthesis_expression(self):
        try:
            if self.current_token_text() == '(':
                self.next_token()
                self.simple_expression()
                if self.current_token_text() == ')':
                    self.next_token()
                    self.end_expression_optional()
                else:
                    self.error('Expected ")"')
            else:
                self.error('Expected "("')
        except SyntaxError as e:
            self.write_error(e)

    def part_loop(self):
        try:
            if self.current_token_class() == 'NRO' or self.current_token_class() == 'IDE':
                self.part()
                self.end_expression_optional()
            elif self.current_token_text() == '(':
                self.parenthesis_expression()
            else:
                self.error('Expected <NRO> or "("')
        except SyntaxError as e:
            self.write_error(e)

    def part(self):
        try: 
            if self.current_token_class() == 'NRO':
                self.next_token()
            elif self.current_token_class() == 'IDE':
                self.object_method_or_object_access_or_part()
            else:
                self.error('Expected <NRO> or <IDE>')
        except:
            pass

    # <OBJECT_METHOD_OR_OBJECT_ACCESS> ::= <OBJECT_METHOD_OR_OBJECT_ACCESS_OR_PART> 
    # remoção de ambiguidade
    def object_method_or_object_access_or_part(self):
        self.dec_object_attribute_access()
        self.optional_object_method_access()

    def dec_object_attribute_access(self):
        try:
            if self.current_token_class() == 'IDE':
                #   SEMÂNTICO: O objeto deve estar declarado para ser acessado.
                if not ((self.table.get_lexema(self.current_token_text(), self.table.get_scope())) or (self.table.get_lexema(self.current_token_text(), self.table.get_current_method()))):
                    pass
                elif self.current_token_text() == 'this': 
                    pass
                else:
                    self.semantic_errors_string += f'Erro semântico na linha {self.current_token_line()}, {self.current_token_text()} não foi declarado no escopo.\n'
                self.next_token()
                self.dimensions()
                self.end_object_attribute_access()
            else:
                self.error('Expected <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    def method(self):
        try:
            if self.current_token_text() == 'void' or self.match_TYPE_VARIABLES():
                self.table.set_type(self.current_token_text())
                self.next_token()
                if self.current_token_class() == 'IDE': # SEMÂNTICO: Nome do método
                    self.table.inserir(self.current_token(),self.table.get_type(),'metodo', self.table.get_scope(), params=[])
                    self.table.set_current_method(self.current_token_text())
                    self.next_token()
                    if self.current_token_text() == '(':
                        self.next_token()
                        self.dec_parameters()
                    else: self.error('Expected "("')
                else: self.error('Expected <IDE>')
            else: self.error('Expected "void" or <IDE> or <TYPE>')
        except SyntaxError as e:
            self.write_error(e=e)
    
    def dec_parameters(self):
        try:
            # <END_DEC_PARAMETERS>
            if self.current_token_text() == ')':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.method_body()
                else:
                    self.error('Expected "{"')
            # <VARIABLE_PARAM>
            elif self.match_TYPE():
                self.table.set_type(self.current_token_text())  # tipo do parametro
                self.next_token()
                if self.current_token_class() == 'IDE': # fim de var param
                    # IDE do parametro
                    self.table.inserir(token=self.current_token(),type=self.table.get_type(), categoria='param', escopo=self.table.get_current_method())
                    self.table.set_params(self.current_token_text(),{'escopo':self.table.get_current_method(),'type':self.table.get_type()})
                    self.next_token()
                    self.mult_dec_parameters()
                else:
                    self.error('Expected <IDE>')
            # <OBJECT_PARAM>
            elif self.current_token_class() == 'IDE':
                self.table.set_type(self.current_token_text())  # tipo do parametro
                self.next_token()
                if self.current_token_class() == 'IDE':
                    # IDE do parametro
                    self.table.inserir(token=self.current_token(),type=self.table.get_type(), categoria='param', escopo=self.table.get_current_method())
                    self.table.set_params(self.current_token_text(),{'escopo':self.table.current_method(),'type':self.table.get_type()})
                    self.next_token()
                    self.mult_dec_parameters()
                else: self.error('Expected <IDE>')
            else:
                self.error('Expected " ) { " or <TYPE> or <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    # <MULT_DEC_PARAMETERS>
    def mult_dec_parameters(self):
        try:
            #   <END_DEC_PARAMETERS>
            if self.current_token_text() == ')':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.method_body()
                else:
                    self.error('Expected "{"')
            elif self.current_token_text() == ',':
                self.next_token()
                if self.match_TYPE_VARIABLES():
                    self.table.set_type(self.current_token_text())  # tipo do parametro
                    self.next_token()
                    if self.current_token_class() == 'IDE':
                        # IDE do parametro
                        self.table.inserir(token=self.current_token(),type=self.table.get_type(), categoria='param', escopo=self.table.get_current_method())
                        self.next_token()
                        self.mult_dec_parameters()
                    else:
                        self.error('Expected <IDE>')
                else:
                    self.error('Expected <TYPE> or <IDE>')
            else:
                self.error('Expected ")" or ","')
        except SyntaxError as e:
            self.write_error(e)

    # <TYPE_VARIABLES>
    def match_TYPE_VARIABLES(self):
        return self.current_token_class() == 'IDE' or self.match_TYPE()
    
    # <METHODS>
    def methods (self):
        #   <TYPES> (primeiro de method)
        if self.current_token_text() == 'void' or self.match_TYPE_VARIABLES():
            self.method()
            self.methods()
        else:
            pass

    def methods_block(self):
        try:
            #   SEMANTICO: Nesta altura o escopo é o mesmo da classe.
            if self.current_token_text() == 'methods':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.methods()
                    if self.current_token_text() == '}':
                        self.next_token()
                    else:
                        self.error('Expected "}"')
                else:
                    self.error('Expected "{"')
            else: 
                self.error('Expected "methods"')
        except SyntaxError as e:
            self.write_error(e)

    #   <COMMANDS> (recursao de <COMMAND>)
    def commands(self):
        primeiro_command = ['print', 'read', 'if', 'for']
        try:
            if (self.current_token_text() in primeiro_command) or (self.current_token_class() == 'IDE'):
                self.command()
                self.commands()
            else:
                pass
        except SyntaxError as e:
            pass

    # Bloco <COMMAND>
    def command(self):
        try:
            if self.current_token_text() == 'print':
                self.print_begin()
            elif self.current_token_text() == 'read':
                self.read_begin()
            elif self.current_token_class() == 'IDE':
                self.object_access_or_assignment()
                if self.current_token_text() == ';':
                    self.next_token()
                else:
                    self.error('Expected ";"')
            elif self.current_token_text() == 'if':
                self.IF()
            elif self.current_token_text() == 'for':
                self.for_block()
            else:
                self.error('Expected "print" or "read" or "if" or "for" or <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    def dec_parameters_constructor(self):
        if self.current_token_class() == 'IDE' or self.match_TYPE():
            self.mult_param_constructor()
            self.mult_dec_parameters_constructor()
        else: pass
    
    def mult_dec_parameters_constructor(self):
        if self.current_token_text() == ',':
            self.next_token()
            self.mult_param_constructor()
            self.mult_dec_parameters_constructor()
        else:
            pass    # prod. vazia

    def mult_param_constructor(self):
        try:
            if self.match_TYPE():
                self.variable_param()
            elif self.current_token_class() == 'IDE':
                self.object_param()
            else:
                self.error('Expected <IDE> or <TYPE>')
        except SyntaxError as e:
            self.write_error(e)
    
    def variable_param(self):
        try:
            if self.match_TYPE():
                self.next_token()
                if self.current_token_class() == 'IDE':
                    self.next_token()
                else: 
                    self.error('Expected <IDE>')
            else:
                self.error('Expected <TYPE>')
        except SyntaxError as e:
            self.write_error(e)

    def object_param(self):
        try:
            if self.current_token_class() == 'IDE':
                self.next_token()
                if self.current_token_class() == 'IDE':
                    self.next_token()
                else:
                    self.error('Expected <IDE>')
            else:
                self.error('Expected <IDE>')
        except SyntaxError as e:
            self.write_error(e)

    def mult_parameters(self):
        if self.current_token_text() == ',':
            self.next_token()
            self.value()
            self.mult_parameters()
        else:
            pass    # prod. vazia

    def parameters(self):
        if self.match_value_firsts():
            self.value()
            self.mult_parameters()
        else: pass

    def object_access_or_assignment(self):
        self.dec_object_attribute_access()
        self.object_access_or_assignment_end()
    
    def object_access_or_assignment_end(self):
        try:
            if self.current_token_text() == '=':
                self.next_token()
                self.value()
            elif self.match_ART_DOUBLE():
                self.next_token()
            elif self.current_token_text() == '->':
                self.object_method_access_end()
            else:
                self.error('Expected "=" , "++" , "--" or "->"')
        except SyntaxError as e:
            self.write_error(e)

    def main_type(self):
        try:
            if self.match_TYPE():
                self.next_token()
            elif self.current_token_text() == 'void':
                self.next_token()
            else:
                self.error('Expected "void" or <TYPE>')
        except SyntaxError as e:
            self.write_error(e)
    
    #bloco classe

    def class_block(self):
        try:
            if self.current_token_text() == 'class':
                self.next_token()
                self.ide_class()
            else:
                self.error('Expected "class"')
        except:
            pass
    
    def ide_class(self):
        try:
            if self.current_token_class() == 'IDE':
                #   SEMANTICO: Escopo atual: Classe
                #   Inserção do IDE e verificação de duplicidade da classe
                self.table.set_scope(self.current_token_text())
                self.table.inserir(self.current_token(),type='IDE', categoria='classe', escopo=self.table.get_scope())
                if self.table.inserir_classe(self.current_token_text(),self.current_token_line()): pass
                else: 
                    self.semantic_errors_string += (f'Identificador classe {self.current_token_text()} duplicado na linha {self.current_token_line()} será sobrescrito.\n')
                    lexema = self.table.get_lexema(self.current_token_text(), self.table.get_scope())
                    lexema["ide"]=self.current_token_text()
                    lexema["type"]='IDE'
                    lexema["categoria"]='classe'
                    lexema["escopo"]=self.table.get_scope()
                self.next_token()
                self.extends()
            elif self.current_token_text() == 'main':
                self.main()
            else:
                self.error('Expected <IDE> or "main"')
        except SyntaxError as e:
            self.write_error(e)
    
    def extends(self):
        try:
            if self.current_token_text() == 'extends':
                self.next_token()
                if self.current_token_class() == 'IDE':
                    if self.current_token_text() in self.table.classes: pass
                    else: self.semantic_errors_string += f'Erro semantico na linha {self.current_token_line()}, {self.current_token_text()} não e uma classe declarada.\n'
                    self.next_token()
                    self.start_class_block()
                else:
                    self.error('Expected IDE')
            elif self.current_token_text() == '{':
                self.start_class_block()
            else: self.error('Expected "extends" or "{"')
        except SyntaxError as e:
            self.write_error(e)

    def start_class_block(self):
        try:
            if self.current_token_text() == '{':
                self.next_token()
                self.init_class()
            else:
                self.error('Expected "{"')
        except SyntaxError as e:
            self.write_error(e)
    
    def init_class(self):
        try:
            self.body_blocks()
            self.methods_block()
            self.constructor()
        except SyntaxError as e:
            self.write_error(e)

    def constructor(self):
        try:
            if self.current_token_text() == 'constructor':
                self.next_token()
                if self.current_token_text() == '(':
                    self.next_token()
                    self.dec_parameters_constructor()
                    if self.current_token_text() == ')':
                        self.next_token()
                        if self.current_token_text() == '{':
                            self.next_token()
                            self.variables_block()
                            self.objects_block()
                            self.commands()
                            if self.current_token_text() == '}':
                                self.next_token()
                                self.end_class()
                            else:
                                self.error('Expected "}"')
                        else:
                            self.error('Expected "{"')
                    else:
                        self.error('Expected ")"')
                else:
                    self.error('Expected "("')
            else:
                self.error('Expected "constructor"')
        except SyntaxError as e:
            self.write_error(e)
    
    def end_class(self):
        try:
            if self.current_token_text() == '}':
                self.next_token()
                self.class_block()
            else:
                self.error('Expected "}"')
        except SyntaxError as e:
            self.write_error(e)
    
    def main(self):
        try:
            if self.current_token_text() == 'main':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.init_main()
                else:
                    self.error('Expected "{"')
            else:
                self.error('Expected "main"')
        except SyntaxError as e:
            self.write_error(e)
    

    def init_main(self):
        try:
            self.body_blocks()
            self.main_methods()
            if self.current_token_text() == '}':
                self.next_token()
            else:
                self.error('Expected "}"')
        except SyntaxError as e:
            self.write_error(e)
    
    def body_blocks(self):
        try:
            self.variables_block()
            self.objects_block()
        except SyntaxError as e:
            self.write_error(e)


    # bloco if-else
    def IF(self):
        try:
            if self.current_token_text() == 'if':
                self.next_token()
                if self.current_token_text() ==  '(':
                    self.next_token()
                    self.logical_expression() # <condition> ::= <LOGICAL_EXPRESSION>
                    if self.current_token_text() == ')':
                        self.next_token()
                        if self.current_token_text() == 'then':
                            self.next_token()
                            if self.current_token_text() == '{':
                                self.next_token()
                                self.commands()
                                if self.current_token_text() == '}':
                                    self.next_token()
                                    self.if_else()
                                else:
                                    self.error('Expected "}"')
                            else:
                                self.error('Expected "{"')
                        else:
                            self.error('Expected "then"')
                    else:
                        self.error('Expected ")"')
                else:
                    self.error('Expected "("')
            else:
                self.error('Expected "if"')
        except SyntaxError as e:
            self.write_error(e)
    
    def if_else(self):
        try:
            if self.current_token_text() == 'else':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.commands()
                    if self.current_token_text() == '}':
                        self.next_token()
                    else:
                        self.error('Expected "}"')
            else:
                pass #prod vazia
        except SyntaxError as e:
            self.write_error(e)
    
    #print + read

    def print_begin(self):
        try:
            if self.current_token_text() == 'print':
                self.next_token()
                if self.current_token_text() == '(':
                    self.next_token()
                    self.print_end()
                else:
                    self.error('Expected "("')
            else:
                self.error('Expected "print"')
        except SyntaxError as e:
            self.write_error(e)
    
    def print_end(self):
        try:
            self.print_parameter()
            if self.current_token_text() == ')':
                self.next_token()
                if self.current_token_text() == ';':
                    self.next_token()
                else:
                    self.error('Expected ";"')
            else:
                self.error('Expected ")"')
        except SyntaxError as e:
            self.write_error(e)
    
    def read_begin(self):
        try:
            if self.current_token_text() == 'read':
                self.next_token()
                if self.current_token_text() == '(':
                    self.next_token()
                    self.read_end()
                else:
                    self.error('Expected "("')
            else:
                self.error('Expected "read"')
        except SyntaxError as e:
            self.write_error(e)
    
    def read_end(self):
        try:
            self.dec_object_attribute_access()
            if self.current_token_text() == ')':
                self.next_token()
                if self.current_token_text() == ';':
                    self.next_token()
                else:
                    self.error('Expected ";"')
            else:
                self.error('Expected ")"')
        except SyntaxError as e:
            self.write_error(e)
    

    def print_parameter(self):
        try:
            if self.current_token_class() == 'IDE':
                self.dec_object_attribute_access()
            elif self.current_token_class() == 'CAC' or self.current_token_class() == 'NRO':
                self.next_token()
            else:
                self.error('Expected <DEC_OBJECT_ATTRIBUTE_ACCESS>, <CAC>, or <NRO>')
        except SyntaxError as e:
            self.write_error(e)
    
    #atributos e metodos de objetos 
    def multiple_object_atribute_access(self):
        try:
            self.dec_var()
            self.end_object_attribute_access()
        except SyntaxError as e:
            self.write_error(e)
    
    def end_object_attribute_access(self):
        if self.current_token_text() == '.':
            self.next_token()
            self.multiple_object_atribute_access()
        else:
            pass
            
    def optional_object_method_access(self):
        if self.current_token_text() == '->':
            self.object_method_access_end()
        else:
            pass
    
    def ide_or_constructor(self):
        try:
            if self.current_token_text() == 'constructor' or self.current_token_class() == 'IDE':
                self.next_token()
            else:
                self.error('Expected "constructor" or <IDE>')
        except SyntaxError as e:
            self.write_error(e)
    
    def object_method_access_end(self):
        try:
            if self.current_token_text() == '->':
                self.next_token()
                self.ide_or_constructor()
                if self.current_token_text() == '(':
                    self.next_token()
                    self.parameters()
                    if self.current_token_text() == ')':
                        self.next_token()
                    else:
                        self.error('Expected ")"')
                else:
                    self.error('Expected "("')
            else:
                self.error('Expected "->"')
        except SyntaxError as e:
            self.write_error(e)
    
    #operadores relacionais 
    def relational_expression(self):
        try:
            self.relational_expression_value()
            if self.current_token_class() == 'REL':
                self.next_token()
                self.relational_expression_value()
            else:
                self.error('Expected "<REL>"')
        except SyntaxError as e:
            self.write_error(e)
    
    def relational_expression_value(self):
        try:
            if self.current_token_class() == 'NRO' or self.current_token_class() == 'CAC':
                self.next_token()
            elif self.current_token_class() == 'IDE':
                self.object_method_or_object_access_or_part()
            else:
                self.error('Expected <NRO> , <CAC> or <IDE>')
        except SyntaxError as e:
            self.write_error(e)
    
    #operadores logicos
    def logical_expression(self):
        self.logical_expression_begin()
        self.logical_expression_end()
    
    def logical_expression_begin(self):
        try:
            if self.current_token_text() == '!':
                self.next_token()
                self.logical_expression_begin()
            elif self.current_token_text() == '(':
                self.next_token()
                self.logical_expression()
                if self.current_token_text() == ')':
                    self.next_token()
                else:
                    self.error('Expected ")"')
            elif self.match_Bool() or self.current_token_class() == 'IDE':
                self.logical_expression_value()
            else:
                self.error('Expected "!" , "(" , <BOOL> or <IDE>')
        except SyntaxError as e:
            self.write_error(e)
    
    def logical_expression_end(self):
        if self.current_token_class() == 'LOG':
            self.next_token()
            self.logical_expression_begin()
            self.logical_expression_end()
        else: pass
    
    def log_rel_optional(self):
        if self.current_token_class() == 'REL':
            self.next_token()
            self.relational_expression_value()
        else: pass

    def logical_expression_value(self):
        try:
            if self.match_Bool():
                self.next_token()
            elif self.current_token_class() == 'IDE':
                self.object_method_or_object_access_or_part()
                self.log_rel_optional()
            else:
                self.error('Expected <BOOL> or <IDE>')
        except SyntaxError as e:
            self.write_error(e)
    
    #bloco for
    def for_block(self):
        try:
            self.begin_for()
            self.for_increment()
            self.end_for()
        except SyntaxError as e:
            self.write_error(e)
    
    def assignment(self):
        try:
            if self.current_token_text() == '=':
                self.next_token()
                self.value()
            elif self.current_token_text() in ['--','++']:
                self.next_token()
            else:
                self.error('Expected "=" or "ART_DOUBLE"')
        except SyntaxError as e:
            self.write_error(e)

    def for_increment(self):
        try:
            self.dec_object_attribute_access()
            self.assignment()
        except SyntaxError as e:
            self.write_error(e)
    
    def begin_for(self):
        try:
            if self.current_token_text() == 'for':
                self.next_token()
                if self.current_token_text() == '(':
                    self.next_token()
                    self.object_access_or_assignment()
                    if self.current_token_text() == ';':
                        self.next_token()
                        self.conditional_expression()
                        if self.current_token_text() == ';':
                            self.next_token()
                        else:
                            self.error('Expected ";"')
                    else:
                        self.error('Expected ";"')
                else:
                    self.error('Expected "("')
            else:
                self.error('Expected "for"')
        except SyntaxError as e:
            self.write_error(e)
    
    def end_for(self):
        try:
            if self.current_token_text() == ')':
                self.next_token()
                if self.current_token_text() == '{':
                    self.next_token()
                    self.commands()
                    if self.current_token_text() == '}':
                        self.next_token()
                    else:
                        self.error('Expected "}"')
                else:
                    self.error('Expected "{"')
            else:
                self.error('Expected ")"')
        except SyntaxError as e:
            self.write_error(e)
    
    def conditional_expression(self):
        try:
            if self.current_token_text() == '(':
                self.next_token()
                self.relational_expression()
                if self.current_token_text() == ')':
                    self.next_token()
                else:
                    self.error('Expected ")"')
            else:
                self.relational_expression()
        except SyntaxError as e:
            self.write_error(e)
