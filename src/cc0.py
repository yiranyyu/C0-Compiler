#! /usr/bin/python3
import sys
from typing import List, Dict
from tokenizer import Tokenizer
from analyser import Analyser
from exception.parser_exceptions import ParserException
from exception.analyser_exceptions import AnalyserException
from exception.symbol_table_exceptions import SymbolTableException
from exception.tokenizer_exceptions import TokenizerException


def print_error_msg_and_exit(msg):
    print(msg, file=sys.stderr)
    exit(1)


if __name__ == '__main__':
    help_info = '''Usage:
      cc0 [options] input [-o file]
    or
      cc0 [-h]
    Options:
      -s        将输入的 c0 源代码翻译为文本汇编文件
      -c        将输入的 c0 源代码翻译为二进制目标文件
      -h        显示关于编译器使用的帮助
      -o file   输出到指定的文件 file, 默认输出到 out 文件
      -a        输出抽象语法树到标准输出
      -A        输出详细的抽象语法树到标准输出
    '''

    args: List[str] = sys.argv[1:]
    options: Dict[str, int] = {}
    for idx, arg in enumerate(args):
        if arg.startswith('-'):
            if arg not in ['-s', '-c', '-h', '-o', '-a', '-A']:
                print_error_msg_and_exit(f'Invalid option {arg}')
            options[arg] = idx

    if '-h' in args:
        print(help_info)
        exit(0)
    if '-s' in args and '-c' in args:
        print_error_msg_and_exit(
            'Please specify `-s` or `-c`, not both\n' + help_info)
    if '-s' not in args and '-c' not in args:
        print_error_msg_and_exit(
            'Please specify output type, `-s` or `-c`\n' + help_info)

    mode = 'w' if '-s' in args else 'wb'

    out_file = sys.stdout
    if '-o' in args:
        out_file_path_index = options['-o'] + 1
        if out_file_path_index == len(args):
            print_error_msg_and_exit('Missing value of -o option')

        out_file_path = args[out_file_path_index]
        try:
            out_file = open(out_file_path, mode)
        except IOError:
            print_error_msg_and_exit(
                f'Cannot open output file {out_file_path}')

    if out_file is sys.stdout:
        out_file = open('./out', mode)

    # for typing convenience, not necessarily `sys.stdin`
    in_file = sys.stdin
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('-'):
            if arg == '-o':
                i += 1
            i += 1
            continue
        try:
            in_file = open(arg)
            break
        except IOError:
            print_error_msg_and_exit(f'Cannot open input file {in_file}')
    if in_file is sys.stdin:
        print_error_msg_and_exit(f'No input file')

    tokenizer = Tokenizer(in_file.read())
    try:
        tokens = tokenizer.all_tokens()
        analyser = Analyser(tokens)
        # analyser.c0_ast.draw()
        elf = analyser.generate()
        if '-s' in args:
            out_file.write(elf.generate_s0())
        elif '-c' in args:
            out_file.write(elf.generate_o0())

        if '-A' in args:
            analyser.c0_ast.draw(draw_full_ast=True)
        elif '-a' in args:
            analyser.c0_ast.draw(draw_full_ast=False)
    except (TokenizerException, ParserException, AnalyserException) as e:
        print(e)
        print('Source code: ' + tokenizer.source[e.row], end='')
        print('\033[91mError at     ' + ' ' * e.col + '^\033[0m')
        raise e
    except SymbolTableException as e:
        print(e)
