from .DFA import DFA
from .NFA import NFA
from .Regex import Regex, parse_regex
from .Lexer import Lexer


class Parser():
    def __init__(self)  -> None:
        self.tokens = []
        self.curr_char = None
        self.pos = -1

    def parse(self, input: str)  -> None:
        # inpartire input caracter cu caracter
        for i in range(len(input)):
            if input[i] != ' ':
                self.tokens.append(input[i])
        self.pos = -1
        # obtinem primul caracter
        self.next_char()
        # parsam expresia
        result = self.parse_expr()
        return result

    def next_char(self):
        self.pos += 1 # trecem la urmatorul caracter
        if self.pos < len(self.tokens):
            self.curr_char = self.tokens[self.pos]
        # daca am terminat de parsat inputul
        else:
            self.curr_char = None

    def parse_expr(self):
        # parsare expresie lambda
        if self.curr_char == '\\':
            return self.parse_lambda()
        #parsare termen stanga
        left = self.process_term()
        # parsare operatii
        while self.curr_char in ['+', '-', '*', '/']:
            #parsare operator
            op = self.curr_char
            # obtinem urmatorul caracter
            self.next_char()
            # parsare termen dreapta
            right = self.process_term()
            # construire expresie cu operatorul si termenii
            if op == '+':
                left = f"Plus ({left}) ({right})"
            elif op == '-':
                left = f"Minus ({left}) ({right})"
            elif op == '*':
                left = f"Mult ({left}) ({right})"
            elif op == '/':
                left = f"Div ({left}) ({right})"
        return left

    def parse_lambda(self):
        # parsare expresie lambda
        self.next_char() # trecem peste caracterele '\'
        # parametrul lambda
        param = f"Var \"{self.curr_char}\""
        self.next_char()  # trecem peste parametrul lambda
        if self.curr_char != '.':
            print("Lipsa '.' dupa parametrul lambda")
        self.next_char()  # trecem peste '.'
        # parsare corp lambda
        body = self.parse_expr()
        # returnam expresia lambda
        return f"Lambda ({param}) -> {body}"

    def process_term(self):
        # parsare termen
        if self.curr_char == '(':
            # consumam caracterul '('
            self.next_char()
            # parsare expresie dintre paranteze
            expr = self.parse_expr()
            # verificam daca exista paranteza inchisa
            if self.curr_char != ')':
                print("Lipsa paranteza inchisa")
            # consumam caracterul ')'
            self.next_char()
            # returnam expresia dintre paranteze
            return f"Parant ({expr})"
            # parsare variabila
        elif self.curr_char.isalpha():
            # obtinem variabila
            var = self.curr_char
            # consumam variabila
            self.next_char()
            # returnam variabila
            return f"Var \"{var}\""
        elif self.curr_char.isdigit():
            # obtinem valoarea
            val = self.curr_char
            # consumam valoarea
            self.next_char()
            # returnam valoarea
            return f"Val {val}"
            # daca intalnim caracterul '\' parsam expresia lambda
        elif self.curr_char == '\\':
            return self.parse_lambda()