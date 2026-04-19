from __future__ import annotations

from dataclasses import dataclass

from tokenType import Token, TokenKind


@dataclass
class ParseError(Exception):
    message: str
    line: int
    col: int

    def __str__(self) -> str:
        return f"{self.message} at line {self.line}, col {self.col}"


class Parser:
    def __init__(self) -> None:
        self.tokens: list[Token] = []
        self.pos = 0

    def parse(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        program = self.parse_program()
        self.expect(TokenKind.EOF, "Expected end of input")
        return program

    def parse_program(self):
        funcs = []
        while not self.check(TokenKind.EOF):
            if self.match(TokenKind.HASH):
                break
            funcs.append(self.parse_function())
        return {"type": "Program", "functions": funcs}

    def parse_function(self):
        self.expect(TokenKind.KW_FN, "Expected 'fn'")
        name = self.expect(TokenKind.IDENTIFIER, "Expected function name")
        self.expect(TokenKind.LPAREN, "Expected '('")
        params = []
        if not self.check(TokenKind.RPAREN):
            params = self.parse_params()
        self.expect(TokenKind.RPAREN, "Expected ')' after parameter list")

        ret_type = None
        if self.match(TokenKind.ARROW):
            ret_type = self.parse_type()

        body = self.parse_block()
        return {
            "type": "FunctionDecl",
            "name": name.lexeme,
            "params": params,
            "return_type": ret_type,
            "body": body,
        }

    def parse_params(self):
        params = [self.parse_param()]
        while self.match(TokenKind.COMMA):
            params.append(self.parse_param())
        return params

    def parse_param(self):
        is_mut = self.match(TokenKind.KW_MUT)
        ident = self.expect(TokenKind.IDENTIFIER, "Expected parameter name")
        self.expect(TokenKind.COLON, "Expected ':' in parameter")
        ty = self.parse_type()
        return {"type": "Param", "mut": is_mut, "name": ident.lexeme, "ty": ty}

    def parse_type(self):
        if self.match(TokenKind.KW_I32):
            return "i32"
        tk = self.peek()
        raise ParseError("Expected type (currently only i32)", tk.line, tk.col)

    def parse_block(self):
        self.expect(TokenKind.LBRACE, "Expected '{'")
        stmts = []
        while not self.check(TokenKind.RBRACE):
            if self.check(TokenKind.EOF):
                tk = self.peek()
                raise ParseError("Unterminated block, missing '}'", tk.line, tk.col)
            stmts.append(self.parse_statement())
        self.expect(TokenKind.RBRACE, "Expected '}'")
        return {"type": "Block", "statements": stmts}

    def parse_statement(self):
        if self.match(TokenKind.SEMI):
            return {"type": "EmptyStmt"}

        if self.match(TokenKind.KW_RETURN):
            if self.match(TokenKind.SEMI):
                return {"type": "ReturnStmt", "expr": None}
            expr = self.parse_expression()
            self.expect(TokenKind.SEMI, "Expected ';' after return expression")
            return {"type": "ReturnStmt", "expr": expr}

        if self.match(TokenKind.KW_LET):
            decl = self.parse_var_decl()
            self.expect(TokenKind.SEMI, "Expected ';' after let declaration")
            return {"type": "LetStmt", "decl": decl}

        if self.match(TokenKind.KW_IF):
            return self.parse_if_stmt()

        if self.match(TokenKind.KW_WHILE):
            cond = self.parse_expression()
            body = self.parse_block()
            return {"type": "WhileStmt", "cond": cond, "body": body}

        if self.match(TokenKind.KW_LOOP):
            body = self.parse_block()
            return {"type": "LoopStmt", "body": body}

        if self.match(TokenKind.KW_FOR):
            var_name = self.expect(TokenKind.IDENTIFIER, "Expected loop variable after 'for'")
            self.expect(TokenKind.KW_IN, "Expected 'in' after loop variable in for statement")
            start = self.parse_expression()
            self.expect(TokenKind.DOT_DOT, "Expected '..' in for range")
            end = self.parse_expression()
            body = self.parse_block()
            return {
                "type": "ForStmt",
                "var": var_name.lexeme,
                "start": start,
                "end": end,
                "body": body,
            }

        if self.match(TokenKind.KW_BREAK):
            self.expect(TokenKind.SEMI, "Expected ';' after break")
            return {"type": "BreakStmt"}

        if self.match(TokenKind.KW_CONTINUE):
            self.expect(TokenKind.SEMI, "Expected ';' after continue")
            return {"type": "ContinueStmt"}

        # assignment: ID = expr ;
        if self.check(TokenKind.IDENTIFIER) and self.check_next(TokenKind.ASSIGN):
            name = self.advance().lexeme
            self.advance()  # =
            expr = self.parse_expression()
            self.expect(TokenKind.SEMI, "Expected ';' after assignment")
            return {"type": "AssignStmt", "target": name, "expr": expr}

        # expression statement
        expr = self.parse_expression()
        self.expect(TokenKind.SEMI, "Expected ';' after expression")
        return {"type": "ExprStmt", "expr": expr}

    def parse_if_stmt(self):
        cond = self.parse_expression()
        then_block = self.parse_block()
        else_branch = None
        if self.match(TokenKind.KW_ELSE):
            if self.match(TokenKind.KW_IF):
                else_branch = self.parse_if_stmt()
            else:
                else_branch = self.parse_block()
        return {"type": "IfStmt", "cond": cond, "then": then_block, "else": else_branch}

    def parse_var_decl(self):
        is_mut = self.match(TokenKind.KW_MUT)
        if not is_mut:
            tk = self.peek()
            raise ParseError("let declaration must include 'mut'", tk.line, tk.col)
        name = self.expect(TokenKind.IDENTIFIER, "Expected variable name")
        ty = None
        init = None
        if self.match(TokenKind.COLON):
            ty = self.parse_type()
        if self.match(TokenKind.ASSIGN):
            init = self.parse_expression()
        return {"type": "VarDecl", "mut": True, "name": name.lexeme, "ty": ty, "init": init}

    # expression -> comparison -> additive -> multiplicative -> primary
    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        expr = self.parse_additive()
        while self.match_any(
            TokenKind.LT, TokenKind.LE, TokenKind.GT, TokenKind.GE, TokenKind.EQ, TokenKind.NE
        ):
            op = self.previous().kind.value
            right = self.parse_additive()
            expr = {"type": "Binary", "op": op, "left": expr, "right": right}
        return expr

    def parse_additive(self):
        expr = self.parse_multiplicative()
        while self.match_any(TokenKind.PLUS, TokenKind.MINUS):
            op = self.previous().kind.value
            right = self.parse_multiplicative()
            expr = {"type": "Binary", "op": op, "left": expr, "right": right}
        return expr

    def parse_multiplicative(self):
        expr = self.parse_primary()
        while self.match_any(TokenKind.STAR, TokenKind.SLASH):
            op = self.previous().kind.value
            right = self.parse_primary()
            expr = {"type": "Binary", "op": op, "left": expr, "right": right}
        return expr

    def parse_primary(self):
        if self.match(TokenKind.INTEGER):
            return {"type": "IntLiteral", "value": int(self.previous().lexeme)}
        if self.match(TokenKind.IDENTIFIER):
            ident = self.previous()
            if self.match(TokenKind.LPAREN):
                args = []
                if not self.check(TokenKind.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenKind.COMMA):
                        args.append(self.parse_expression())
                self.expect(TokenKind.RPAREN, "Expected ')' after call arguments")
                return {"type": "Call", "callee": ident.lexeme, "args": args}
            return {"type": "Identifier", "name": ident.lexeme}
        if self.match(TokenKind.LPAREN):
            expr = self.parse_expression()
            self.expect(TokenKind.RPAREN, "Expected ')' after expression")
            return {"type": "Grouped", "expr": expr}

        tk = self.peek()
        raise ParseError("Expected expression", tk.line, tk.col)

    # helpers
    def peek(self) -> Token:
        return self.tokens[self.pos]

    def previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def advance(self) -> Token:
        if not self.check(TokenKind.EOF):
            self.pos += 1
        return self.tokens[self.pos - 1]

    def check(self, kind: TokenKind) -> bool:
        return self.peek().kind == kind

    def check_next(self, kind: TokenKind) -> bool:
        if self.pos + 1 >= len(self.tokens):
            return False
        return self.tokens[self.pos + 1].kind == kind

    def match(self, kind: TokenKind) -> bool:
        if self.check(kind):
            self.advance()
            return True
        return False

    def match_any(self, *kinds: TokenKind) -> bool:
        for k in kinds:
            if self.check(k):
                self.advance()
                return True
        return False

    def expect(self, kind: TokenKind, msg: str) -> Token:
        if self.check(kind):
            return self.advance()
        tk = self.peek()
        raise ParseError(msg, tk.line, tk.col)

    # Backward-compatible method used by old GUI code
    def getParse(self, lex_items):
        tokens = []
        for item in lex_items:
            tk_kind = item["prop"]
            tokens.append(Token(tk_kind, item.get("content", ""), item["loc"]["row"], item["loc"]["col"]))
        try:
            return self.parse(tokens)
        except ParseError as e:
            return {"root": str(e), "err": {"row": e.line, "col": e.col}}
