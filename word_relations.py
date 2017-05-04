# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from ckip import CKIPParser

def construct_parsing_tree(tree_text):
    parent_node = None
    current_node = {}

    node_queue = []
    text = ''
    is_head = False
    node_id = 0

    for char in tree_text:
        if char == '(':
            node_queue.append(parent_node)

            current_node['child'] = []
            current_node['pos'] = text
            text = ''

            parent_node = current_node
            current_node = {}

        elif char == ')' or char == '|':
            # end of the representation of a node
            if is_head:
                if 'head' in parent_node and parent_node['head']['role']=='head':
                    # 'head' is more important than 'Head'
                    pass
                else:
                    parent_node['head'] = current_node
                is_head = False

            if len(text) > 0:
                current_node['term'] = text
                text = ''
            current_node['id'] = node_id
            node_id += 1
            parent_node['child'].append(current_node)

            if char==')':
                current_node = parent_node
                parent_node = node_queue.pop()
            else:
                current_node = {}


        elif char == ':':
            if text == 'Head' or text == 'head':
                is_head = True
            if 'role' in current_node:
                current_node['pos'] = text
            else:
                current_node['role'] = text

            text = ''

        else:
            text += char

    return current_node

def getRelations(tree):
    if 'child' in tree:
        for child in tree['child']:
            if child==tree['head']:
                continue
            if 'term' in child: # it's a leaf node
                if tree['head']['id'] < child['id']:
                    yield tree['head'], child
                else:
                    yield child, tree['head']
            else:
                head_of_child = child['head'].copy()
                head_of_child['role'] = child['role']
                if tree['head']['id'] < child['head']['id']:
                    yield tree['head'], head_of_child
                else:
                    yield head_of_child, tree['head']
            for r1, r2 in getRelations(child):
                yield r1, r2

raw_text = '我們都喜歡美麗的蝴蝶'
parser = CKIPParser('USERNAME', 'PASSWORD')
result = parser.process(raw_text)
tree_text = result['result'][0]['tree']
#tree_text = 'S(experiencer:NP(Head:Nhaa:我們)|quantity:Dab:都|Head:VK1:喜歡|goal:NP(property:V‧的(head:VH11:美麗|Head:DE:的)|Head:Nab:蝴蝶))'
tree = construct_parsing_tree(tree_text)
for r1, r2 in getRelations(tree):
    print(r1['role'], r1['pos'], r1['term'])
    print(r2['role'], r2['pos'], r2['term'])
    print('-'*50)
