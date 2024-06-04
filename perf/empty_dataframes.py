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

def dict_match(d, prototype):
    if set(d.keys()) != set(prototype.keys()):
        return False
    return all(type(d[k]) == type(prototype[k]) for k in d)

def check_empty_RowDf(rows):
    result = []
    for row in rows:
        result.append(all([type(row[col]) == None for col in row]))
    return all(result)

class DfRow(DataFrame):
    def __init__(self,rows):
        assert len(rows) > 0
        if not check_empty_RowDf(rows):
            assert all(dict_match(r, rows[0]) for r in rows)
        self._data = rows

    def ncols(self):
        return len(self._data[0])
    
    def nrow(self):
        return len(self._data)
    
    def cols(self):
        return set(self._data[0].keys())
    
    def get(self, col, row):
        assert col in self._data[0]
        assert 0 <= row < len(self._data)
        return self._data[row][col]
    
    def eq(self, other):
        assert isinstance(other, DataFrame)
        for (i, row) in enumerate(self._data):
            for key in row:
                if key not in other.cols():
                    return False
                if row[key] != other.get(key, i):
                    return False
        return True
    
    def select(self, *names):
        assert all(n in self._data[0] for n in names)
        rows =[{key:r[key] for key in names} for r in self._data]
        return DfRow(rows)
    
    def filter(self, func):
        result = [r for r in self._data if func(**r)]
        return DfRow(result)
    
    def __str__(self):
        return str(self._data)
