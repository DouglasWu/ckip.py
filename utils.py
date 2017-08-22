# -*- coding: utf-8 -*-

def construct_parsing_tree(tree_text):
    parent_node = None
    current_node = {}

    node_queue = []
    text = ''
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
            if 'role' in current_node:
                current_node['pos'] = text
            else:
                current_node['role'] = text
            text = ''

        else:
            text += char

    return current_node

def find_head(tree):
    head = tree
    if 'child' in tree:
        headFound = False
        for child in tree['child']:
            if not headFound and (child['role']=='Head' or child['role']=='head'):
                head = find_head(child)
                headFound = True
            elif headFound and child['role']=='head':
                head = find_head(child)
    return head

def get_relations(tree):
    if 'child' in tree:
        # create a copy of the head
        # and modify its role to include the 'pos' information
        head_of_tree = find_head(tree).copy()
        head_of_tree['role'] += '[{}]'.format(tree['pos'])
        for child in tree['child']:
            if child['id']==head_of_tree['id']:
                continue
            if 'term' in child: # if child is a leaf node
                if head_of_tree['id'] < child['id']:
                    yield head_of_tree, child
                else:
                    yield child, head_of_tree
            else:
                head_of_child = find_head(child).copy()
                head_of_child['role'] = child['role']
                if head_of_child['id']==head_of_tree['id']:
                    continue
                if head_of_tree['id'] < head_of_child['id']:
                    yield head_of_tree, head_of_child
                else:
                    yield head_of_child, head_of_tree
            for r1, r2 in get_relations(child):
                yield r1, r2
                
                
# check if the node contains DUMMY1 and DUMMY2
def has_dummies(node):
    if 'child' in node:
        # the roles of all node's children
        roles = [n['role'] for n in node['child']]
        return 'DUMMY1' in roles and 'DUMMY2' in roles
    return False

# check if the pos is PP or GP
# and contains a DUMMY child
def pp_gp(node):
    if node['pos'] not in ['PP', 'GP']:
        return False
    for n in node['child']:
        if n['role'] == 'DUMMY':
            return True
    return False

# get dummy1 and dummy2
def get_dummies(node):
    if not has_dummies(node):
        raise Exception('node does not have dummies!')
    dummy1 = {}
    dummy2 = {}
    for n in node['child']:
        if n['role']=='DUMMY1':
            dummy1 = find_head(n).copy()
            dummy1['role'] = n['role']
        if n['role']=='DUMMY2':
            dummy2 = find_head(n).copy()
            dummy2['role'] = n['role']
    return dummy1, dummy2

# get the node information
# of node with pos type PP or GP
def get_pp_gp_node(node):
    def get_term_pos(node1, node2):
        term1, pos1 = node1['term'], node1['pos']
        term2, pos2 = node2['term'], node2['pos']
        if node1['id'] < node2['id']:
            return '{}..{}'.format(term1, term2), '{}..{}'.format(pos1, pos2)
        else:
            return '{}..{}'.format(term2, term1), '{}..{}'.format(pos2, pos1)
    
    head_of_dummy = {}
    for n in node['child']:
        if n['role'] == 'DUMMY':
            head_of_dummy = find_head(n)
            break
    head_of_node = find_head(node).copy()
    head_of_node['role'] = node['role']
    term, pos = get_term_pos(head_of_node, head_of_dummy)
    head_of_node['term'] = term
    head_of_node['pos'] = pos
    return head_of_node

def order_relation(node1, node2):
    if node1['id'] < node2['id']:
        return node1, node2
    else:
        return node2, node1

def get_relations_all(tree):
    if 'child' in tree:
        # create a copy of the head
        # and modify its role to include the 'pos' information
        head_of_tree = find_head(tree).copy()
        head_of_tree['role'] += '[{}]'.format(tree['pos'])
        for child in tree['child']:
            if child['id']==head_of_tree['id']:
                continue
            if 'term' in child: # if child is a leaf node
                yield order_relation(head_of_tree, child)
            else:
                head_of_child = find_head(child).copy()
                if head_of_child['id']==head_of_tree['id']:
                    continue
                if has_dummies(child):
                    dummy1, dummy2 = get_dummies(child)
                    yield order_relation(dummy1, head_of_tree)
                    yield order_relation(dummy2, head_of_tree)
                elif pp_gp(child):
                    yield order_relation(get_pp_gp_node(child), head_of_tree)
                else:
                    head_of_child['role'] = child['role']
                    yield order_relation(head_of_tree, head_of_child)

            for r1, r2 in get_relations_all(child):
                yield r1, r2