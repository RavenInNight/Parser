# Абстрактное синтаксическое дерево --- структура данных, описывающая абстрактную структуру программы.
# Дерево абстрактного синтаксиса содержит только содержательную информацию о программе --- в нём нет
# разделителей (запятые, точки с запятой, скобки...), вспомогательных нетерминалов для указания приоритета и т.д.
#
# Абстрактное синтаксическое дерево --- это структура данных в программе

class Expr:
    def eval(self, vartable):
        raise NotImplementedError()

    # Порождаем строчку
    def compile(self):
        raise NotImplementedError()

class BinOpExpr(Expr):
    def __init__(self, left, op, right):
        assert op in ('+', '-', '*', '/', '[', '**', '<', '=', '>')

        self.left = left
        self.op = op
        self.right = right

    def eval(self, vartable):
        if self.op == '+':
            return self.left.eval(vartable) + self.right.eval(vartable)
        elif self.op == '-':
            return self.left.eval(vartable) - self.right.eval(vartable)
        elif self.op == '*':
            return self.left.eval(vartable) * self.right.eval(vartable)
        elif self.op == '/':
            return self.left.eval(vartable) / self.right.eval(vartable)
        elif self.op == '[':
            return self.left.eval(vartable)[self.right.eval(vartable)]
        elif self.op == '**':
            return self.left.eval(vartable) ** self.right.eval(vartable)
        elif self.op == '<':
            return self.left.eval(vartable) < self.right.eval(vartable)
        elif self.op == '=':
            return self.left.eval(vartable) == self.right.eval(vartable)
        elif self.op == '>':
            return self.left.eval(vartable) > self.right.eval(vartable)

    def compile(self):
        if self.op == '[':
            return self.left.compile() + '[' + self.right.compile() + ']'
        else:
            return '(' + self.left.compile() + ' ' + self.op + ' ' + self.right.compile() + ')'

class NumberExpr(Expr):
    def __init__(self, value):
        self.value = value

    def eval(self, vartable):
        return self.value

    def compile(self):
        return repr(self.value)

class VariableExpr(Expr):
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos

    def eval(self, vartable):
        if self.name in vartable:
            return vartable[self.name]
        else:
            raise Error(self.pos, 'Неизвестная переменная ' + self.name)

    def compile(self):
        return self.name

class Statement:
    def exec(self, vartable):
        raise NotImplementedError()

    # Печатаем на стандартный ввод
    def compile(self, indent):
        raise NotImplementedError()

def make_indent(indent):
    return ' ' * 4 * indent

class InputStmt(Statement):
    def __init__(self, varnames):
        self.varnames = varnames

    def exec(self, vartable):
        for varname in self.varnames:
            value = input(varname + ' = ')
            try:
                value = float(value)
            except ValueError:
                value = 0
            vartable[varname] = value

    def compile(self, indent):
        # для каждой x из self.varnames
        # x = float(input('x = '))
        for varname in self.varnames:
            print(make_indent(indent) + varname + " = float(input('" + varname + " = '))")
        

class AssignStmt(Statement):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def exec(self, vartable):
        vartable[self.var] = self.expr.eval(vartable)

    def compile(self, indent):
        print(make_indent(indent) + self.var + ' = ' + self.expr.compile())

class PrintStmt(Statement):
    def __init__(self, exprs):
        self.exprs = exprs

    def exec(self, vartable):
        for expr in self.exprs:
            print(expr.eval(vartable), end=' ')
        print()

    def compile(self, indent):
        print(make_indent(indent) + 'print(' + ', '.join(expr.compile() for expr in self.exprs) + ')')

class Program(Statement):
    def __init__(self, stmts):
        self.stmts = stmts

    def exec(self, vartable):
        for stmt in self.stmts:
            stmt.exec(vartable)

    def compile(self, indent):
        if len(self.stmts) > 0:
            for stmt in self.stmts:
                stmt.compile(indent)
        else:
            print(make_indent(indent) + 'pass')

