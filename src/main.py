import sys
from tokenizer import Tokenizer, TokenType
from analyser import Analyser
from exception.analyser_exceptions import AnalyserException

if __name__ == '__main__':
    tkz = Tokenizer(open('./tmp/ast/base.c0').read())
    tokens = tkz.all_tokens()

    for tok in tokens:
        print(tok)
    try:
        ast = Analyser(tokens).ast
        ast.draw(draw_full_ast=False)
    except AnalyserException as e:
        print(e)
        print('Source code: ' + tkz.source[e.row], end='')
        print('\033[91mError at     ' + ' ' * e.col + '^\033[0m')
        raise e
