# -*- coding: utf-8 -*-

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

def get_relations(tree):
    if 'child' in tree:
        # create a copy of the head
        # and modify its role to include the 'pos' information
        head_of_tree = tree['head'].copy()
        head_of_tree['role'] += '[{}]'.format(tree['pos'])
        for child in tree['child']:
            if child==tree['head']:
                continue    
            if 'term' in child: # if child is a leaf node
                if head_of_tree['id'] < child['id']:
                    yield head_of_tree, child
                else:
                    yield child, head_of_tree
            else:
                head_of_child = child['head'].copy()
                head_of_child['role'] = child['role']
                if head_of_tree['id'] < head_of_child['id']:
                    yield head_of_tree, head_of_child
                else:
                    yield head_of_child, head_of_tree
            for r1, r2 in get_relations(child):
                yield r1, r2