# IfStmt = 'if' CondExpr 'then' Program 'else' Program 'end'.
class IfStmt(Statement):
    def __init__(self, cond, on_true, on_false):
        self.cond = cond
        self.on_true = on_true
        self.on_false = on_false

    def exec(self, vartable):
        if self.cond.eval(vartable):
            self.on_true.exec(vartable)
        else:
            self.on_false.exec(vartable)

    def compile(self, indent):
        print(make_indent(indent) + 'if ' + self.cond.compile() + ':')
        self.on_true.compile(indent + 1)
        print(make_indent(indent) + 'else:')
        self.on_false.compile(indent + 1)

class WhileStmt(Statement):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def exec(self, vartable):
        while self.cond.eval(vartable):
            self.body.exec(vartable)

    def compile(self, indent):
        print(make_indent(indent) + 'while ' + self.cond.compile() + ':')
        self.body.compile(indent + 1)
    
class Token:
    def __init__(self, tok_type, pos, value):
        self.type = tok_type
        self.pos = pos
        self.value = value

class Error(Exception):
    def __init__(self, pos, message):
        self.pos = pos
        self.message = message


class Lexer:
    def __init__(self, program):
        self.program = program
        self.pos = 0
        self.char = ''
        self.__next()

    def __next(self):
        if self.pos < len(self.program):
            self.char = self.program[self.pos]
            self.pos += 1
        else:
            self.char = ''

    def next_token(self):
        while self.char.isspace():
            self.__next()
        
        pos = self.pos
        if self.char in ('+', '-', '/', '(', ')', '[', ']', ',', ';', '=', '<', '=', '>'):
            result = Token(self.char, pos, None)
            self.__next()

        elif self.char == '*':
            self.__next()
            if self.char == '*':
                self.__next()
                result = Token('**', pos, None)
            else:
                result = Token('*', pos, None)
            
        elif self.char.isdigit():
            value = ''
            while self.char.isdigit():
                value += self.char
                self.__next()
            result = Token('NUMBER', pos, int(value))
            
        elif self.char.isalpha():
            value = ''
            while self.char.isalnum():  # буквы или числа
                value += self.char
                self.__next()

            if value in ('print', 'input', 'if', 'then', 'else', 'end', 'while', 'do'):
                result = Token(value, pos, None)
            else:
                result = Token('VARIABLE', pos, value)

        elif self.char == '':
            result = Token('EOF', pos, None)

        else:
            raise Error(pos, 'Неопознанная лексема')

        return result


