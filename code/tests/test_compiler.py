import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from myLexer import Lexer
from myParser import ParseError, Parser
from tokenType import TokenKind


class LexerTests(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def kinds(self, src: str):
        tks, errs = self.lexer.tokenize(src)
        self.assertFalse(errs)
        return [t.kind for t in tks[:-1]]

    def test_if123_identifier(self):
        ks = self.kinds("if123")
        self.assertEqual(ks, [TokenKind.IDENTIFIER])

    def test_if_equal_number(self):
        ks = self.kinds("if=123")
        self.assertEqual(ks, [TokenKind.KW_IF, TokenKind.ASSIGN, TokenKind.INTEGER])

    def test_multi_char_ops(self):
        ks = self.kinds("== >= <= != -> ..")
        self.assertEqual(
            ks,
            [TokenKind.EQ, TokenKind.GE, TokenKind.LE, TokenKind.NE, TokenKind.ARROW, TokenKind.DOT_DOT],
        )

    def test_comments_and_whitespace(self):
        ks = self.kinds("// one\n  let /*two*/ mut a:i32;")
        self.assertEqual(
            ks,
            [
                TokenKind.KW_LET,
                TokenKind.KW_MUT,
                TokenKind.IDENTIFIER,
                TokenKind.COLON,
                TokenKind.KW_I32,
                TokenKind.SEMI,
            ],
        )

    def test_keywords_vs_identifiers(self):
        ks = self.kinds("if ifa while while_1 else for in loop break continue")
        self.assertEqual(
            ks,
            [
                TokenKind.KW_IF,
                TokenKind.IDENTIFIER,
                TokenKind.KW_WHILE,
                TokenKind.IDENTIFIER,
                TokenKind.KW_ELSE,
                TokenKind.KW_FOR,
                TokenKind.KW_IN,
                TokenKind.KW_LOOP,
                TokenKind.KW_BREAK,
                TokenKind.KW_CONTINUE,
            ],
        )

    def test_mut_and_i32_keywords(self):
        ks = self.kinds("mut value:i32")
        self.assertEqual(
            ks,
            [TokenKind.KW_MUT, TokenKind.IDENTIFIER, TokenKind.COLON, TokenKind.KW_I32],
        )


class ParserTests(unittest.TestCase):
    def parse_ok(self, src: str):
        lexer = Lexer()
        tokens, errs = lexer.tokenize(src)
        self.assertFalse(errs)
        parser = Parser()
        return parser.parse(tokens)

    def parse_fail(self, src: str):
        lexer = Lexer()
        tokens, errs = lexer.tokenize(src)
        self.assertFalse(errs)
        parser = Parser()
        with self.assertRaises(ParseError):
            parser.parse(tokens)

    def test_required_programs(self):
        programs = [
            "fn program_1_1() { }",
            "fn program_1_2() { ;;;;;; }",
            "fn program_1_3() { return ; }",
            "fn program_1_4(mut a:i32) { }",
            "fn program_1_5() -> i32 { return 1; }",
            "fn program_2_0() { let mut a:i32 = 1; }",
            "fn program_2_1() { let mut a; let mut b:i32; }",
            "fn program_2_2(mut a:i32) { a=32; }",
            "fn program_3_1__1() { 0; (1); ((2)); (((3))); }",
            "fn program_3_1__2(mut a:i32) { a; (a); ((a)); (((a))); }",
            "fn program_3_2() { 1<2; 3<=4; 5>6; 7>=8; 9==10; 11!=12; }",
            "fn program_3_3() { 1+2; 3-4; }",
            "fn program_3_4() { 1*2; 3/4; }",
            "fn program_3_5__1() { }",
            "fn program_3_5__2() { program_3_5__1(); }",
            "fn program_4_1(a:i32) -> i32 { if a>0 { return 1; } }",
            "fn program_5_0(a:i32,b:i32) -> i32 { return a+b; }",
            "fn program_5_1(mut n:i32) { while n>0 { n=n-1; } }",
        ]
        for p in programs:
            self.parse_ok(p)

    def test_comparison_operators_parse_success(self):
        self.parse_ok("fn cmp(){ 1<2; 1<=2; 2>1; 2>=1; 1==1; 1!=2; }")

    def test_identifier_as_lvalue_assignment(self):
        ast = self.parse_ok("fn set(mut a:i32){ a=1; }")
        first_stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(first_stmt["type"], "AssignStmt")
        self.assertEqual(first_stmt["target"], "a")

    def test_loop_statement_while(self):
        ast = self.parse_ok("fn loop_min(mut n:i32){ while n>0 { n=n-1; } }")
        first_stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(first_stmt["type"], "WhileStmt")

    def test_if_else_parse(self):
        ast = self.parse_ok("fn s(mut a:i32){ if a>0 { a=a-1; } else { a=a+1; } }")
        stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(stmt["type"], "IfStmt")
        self.assertEqual(stmt["else"]["type"], "Block")

    def test_if_else_if_parse(self):
        ast = self.parse_ok("fn s(mut a:i32){ if a>0 { a=1; } else if a<0 { a=2; } }")
        stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(stmt["type"], "IfStmt")
        self.assertEqual(stmt["else"]["type"], "IfStmt")

    def test_chained_else_if_else_parse(self):
        ast = self.parse_ok(
            "fn s(mut a:i32){ if a>0 { a=1; } else if a<0 { a=2; } else if a==0 { a=3; } else { a=4; } }"
        )
        stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(stmt["type"], "IfStmt")
        self.assertEqual(stmt["else"]["type"], "IfStmt")
        self.assertEqual(stmt["else"]["else"]["type"], "IfStmt")
        self.assertEqual(stmt["else"]["else"]["else"]["type"], "Block")

    def test_loop_break_parse(self):
        ast = self.parse_ok("fn s(){ loop { break; } }")
        stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(stmt["type"], "LoopStmt")
        inner = stmt["body"]["statements"][0]
        self.assertEqual(inner["type"], "BreakStmt")

    def test_while_continue_parse(self):
        ast = self.parse_ok("fn s(mut n:i32){ while n>0 { continue; } }")
        stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(stmt["type"], "WhileStmt")
        inner = stmt["body"]["statements"][0]
        self.assertEqual(inner["type"], "ContinueStmt")

    def test_for_range_parse(self):
        ast = self.parse_ok("fn s(){ for i in 0..10 { } }")
        stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(stmt["type"], "ForStmt")
        self.assertEqual(stmt["var"], "i")

    def test_for_range_with_break_parse(self):
        ast = self.parse_ok("fn s(){ for i in 0..10 { if i>5 { break; } } }")
        stmt = ast["functions"][0]["body"]["statements"][0]
        self.assertEqual(stmt["type"], "ForStmt")
        nested_if = stmt["body"]["statements"][0]
        self.assertEqual(nested_if["type"], "IfStmt")

    def test_precedence(self):
        self.parse_ok("fn p(){ 1+2*3; (1+2)*3; a+b<c; foo(1,2+3); }")

    def test_invalid_cases(self):
        self.parse_fail("fn a( { }")  # missing right parenthesis
        self.parse_fail("fn a(){ return 1 }")  # missing semicolon

        # illegal token
        tks, errs = Lexer().tokenize("fn a(){ @; }")
        self.assertTrue(errs)

        self.parse_fail("fn a(){ 1+; }")  # incomplete expression
        self.parse_fail("fn a(){ if 1 return 1; }")  # if without block
        self.parse_fail("fn a(){ while 1 return 1; }")  # while without block
        self.parse_fail("fn a(){ return +; }")  # syntax error after return
        self.parse_fail("fn a(){ else { return; } }")  # else without if
        self.parse_fail("fn a(){ for i 0..10 { } }")  # for missing in
        self.parse_fail("fn a(){ for i in 0 10 { } }")  # for missing ..
        self.parse_fail("fn a(){ loop ; }")  # loop without block
        self.parse_fail("fn a(){ break }")  # break without semicolon
        self.parse_fail("fn a(){ continue }")  # continue without semicolon


if __name__ == "__main__":
    unittest.main()
