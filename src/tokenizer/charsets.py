class CharSets(object):
    blank_chars = [' ', '\t', '\n', '\r']
    digit_chars = list(map(str, range(10)))
    alpha_chars = [chr(ord(base) + i)
                   for i in range(26) for base in ['a', 'A']]
    punc_chars = ['_', '(', ')', '[', ']', '{', '}', '<', '=', '>', '.',
                  ',', ':', ';', '!', '?', '+', '-', '*', '/', '%', '^',
                  '&', '|', '~', '\\', '"', '\'', '`', '$', '#', '@']
    not_base_chars = ['_', '[', ']', '.', ':', '?', '%', '^',
                      '&', '|', '~', '\\', '"', '\'', '`', '$', '#', '@']
