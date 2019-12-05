import unittest
from tokenizer import Tokenizer, CharSets
from tokenizer.token import TokenType
from exception.tokenizer_exceptions import *


class TestTokenizer(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.tkz = Tokenizer('')

    def setUp(self):
        with open('./test_tokenizer.py') as file:
            self.code = file.read()
            self.tkz = Tokenizer(self.code)

    def tearDown(self):
        pass

    def test_next_char(self):
        read = ''
        while not self.tkz.is_eof():
            read += self.tkz._Tokenizer__next_char()
        self.assertEqual(self.code + '\n', read)

    def test_unread_char(self):
        c = self.tkz._Tokenizer__next_char()
        self.tkz._Tokenizer__unread_char()
        self.assertEqual(c, self.tkz._Tokenizer__next_char())

    def test_float(self):
        tkz = Tokenizer('''
        double fa = .3;
        double fb = .34;
        double fc = 1.3;
        double fd = .3e4;
        double fe = 1.3e4;
        double ff = 3.;
        double fg = 3.e4;
        double fh = 3E+4;
        ''')
        literals = ['.3', '.34', '1.3', '.3e4', '1.3e4', '3.', '3.e4', '3E+4']
        tokens = tkz.all_tokens()
        for idx, token in enumerate(tokens):
            if idx % 5 == 0:
                self.assertEqual(token.tok_type, TokenType.DOUBLE)
            elif idx % 5 == 1:
                self.assertEqual(token.tok_type, TokenType.IDENTIFIER)
            elif idx % 5 == 2:
                self.assertEqual(token.tok_type, TokenType.ASSIGN)
            elif idx % 5 == 3:
                # print(token)
                self.assertEqual(token.tok_type, TokenType.FLOAT_LITERAL)
                self.assertEqual(token.literal, literals[0])
                literals = literals[1:]
            else:
                self.assertEqual(token.tok_type, TokenType.SEMICOLON)

    def test_decimal_integer(self):
        tkz = Tokenizer('''
        int a = 0;
        int b = 134;
        ''')
        literals = ['0', '134']
        tokens = tkz.all_tokens()
        for idx, token in enumerate(tokens):
            if idx % 5 == 0:
                self.assertEqual(token.tok_type, TokenType.INT)
            elif idx % 5 == 1:
                self.assertEqual(token.tok_type, TokenType.IDENTIFIER)
            elif idx % 5 == 2:
                self.assertEqual(token.tok_type, TokenType.ASSIGN)
            elif idx % 5 == 3:
                # print(token)
                self.assertEqual(token.tok_type, TokenType.INTEGER_LITERAL)
                self.assertEqual(token.literal, literals[0])
                literals = literals[1:]
            else:
                self.assertEqual(token.tok_type, TokenType.SEMICOLON)

        tkz = Tokenizer('int a = 03;')
        self.assertRaises(InvalidInputForState, tkz.all_tokens)

    def test_hexdecimal_integer(self):
        tkz = Tokenizer('''
        int a = 0xff;
        int b = 0X4af;
        int c = 0x03f;
        ''')
        literals = ['0xff', '0X4af', '0x03f']

        tokens = tkz.all_tokens()
        for idx, token in enumerate(tokens):
            if idx % 5 == 0:
                self.assertEqual(token.tok_type, TokenType.INT)
            elif idx % 5 == 1:
                self.assertEqual(token.tok_type, TokenType.IDENTIFIER)
            elif idx % 5 == 2:
                self.assertEqual(token.tok_type, TokenType.ASSIGN)
            elif idx % 5 == 3:
                self.assertEqual(token.tok_type, TokenType.INTEGER_LITERAL)
                self.assertEqual(token.literal, literals[0])
                literals = literals[1:]
            else:
                self.assertEqual(token.tok_type, TokenType.SEMICOLON)

        self.assertRaises(InvalidInputForState,
                          Tokenizer('int a = 0xG').all_tokens)
        self.assertRaises(InvalidInputForState,
                          Tokenizer('int a = 0x').all_tokens)

    def test_comment(self):
        tkz = Tokenizer('''
        /*
        跨行可以 ** /
        nishuo 这是中文
        这是国旗 🇨🇳 */

        // 一行也行哦 😄
        int
        ''')
        tokens = tkz.all_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].tok_type, TokenType.INT)

        self.assertRaises(InvalidCharacter, Tokenizer('🙈').all_tokens)

    def test_char_literal(self):
        tkz = Tokenizer('''
        char a = '3';
        char b = 'o';
        char c = '\\\\';
        char d = '\\'';
        char f = '\\"';
        char g = '\\n';
        char h = '\\r';
        char i = '\\t';
        char j = '\\x23';
        ''')
        literals = ['3', 'o', '\\\\', '\\\'',
                    '\\"', '\\n', '\\r', '\\t', '\\x23']

        tokens = tkz.all_tokens()
        for idx, token in enumerate(tokens):
            if idx % 5 == 0:
                self.assertEqual(token.tok_type, TokenType.CHAR)
            elif idx % 5 == 1:
                self.assertEqual(token.tok_type, TokenType.IDENTIFIER)
            elif idx % 5 == 2:
                self.assertEqual(token.tok_type, TokenType.ASSIGN)
            elif idx % 5 == 3:
                # print(token)
                self.assertEqual(token.tok_type, TokenType.CHAR_LITERAL)
                self.assertEqual(token.literal, '\'' + literals[0] + '\'')
                literals = literals[1:]
            else:
                self.assertEqual(token.tok_type, TokenType.SEMICOLON)

        self.assertRaises(InvalidInputForState, Tokenizer(
            "char c = '\\';").all_tokens)
        self.assertRaises(IllegalEscapeSequenceException,
                          Tokenizer("char c = '\r';").all_tokens)
        self.assertRaises(IllegalEscapeSequenceException,
                          Tokenizer("char c = '\n';").all_tokens)
        self.assertRaises(IllegalEscapeSequenceException,
                          Tokenizer("char c = ''';").all_tokens)

    def test_str_literal(self):
        tkz = Tokenizer('''
        print("hello");
        print("thank you\\n");
        ''')
        literals = ["hello", "thank you\\n"]

        tokens = tkz.all_tokens()
        for idx, token in enumerate(tokens):
            if idx % 5 == 0:
                self.assertEqual(token.tok_type, TokenType.PRINT)
            elif idx % 5 == 1:
                self.assertEqual(token.tok_type, TokenType.LEFT_PARENTHESES)
            elif idx % 5 == 2:
                # print(token)
                self.assertEqual(token.tok_type, TokenType.STR_LITERAL)
                self.assertEqual(token.literal, '"' + literals[0] + '"')
                literals = literals[1:]
            elif idx % 5 == 3:
                self.assertEqual(token.tok_type, TokenType.RIGHT_PARENTHESES)
            else:
                self.assertEqual(token.tok_type, TokenType.SEMICOLON)
