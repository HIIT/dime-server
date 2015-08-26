from ete2 import Tree
root_tree = Tree()
fname = 'skills_hierarchy.txt'
with open(fname) as f:
    content = f.readlines()

i = 0

def addNodes(current_node, parent_node,level):
    global i
    new_parent_node = parent_node.add_child(name=current_node,dist = 0.0)
    i = i+1
    if(i >= len(content)):
        return
    new_node = content[i]
    new_node = new_node[:-1]
    new_level = len(new_node) - len(new_node.lstrip('-'))
    new_node = new_node.lstrip('-').lower().replace('&amp;', '&')
    while(new_level > level):
        addNodes(new_node,new_parent_node,new_level)
        if(i >= len(content)):
            return
        new_node = content[i]
        new_node = new_node[:-1]
        new_level = len(new_node) - len(new_node.lstrip('-'))
        new_node = new_node.lstrip('-').lower().replace('&amp;', '&')


current_node = content[0][:-1].lower().replace('&amp;', '&')
while(i < len(content)):
    addNodes(current_node,root_tree,0)
    if(i >= len(content)):
        break
    current_node = content[i][:-1].lower().replace('&amp;', '&')

    

print 'Skills Tree Constructed'
def getAncestors(skill):
    lis = []
    f = root_tree.search_nodes(name=skill)[0]
    node = f
    while node:
        if(node.name == ''):
            node = node.up
            continue
        lis.append(node.name)
        node = node.up
    return lis

def search_phrase_set(node, phrase):
    matches = []
    sp_phrase = set(phrase.split(' '))
    for n in node.traverse():
        name = set(n.name.split(' '))
        if (sp_phrase.intersection(name)==sp_phrase):
            matches.append(n.name)
    return matches
    
def getAllChildren(node):
    ret = []
    for n in node.traverse():
        ret.append(n.name)
    return set(ret)


def search_phrase(node, phrase):
    matches = []
    for n in node.traverse():
        name = n.name
        if (n.name == phrase):
            matches.append(n)
    return matches




