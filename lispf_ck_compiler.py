import ox
import click
import pprint

lexer = ox.make_lexer([
    ('LOOP', r'loop'),
    ('DEC', r'dec'),
    ('INC', r'inc'),
    ('LPAR', r'\('),
    ('RPAR', r'\)'),
    ('RIGHT', r'right'),
    ('LEFT', r'left'),
    ('PRINT', r'print'),
    ('READ', r'read'),
    ('DO', r'do'),
    ('DO_AFTER', r'do-after'),
    ('DO_BEFORE', r'do-before'),
    ('ADD', r'add'),
    ('SUB', r'sub'),
    ('NUMBER', r'[0-9]+'),
    ('ignore_COMMENT', r';[^\n]*'),
    ('ignore_BREAK_LINE', r'\n'),
    ('ignore_SPACE', r'\s+')
])

tokens_list = ['DEC',
          'INC',
          'LOOP',
          'LPAR',
          'RPAR',
          'RIGHT',
          'LEFT',
          'PRINT',
          'READ',
          'DO',
          'DO_AFTER',
          'DO_BEFORE',
          'ADD',
          'SUB',
          'NUMBER']

parser = ox.make_parser([
    ('expr : LPAR RPAR', lambda x,y: '()'),
    ('expr : LPAR term RPAR', lambda x,y,z: y),
    ('term : atom term', lambda x,y: (x,) + y),
    ('term : atom', lambda x : (x,)),
    ('atom : expr', lambda x : x),
    ('atom : DEC', lambda x : x),
    ('atom : INC', lambda x : x),
    ('atom : LOOP', lambda x : x),
    ('atom : RIGHT', lambda x : x),
    ('atom : LEFT', lambda x : x),
    ('atom : PRINT', lambda x : x),
    ('atom : READ', lambda x : x),
    ('atom : DO', lambda x : x),
    ('atom : DO_AFTER', lambda x : x),
    ('atom : DO_BEFORE', lambda x : x),
    ('atom : ADD', lambda x : x),
    ('atom : SUB', lambda x : x),
    ('atom : NUMBER', int),
], tokens_list)

def do_after(command, old_array):
    new_array = []
    i = 0
    while i < len(old_array):
        if old_array[i] == 'add' or old_array[i] == 'sub':
            new_array.append(old_array[i])
            i += 1
        new_array.append(old_array[i])
        new_array.append(command)

        i += 1

    return new_array

def do_before(command, old_array):
    new_array = []
    i = 0
    while i < len(old_array):
        new_array.append(command)
        new_array.append(old_array[i])
        if old_array[i] == 'add' or old_array[i] == 'sub':
            i += 1
            new_array.append(old_array[i])

        i += 1

    return new_array

def lisp_f_ck_compiler(tree, output_list):
    loop_active = False
    i = 0
    j = 0
    while i < len(tree):
        if isinstance(tree[i], tuple):
            output_list = lisp_f_ck_compiler(tree[i], output_list)
        elif tree[i] == 'inc':
            output_list.append('+')
        elif tree[i] == 'dec':
            output_list.append('-')
        elif tree[i] == 'right':
            output_list.append('>')
        elif tree[i] == 'left':
            output_list.append('<')
        elif tree[i] == 'add':
            i += 1
            while j < tree[i]:
                output_list.append('+')
                j += 1

            j = 0
        elif tree[i] == 'sub':
            i += 1
            while j < tree[i]:
                output_list.append('+')
                j += 1

            j = 0
        elif tree[i] == 'print':
            output_list.append('.')
        elif tree[i] == 'read':
            output_list.append(',')
        elif tree[i] == 'do-after':
            i += 1 # pass to command
            command = tree[i]
            i += 1 # pass to tuple
            array = do_after(command, list(tree[i]))
            output_list = lisp_f_ck_compiler(array, output_list)
        elif tree[i] == 'do-before':
            i += 1 # pass to command
            command = tree[i]
            i += 1 # pass to tuple
            array = do_before(command, list(tree[i]))
            output_list = lisp_f_ck_compiler(array, output_list)
        elif tree[i] == 'loop':
            output_list.append('[')
            output_list = lisp_f_ck_compiler(tree[i], output_list)
            output_list.append(']')

        i += 1

    return output_list

def eval(tree):
    file_code = open('saida.bf', 'w')
    output_list = []
    output_list = lisp_f_ck_compiler(tree, output_list)
    file_code.write(''.join(output_list))
    file_code.close()

@click.command()
@click.argument('source', type=click.File('r'))
def make_tree(source):
    source_code = source.read()
    tokens = lexer(source_code)
    print('Tokens List:\n', tokens)
    tree = parser(tokens)
    print("\nSyntax Tree:")
    pprint.pprint(tree)
    eval(tree)

if __name__ == '__main__':
    make_tree()
