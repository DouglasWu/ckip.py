# -*- coding: utf-8 -*-

def construct_parsing_tree(tree_text):
    parent_node = None
    current_node = {'role': 'root'}

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


# check if the node contains DUMMY1 and DUMMY2
def has_dummies(node):
    if 'child' in node:
        # the roles of all node's children
        roles = [n['role'] for n in node['child']]
        return 'DUMMY1' in roles and 'DUMMY2' in roles
    return False

# get dummy1 and dummy2
def get_dummies(node):
    if not has_dummies(node):
        raise Exception('node does not have dummies!')
    dummy1 = {}
    dummy2 = {}
    for n in node['child']:
        if n['role']=='DUMMY1':
            tmp = find_head(n)
            dummy1 = tmp[0].copy()
        if n['role']=='DUMMY2':
            tmp = find_head(n)
            dummy2 = tmp[0].copy()
    return [dummy1, dummy2]

# get the node information
# of node with pos type PP or GP
def get_pp_gp_node(node, level=0):
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
            head_of_dummy = find_head(n, level+1)
            break
    nodes = []
    for hd in head_of_dummy:
        head_of_node = find_tree_head(node).copy()
        head_of_node['role'] = node['role']
        term, pos = get_term_pos(head_of_node, hd)
        head_of_node['term'] = term
        head_of_node['pos'] = pos
        nodes.append(head_of_node)
    
    return nodes

# Return a list of nodes that represents the child
# When there are dummy1 and dummy2, it's a two-element list
# otherwise it's a one-element list
# 1. when there are dummies, return the heads of the two dummies
# 2. when there's a DE, find head of the other child A and return A
# 3. when it's a PP or GP, find the head of the DUMMY child A and return 在..A
def find_head(tree, level=0):
    if 'child' in tree:
        head = []
        if has_dummies(tree):
            head = get_dummies(tree)
        else:
            for child in tree['child']:
                if child['role']=='DUMMY':
                    if tree['pos'] in ['PP', 'GP']:
                        if level==0:
                            head = get_pp_gp_node(tree, level+1)
                        else:
                            head = find_head(child, level+1)
                        break
                elif child['role']=='head':
                    head = find_head(child, level+1)
                    break
                elif child['role']=='Head':
                    if child['pos']=='DE': # find another node
                        for tmp in tree['child']:
                            if tmp['id']!=child['id']:
                                head = find_head(tmp, level+1)
                                break
                        break
                    elif tree['pos'] in ['PP', 'GP']:
                        # continue only if DUMMY is a child
                        if 'DUMMY' in [node['role'] for node in tree['child']]:
                            continue
                    head = find_head(child, level+1)
        if head==[]: # if no head found, choose the last node
            head = find_head(tree['child'][-1], level+1)
        return head
    else:
        return [tree]

# find the head in the tree
def find_tree_head(tree):
    if 'child' in tree:
        head = None
        for child in tree['child']:
            if child['role'] in ['head', 'Head']:
                head = find_tree_head(child)
        if head==None:
            # if no head found, choose the last node as head
            head = find_tree_head(tree['child'][-1])
        return head
    else:
        return tree

def order_relation(node1, node2):
    if node1['id'] < node2['id']:
        return node1, node2
    else:
        return node2, node1

def get_relations_all(tree):
    if 'child' in tree:        
        # create a copy of the head
        # and modify its role to include the 'pos' information
        head_of_tree = find_tree_head(tree).copy()
        if 'head' in head_of_tree['role'].lower():
            head_of_tree['role'] += '[{}]'.format(tree['pos'])
        
        # get (dummy1, dummy2) relation
        # when (Head,'Caa') is the direct child of tree
        tags = [(child['role'], child['pos']) for child in tree['child']]
        if ('Head', 'Caa') in tags and has_dummies(tree):
            dummy1, dummy2 = get_dummies(tree)
            dummy1['role'] = 'DUMMY1'
            dummy2['role'] = 'DUMMY2'
            yield order_relation(dummy1, dummy2)

        for child in tree['child']:
            if child['id']!=head_of_tree['id']:
                # if child is a leaf node
                if 'term' in child and head_of_tree['pos']!='Caa':
                    yield order_relation(head_of_tree, child)
                elif head_of_tree['pos']!='Caa':
                    # get a list of nodes from find_head
                    for node in find_head(child):
                        head_of_child = node.copy()
                        head_of_child['role'] = child['role']
                        yield order_relation(head_of_tree, head_of_child)
            
            for r1, r2 in get_relations_all(child):
                yield r1, r2