class Parser:
    def __init__(self, program):
        self.lexer = Lexer(program)
        self.token = None
        self.__next_token()

    def __next_token(self):
        self.token = self.lexer.next_token()

    def expect(self, tok_type):
        if self.token.type == tok_type:
            result = self.token.value
            self.__next_token()
            return result
        else:
            raise Error(self.token.pos,
                        'Ожидался ' + tok_type + ', получен ' + self.token.type)

    def parse(self):
        tree = self.parse_Program()
        self.expect('EOF')
        return tree

    # Program = Statement { ';' Statement }.
    def parse_Program(self):
        statement = self.parse_Statement()
        result = [statement]
        while self.token.type == ";":
            self.expect(";")
            statement = self.parse_Statement()
            result.append(statement)
        return Program(result)
    
    # Statement = Input | Assign | Print | IfStmt | WhileStmt.
    def parse_Statement(self):
        if self.token.type == "input":
            result = self.parse_Input()
        elif self.token.type == "VARIABLE":
            result = self.parse_Assign()
        elif self.token.type == "print":
            result = self.parse_Print()
        elif self.token.type == "if":
            result = self.parse_IfStmt()
        else:
            result = self.parse_WhileStmt()
        return result
    
    # Input = 'input' VARIABLE { ',' VARIABLE }.
    def parse_Input(self):
        self.expect("input")
        name = self.expect('VARIABLE')
        variables = [name]
        while self.token.type == ",":
            self.expect(",")
            name = self.expect('VARIABLE')
            variables.append(name)
        return InputStmt(variables)
        
    # Assign = VARIABLE '=' Expr.
    def parse_Assign(self):
        name = self.expect("VARIABLE")
        self.expect('=')
        expr = self.parse_Expr()
        return AssignStmt(name, expr)
    
    # Print = 'print' Expr {',' Expr}.
    def parse_Print(self):
        self.expect("print")
        expr = self.parse_Expr()
        exprs = [expr]
        while self.token.type == ",":
            self.expect(",")
            expr = self.parse_Expr()
            exprs.append(expr)
        return PrintStmt(exprs)

    # IfStmt = 'if' CondExpr 'then' Program [ 'else' Program ] 'end'.
    def parse_IfStmt(self):
        self.expect('if')
        cond = self.parse_CondExpr()
        self.expect('then')
        on_true = self.parse_Program()
        if self.token.type == 'else':
            self.expect('else')
            on_false = self.parse_Program()
        else:
            on_false = Program([])
        self.expect('end')
        
        return IfStmt(cond, on_true, on_false)

    # WhileStmt = 'while' CondExpr 'do' Program 'end'.
    def parse_WhileStmt(self):
        self.expect('while')
        cond = self.parse_CondExpr()
        self.expect('do')
        body = self.parse_Program()
        self.expect('end')
        return WhileStmt(cond, body)
  
    # CondExpr = Expr ('<' | '=' | '>') Expr.
    def parse_CondExpr(self):
        left = self.parse_Expr()
        if self.token.type == '<':
            op = '<'
            self.expect('<')
        elif self.token.type == '=':
            op = '='
            self.expect('=')
        else:
            op = '>'
            self.expect('>')
        right = self.parse_Expr()
        return BinOpExpr(left, op, right)

    # Expr = ['+' | '-'] Term { ('+' | '-') Term }.
    def parse_Expr(self):
        if self.token.type in ('+', '-'):
            if self.token.type == '+':
                sign = '+'
                self.__next_token()
            else:
                sign = '-'
                self.__next_token()
        else:
            sign = '+'
        
        result = self.parse_Term()
        
        if sign == '-':
            result = BinOpExpr(NumberExpr(0), '-', result)

        while self.token.type in ('+', '-'):
            if self.token.type == '+':
                op = '+'
                self.__next_token()
            else:
                op = '-'
                self.__next_token()

            term = self.parse_Term()
            result = BinOpExpr(result, op, term)

        return result

    # Term = Factor { ('*' | '/') Factor }.
    def parse_Term(self):
        result = self.parse_Factor()

        while self.token.type in ('*', '/'):
            if self.token.type == '*':
                op = '*'
                self.__next_token()
            else:
                op = '/'
                self.__next_token()

            factor = self.parse_Factor()
            result = BinOpExpr(result, op, factor)

        return result

    # Factor = Base ['**' Factor].
    def parse_Factor(self):
        base = self.parse_Base()

        if self.token.type == '**':
            self.__next_token()
            factor = self.parse_Factor()
            result = BinOpExpr(base, '**', factor)
        else:
            result = base

        return result

    # Base = NUMBER | VARIABLE [ '[' Expr ']' ] | '(' Expr ')'.
    def parse_Base(self):
        if self.token.type == 'NUMBER':
            result = NumberExpr(self.token.value)
            self.__next_token()
        elif self.token.type == 'VARIABLE':
            result = VariableExpr(self.token.value, self.token.pos)
            self.__next_token()
            if self.token.type == '[':
                self.expect('[')
                index = self.parse_Expr()
                self.expect(']')
                result = BinOpExpr(result, '[', index)
        else:
            self.expect('(')
            result = self.parse_Expr()
            self.expect(')')

        return result


def run(program, vartable):
    try:
        p = Parser(program)
        pr = p.parse()
        pr.exec(vartable)
    except Error as err:
        print('ОШИБКА', err.pos, err.message)


def compile_(program):
    try:
        p = Parser(program)
        tree = p.parse()
        tree.compile(0)
    except Error as err:
        print('ОШИБКА', err.pos, err.message)
    


# Программа у нас будет последовательностью операторов, среди которых будут оператор ввода
# input, оператор присваивания и оператор печати print.
# Операторы будут разделяться точкой с запятой.
#
# input x, y;
# z = (x + y) / 2;
# print x, y, z, 2+2
#
# В операторе input через запятую перечисляются имена переменных.
# В операторе присваивания слева от равенства записывается имя переменной, справа --- выражение.
# В операторе print через запятую перечисляются выражения.

