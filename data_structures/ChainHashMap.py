from collections.abc import MutableMapping
from random import randrange

class MapBase(MutableMapping):
    class Item:
        __slots__ = 'key', 'value'
        def __init__(self, k, v):
            self.key = k
            self.value = v
        def __eq__(self, other):
            return self.key == other.key
        def __ne__(self, other):
            return not (self == other)
        def __lt__(self, other):
            return self.key < other.key

class UnsortedTableMap(MapBase):
    def __init__(self):
        self.table = []
    def __getitem__(self, k):
        for item in self.table:
            if k == item.key:
                return item.value
        raise KeyError(f"Key Error: {k}")
    def __setitem__(self, k, v):
        for item in self.table:
            if k == item.key:
                item.value = v
                return
        self.table.append(self.Item(k, v))
    def __delitem__(self, k):
        for j in range(len(self.table)):
            if k == self.table[j].key:
                self.table.pop(j)
                return
        raise KeyError(f"Key Error: {k}")
    def __len__(self):
        return len(self.table)
    def __iter__(self):
        for item in self.table:
            yield item.key
    def items(self):
        for item in self.table:
            yield (item.key, item.value)

class HashMapBase(MapBase):
    def __init__(self, cap=11, p=109245121):
        self.table = cap * [None]
        self.n = 0
        self.prime = p
        self.scale = 1 + randrange(p - 1)
        self.shift = randrange(p)
    def hash_function(self, k):
        return (hash(k) * self.scale + self.shift) % self.prime % len(self.table)
    def __len__(self):
        return self.n
    def __getitem__(self, k):
        j = self.hash_function(k)
        return self.bucket_getitem(j, k)
    def __setitem__(self, k, v):
        j = self.hash_function(k)
        self.bucket_setitem(j, k, v)
        if self.n > len(self.table) // 2:
            self.resize(2 * len(self.table) - 1)
    def __delitem__(self, k):
        j = self.hash_function(k)
        self.bucket_delitem(j, k)
        self.n -= 1
    def resize(self, c):
        old = list(self.items())
        self.table = c * [None]
        self.n = 0
        for (k, v) in old:
            self[k] = v

class ChainHashMap(HashMapBase):
    def bucket_getitem(self, j, k):
        bucket = self.table[j]
        if bucket is None:
            raise KeyError(f"Key Error: {k}")
        return bucket[k]
    def bucket_setitem(self, j, k, v):
        if self.table[j] is None:
            self.table[j] = UnsortedTableMap()
        oldsize = len(self.table[j])
        self.table[j][k] = v
        if len(self.table[j]) > oldsize:
            self.n += 1
    def bucket_delitem(self, j, k):
        bucket = self.table[j]
        if bucket is None:
            raise KeyError(f"Key Error: {k}")
        del bucket[k]
    def __iter__(self):
        for bucket in self.table:
            if bucket is not None:
                for key in bucket:
                    yield key
    def __contains__(self, key):
        try:
            _ = self[key]
            return True
        except KeyError:
            return False
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]
    def keys(self):
        for k in self:
            yield k
    def values(self):
        for k in self:
            yield self[k]
    def items(self):
        for k in self:
            yield (k, self[k])
    def clear(self):
        self.table = [None] * len(self.table)
        self.n = 0
    def __repr__(self):
        pairs = [f"{k}: {self[k]!r}" for k in self]
        return "{" + ", ".join(pairs) + "}"
