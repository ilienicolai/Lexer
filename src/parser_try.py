from typing import Any
from dataclasses import dataclass

class Parser:
    def __init__(self, debug=False):
        self.tokens = []
        self.current_token = None
        self.pos = -1
        self.debug = debug  # Debug flag for optional debugging prints

    def next_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            if self.debug:
                print(f"Current Token: {self.current_token}, Position: {self.pos}")
        else:
            self.current_token = None

    def parse(self, input: str):
        # Tokenize the input string
        for i in range(len(input)):
            if input[i] != ' ':
                self.tokens.append(input[i])

        self.pos = -1
        self.next_token()
        result = self.parse_expression()
        if self.current_token is not None:
            raise ValueError("Unexpected tokens after parsing")
        return result

    def parse_expression(self):
        if self.current_token == '\\':
            return self.parse_lambda()

        left = self.parse_term()

        while self.current_token in ['+', '-', '*', '/']:
            op = self.current_token
            self.next_token()
            right = self.parse_term()

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
        # Parse lambda expressions
        self.next_token()  # Consume '\\'
        if not self.current_token.isalnum():
            raise ValueError(f"Invalid lambda parameter: {self.current_token}")
        param = f"Var \"{self.current_token}\""
        self.next_token()  # Consume the parameter
        if self.current_token != '.':
            raise ValueError("Expected '.' after lambda parameter")
        self.next_token()  # Consume '.'
        body = self.parse_expression()
        return f"Lambda ({param}) -> {body}"

    def parse_term(self):
        if self.current_token == '(':
            self.next_token()
            expr = self.parse_expression()
            if self.current_token != ')':
                raise ValueError("Missing closing parenthesis")
            self.next_token()
            return f"Parant ({expr})"
        elif self.current_token.isalpha():
            var = self.current_token
            self.next_token()
            return f"Var \"{var}\""
        elif self.current_token.isdigit():
            val = self.current_token
            self.next_token()
            return f"Val {val}"
        elif self.current_token == '\\':
            return self.parse_lambda()
        elif self.current_token in ['+', '-', '*', '/']:
            raise ValueError(f"Unexpected operator: {self.current_token} without operands")
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")

# Example usage
input_expression = "\\x.\\y.\\z.\\v.(x + (z * \\x.(x * \\y.(y - \\z.(z * \\v.(v + x))))))"
parser = Parser()
parsed_expression = parser.parse(input_expression)
print(parsed_expression)


