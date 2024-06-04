class DataFrame:
    def ncol(self):
        """Report the number of columns"""
    
    def nrow(self):
        """Report the number of rows"""
    
    def cols(self):
        """Return the set of columns name"""
    
    def eq(self, other):
        """Check equality with another dataframe"""
    
    def get(self, col, row):
        """Get a scalr value"""
    
    def select(self, *others):
        """Select a named subset of columns"""
    
    def filter(self, func):
        """Selecte a subset of rows be testing values"""


def all_eg(*values):
    return (not values) or all(v==values[0] for v in values)


class DfCol(DataFrame):
    def __init__(self, **kwargs):
        assert len(kwargs) > 0 
        assert all_eg(len(kwargs[k]) for k in kwargs)
        for k in kwargs:
            assert all_eg(type(v) for v in kwargs[k])
        self._data = kwargs
    
    def ncol(self):
        return len(self._data)
    
    def nrow(self):
        n = list(self._data.keys())[0]
        return len(self._data[n])
    
    def cols(self):
        return set(self._data.keys())
    
    def get(self, col, row):
        assert col in self._data 
        assert 0 <= row < len(self._data[col])
        return self._data[col][row]
    
    def eq(self, other):
        assert isinstance(other, DataFrame)
        for n in self._data:
            if n not in other.cols():
                return False
            for i in range(len(self._data[n])):
                if self.get(n,i) != other.get(n,i):
                    return False
        return True

    def select(self, *names):
        assert all(n in self._data for n in names)
        return DfCol(**{n: self._data[n] for n in names})
    
    def __str__(self):
        return str(self._data)


    def filter(self,func):
        result = {n:[] for n in self._data}
        cols = [col for (i,col) in self._data.items() if len(i) >=3]
        for i_row in range(self.ncol()):
            if func(i_row, *cols):
                for n in self._data:
                    result[n].append(self._data[n][i_row])
