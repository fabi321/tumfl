import unittest
from pathlib import Path

from tumfl.lexer import *


class TestNumberLexing(unittest.TestCase):
    def test_simple_int(self):
        lex = Lexer("1")
        nmb: NumberTuple = (False, "1", None, None, None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("123409204023492")
        nmb: NumberTuple = (False, "123409204023492", None, None, None)
        self.assertEqual(lex.get_number(), nmb)

    def test_hex_int(self):
        lex = Lexer("0x123")
        nmb: NumberTuple = (True, "123", None, None, None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0XaBc123")
        nmb: NumberTuple = (True, "abc123", None, None, None)
        self.assertEqual(lex.get_number(), nmb)

    def test_simple_float(self):
        lex = Lexer("0.1")
        nmb: NumberTuple = (False, "0", "1", None, None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("123.456")
        nmb: NumberTuple = (False, "123", "456", None, None)
        self.assertEqual(lex.get_number(), nmb)

    def test_hex_simple_float(self):
        lex = Lexer("0x0.a")
        nmb: NumberTuple = (True, "0", "a", None, None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0X5.Ca")
        nmb: NumberTuple = (True, "5", "ca", None, None)
        self.assertEqual(lex.get_number(), nmb)

    def test_float_dangling_dot(self):
        lex = Lexer(".3")
        nmb: NumberTuple = (False, None, "3", None, None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0.")
        nmb: NumberTuple = (False, "0", None, None, None)
        self.assertEqual(lex.get_number(), nmb)

    def test_hex_float_dangling_dot(self):
        lex = Lexer("0x.3")
        nmb: NumberTuple = (True, None, "3", None, None)
        self.assertEqual(lex.get_number(), nmb)

    def test_float_exponent(self):
        lex = Lexer("0.2e+1")
        nmb: NumberTuple = (False, "0", "2", "+1", None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0.5e")
        nmb: NumberTuple = (False, "0", "5", None, None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("34E1")
        nmb: NumberTuple = (False, "34", None, "1", None)
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0E+1")
        nmb: NumberTuple = (False, "0", None, "+1", None)
        self.assertEqual(lex.get_number(), nmb)

    def test_hex_float_offset(self):
        lex = Lexer("0x2.efp3")
        nmb: NumberTuple = (True, "2", "ef", None, "3")
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0x.4p-2")
        nmb: NumberTuple = (True, None, "4", None, "-2")
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0X1.921FB54442D18P+1")
        nmb: NumberTuple = (True, "1", "921fb54442d18", None, "+1")
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0x.0p-3")
        nmb: NumberTuple = (True, None, "0", None, "-3")
        self.assertEqual(lex.get_number(), nmb)
        lex = Lexer("0xE+1")
        nmb: NumberTuple = (True, "e", None, None, None)
        self.assertEqual(lex.get_number(), nmb)
        lex.advance()
        nmb: NumberTuple = (False, "1", None, None, None)
        self.assertEqual(lex.get_number(), nmb)

    def test_boundaries(self):
        lex = Lexer("0.1a")
        nmb: NumberTuple = (False, "0", "1", None, None)
        self.assertEqual(lex.get_number(), nmb)
        self.assertEqual(lex.current_char, "a")
        lex = Lexer("0xag")
        nmb: NumberTuple = (True, "a", None, None, None)
        self.assertEqual(lex.get_number(), nmb)
        self.assertEqual(lex.current_char, "g")
        lex = Lexer("0.3p2")
        nmb: NumberTuple = (False, "0", "3", None, None)
        self.assertEqual(lex.get_number(), nmb)
        self.assertEqual(lex.current_char, "p")
        lex = Lexer(".3e-5c")
        nmb: NumberTuple = (False, None, "3", "-5", None)
        self.assertEqual(lex.get_number(), nmb)
        self.assertEqual(lex.current_char, "c")
        lex = Lexer("1xb")
        nmb: NumberTuple = (False, "1", None, None, None)
        self.assertEqual(lex.get_number(), nmb)
        self.assertEqual(lex.current_char, "x")


class TestGetLongBrackets(unittest.TestCase):
    def test_single(self):
        lex = Lexer("[[123456''\\\n]]")
        self.assertEqual(lex.get_long_brackets(), "123456''\\\n")
        self.assertEqual(lex.current_char, None)

    def test_multiple(self):
        lex = Lexer("[=[==[===[1245121[[\\\n]]]==]]=]a")
        self.assertEqual(lex.get_long_brackets(), "==[===[1245121[[\\\n]]]==]")
        self.assertEqual(lex.current_char, "a")

    def test_fails(self):
        lex = Lexer("[[dklaospkda\\")
        with self.assertRaises(ValueError):
            lex.get_long_brackets()
        lex = Lexer("[==[[[]]]=]]===]")
        with self.assertRaises(ValueError):
            lex.get_long_brackets()
        lex = Lexer("[")
        with self.assertRaises(AssertionError):
            lex.get_long_brackets()

    def test_no_long_bracket(self):
        lex = Lexer("[=======")
        with self.assertRaises(ValueError):
            lex.get_long_brackets()


class TestSkipComment(unittest.TestCase):
    def test_single_line_comment(self):
        lex = Lexer("--123456''\n1")
        lex.skip_comment()
        self.assertEqual(lex.current_char, "\n")

    def test_long_comment(self):
        lex = Lexer("--[[abc123\ndklask12''\\\n]]a")
        lex.skip_comment()
        self.assertEqual(lex.current_char, "a")


class TestSkipWhitespace(unittest.TestCase):
    def test_skip_whitespace(self):
        lex = Lexer("  \t\n    \n  \ta")
        lex.skip_whitespace()
        self.assertEqual(lex.current_char, "a")


class TestGetName(unittest.TestCase):
    def test_simple(self):
        lex = Lexer("abcdefg")
        self.assertEqual(lex.get_name(), "abcdefg")
        lex = Lexer("ab1234ad_")
        self.assertEqual(lex.get_name(), "ab1234ad_")
        lex = Lexer("A_Z")
        self.assertEqual(lex.get_name(), "A_Z")

    def test_boundaries(self):
        lex = Lexer("abz123-4")
        self.assertEqual(lex.get_name(), "abz123")

    def test_fail_number(self):
        lex = Lexer("4ab")
        with self.assertRaises(AssertionError):
            lex.get_name()


class TestGetString(unittest.TestCase):
    def test_simple(self):
        lex = Lexer('"abc"')
        self.assertEqual(lex.get_string(), "abc")
        lex = Lexer("'abc'")
        self.assertEqual(lex.get_string(), "abc")
        self.assertEqual(lex.current_char, None)

    def test_skip_whitespace(self):
        lex = Lexer("' \z    \n\ta'")
        self.assertEqual(lex.get_string(), " a")
        lex = Lexer("'\za'")
        self.assertEqual(lex.get_string(), "a")

    def test_other_quote(self):
        lex = Lexer("'\"'")
        self.assertEqual(lex.get_string(), '"')
        lex = Lexer('"\'"')
        self.assertEqual(lex.get_string(), "'")

    def test_fail_eof(self):
        lex = Lexer("'abc")
        with self.assertRaises(ValueError):
            lex.get_string()

    def test_fail_line_end(self):
        lex = Lexer("'abc\n'")
        with self.assertRaises(ValueError):
            lex.get_string()

    def test_simple_escape_codes(self):
        lex = Lexer(r"'\a\b\f\n\r\t\v\\\"\''")
        self.assertEqual(lex.get_string(), "\a\b\f\n\r\t\v\\\"'")
        lex = Lexer("'\\\n'")
        self.assertEqual(lex.get_string(), "\n")
        with self.assertRaises(ValueError):
            lex = Lexer("'\\A'")
            lex.get_string()
        with self.assertRaises(ValueError):
            lex = Lexer("'\\e'")
            lex.get_string()

    def test_hexadecimal_escape(self):
        lex = Lexer("'\\x1'")
        with self.assertRaises(ValueError):
            lex.get_string()
        lex = Lexer("'\\x'")
        with self.assertRaises(ValueError):
            lex.get_string()
        lex = Lexer("'\\x0a'")
        self.assertEqual(lex.get_string(), "\n")
        lex = Lexer("'\\x61'")
        self.assertEqual(lex.get_string(), "a")

    def test_decimal_escape(self):
        lex = Lexer("'\\0'")
        self.assertEqual(lex.get_string(), "\0")
        lex = Lexer("'\\256'")
        with self.assertRaises(ValueError):
            lex.get_string()
        lex = Lexer("'\\97\\0971'")
        self.assertEqual(lex.get_string(), "aa1")
        lex = Lexer("'\\97lo\\10\\04923\"'")
        self.assertEqual(lex.get_string(), 'alo\n123"')


class TestNextToken(unittest.TestCase):
    def test_simple(self):
        lex = Lexer("a=2.45e-3;d=a+4<5")
        self.assertEqual(lex.get_next_token(), Token(TokenType.NAME, "a", 1, 1))
        self.assertEqual(lex.get_next_token(), Token(TokenType.ASSIGN, "=", 1, 2))
        nmb: NumberTuple = (False, "2", "45", "-3", None)
        self.assertEqual(lex.get_next_token(), Token(TokenType.NUMBER, nmb, 1, 3))
        self.assertEqual(lex.get_next_token(), Token(TokenType.SEMICOLON, ";", 1, 10))
        self.assertEqual(lex.get_next_token(), Token(TokenType.NAME, "d", 1, 11))
        self.assertEqual(lex.get_next_token(), Token(TokenType.ASSIGN, "=", 1, 12))
        self.assertEqual(lex.get_next_token(), Token(TokenType.NAME, "a", 1, 13))
        self.assertEqual(lex.get_next_token(), Token(TokenType.PLUS, "+", 1, 14))
        nmb: NumberTuple = (False, "4", None, None, None)
        self.assertEqual(lex.get_next_token(), Token(TokenType.NUMBER, nmb, 1, 15))
        self.assertEqual(lex.get_next_token(), Token(TokenType.LESS_THAN, "<", 1, 16))
        nmb: NumberTuple = (False, "5", None, None, None)
        self.assertEqual(lex.get_next_token(), Token(TokenType.NUMBER, nmb, 1, 17))
        self.assertEqual(lex.get_next_token(), Token(TokenType.EOF, "eof", 1, 18))
        self.assertEqual(lex.get_next_token(), Token(TokenType.EOF, "eof", 1, 18))

    def test_comment_string(self):
        lex = Lexer("'abc\\\ndef'--abc\n\"abab'\"--[==[\n\\\n]===]]==]'abc'")
        self.assertEqual(
            lex.get_next_token(), Token(TokenType.STRING, "abc\ndef", 1, 1)
        )
        self.assertEqual(lex.get_next_token(), Token(TokenType.STRING, "abab'", 2, 1))
        self.assertEqual(lex.get_next_token(), Token(TokenType.STRING, "abc", 5, 10))
        self.assertEqual(lex.get_next_token(), Token(TokenType.EOF, "eof", 5, 15))

    def test_tokenizer_error(self):
        lex = Lexer("!")
        with self.assertRaises(ValueError):
            lex.get_next_token()

    def test_lex_tests(self):
        test_dir: Path = Path("lua-tests")
        for file in test_dir.iterdir():
            if file.is_file() and file.suffix == ".lua":
                print(f"Testing {file}", file=sys.stderr)
                with open(file, encoding="iso-8859-15") as f:
                    content: str = f.read()
                lex = Lexer(content)
                while lex.get_next_token().type != TokenType.EOF:
                    ...
