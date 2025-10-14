class DynamicArray:
    def __init__(self, capacity=1):
        self._n = 0                      
        self._capacity = capacity          
        self._A = [None] * self._capacity    
    def __len__(self):
        return self._n
    def __getitem__(self, k):
        if not 0 <= k < self._n:
            raise IndexError("Invalid index")
        return self._A[k]
    def __setitem__(self, k, value):
        if not 0 <= k < self._n:
            raise IndexError("Invalid index")
        self._A[k] = value
    def append(self, obj):
        if self._n == self._capacity:
            self._resize(2 * self._capacity)
        self._A[self._n] = obj
        self._n += 1
    def insert(self, k, value):
        if self._n == self._capacity:
            self._resize(2 * self._capacity)
        for j in range(self._n, k, -1):
            self._A[j] = self._A[j - 1]
        self._A[k] = value
        self._n += 1
    def remove(self, k):
        if not 0 <= k < self._n:
            raise IndexError("Invalid index")
        value = self._A[k]
        for j in range(k, self._n - 1):
            self._A[j] = self._A[j + 1]
        self._A[self._n - 1] = None
        self._n -= 1
        return value
    def _resize(self, new_cap):
        B = [None] * new_cap
        for k in range(self._n):
            B[k] = self._A[k]
        self._A = B
        self._capacity = new_cap
    def __iter__(self):
        for i in range(self._n):
            yield self._A[i]
    def __repr__(self):
        return "[" + ", ".join(repr(self._A[i]) for i in range(self._n)) + "]"
    def clear(self):
        for i in range(self._n):
            self._A[i] = None
        self._n = 0
