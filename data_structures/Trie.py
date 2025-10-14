class TrieNode:
    def __init__(self):
        self.children = {}
        self.numbers = set()
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self,key,number):
        key = key.lower()
        node = self.root
        for child in key:
            if child not in node.children:
                node.children[child] = TrieNode()
            node = node.children[child]
            node.numbers.add(number)
        node.is_end = True
        node.numbers.add(number)
    def prefix_numbers(self,prefix,limit=200):
        node = self.root 
        for child in prefix.lower():
            if child not in node.children:
                return set()
            node = node.children[child]
        res = list(node.numbers)
        return set(res[:limit])
    def collect_all(self,node=None):
        if node is None:
            node = self.root
        res = set()
        if node.is_end:
            res |= node.numbers
        for child in node.children.values():
            res |= self.collect_all(child)
        return res