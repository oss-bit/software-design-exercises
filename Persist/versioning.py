from io import StringIO

# [save]
class SaveObjects:
    def __init__(self, writer):
        self.writer = writer
        self.version = str(1)
    def save(self, thing, first_write=False):
        if first_write:
            self._write('version',self.version)
        typename = type(thing).__name__
        method = f"save_{typename}"
        assert hasattr(self, method), \
            f"Unknown object type {typename}"
        getattr(self, method)(thing)
# [/save]

    def _write(self, *fields):
        print(":".join(str(f) for f in fields), file=self.writer)

    def save_bool(self, thing):
        self._write("bool", thing)

    def save_float(self, thing):
        self._write("float", thing)

    # [save_examples]
    def save_int(self, thing):
        self._write("int", thing)

    def save_str(self, thing):
        lines = thing.split("\n")
        self._write("str", len(lines))
        for line in lines:
            print(line, file=self.writer)
    # [/save_examples]

    def save_list(self, thing):
        self._write("list", len(thing))
        for item in thing:
            self.save(item)

    def save_set(self, thing):
        self._write("set", len(thing))
        for item in thing:
            self.save(item)

    def save_dict(self, thing):
        self._write("dict", len(thing))
        for (key, value) in thing.items():
            self.save(key)
            self.save(value)


# [load]
class LoadObjects:
    def __init__(self, reader):
        self.reader = reader

    def load(self,first_read=False):
        if first_read:
            line = self.reader.readline()[:-1]
            _,verNum = line.split(':')
            if verNum == str(2):
                return LoadAlias(self.reader).load()
    
        line = self.reader.readline()[:-1]
        assert line, "Nothing to read"
        fields = line.split(":", maxsplit=1)
        assert len(fields) == 2, f"Badly-formed line {line}"
        key, value = fields
        method = f"load_{key}"
        assert hasattr(self, method), f"Unknown object type {key}"
        return getattr(self, method)(value)
# [/load]

    def load_bool(self, value):
        names = {"True": True, "False": False}
        assert value in names, f"Unknown Boolean {value}"
        return names[value]

    # [load_float]
    def load_float(self, value):
        return float(value)
    # [/load_float]

    def load_int(self, value):
        return int(value)

    def load_str(self, value):
        return "\n".join(
            [self.reader.readline()[:-1] for _ in range(int(value))]
        )

    # [load_list]
    def load_list(self, value):
        return [self.load() for _ in range(int(value))]
    # [/load_list]

    def load_set(self, value):
        return {self.load() for _ in range(int(value))}

    def load_dict(self, value):
        result = {}
        for _ in range(int(value)):
            k = self.load()
            v = self.load()
            result[k] = v
        return result
    
class SaveAlias(SaveObjects):
    def __init__(self, writer):
        super().__init__(writer)
        self.seen = set()
        self.version = str(2)
        
    # [save]
    def save(self, thing,first_write=False):
        if first_write:
            self._write('version', self.version)
        thing_id = id(thing)
        if thing_id in self.seen:
            self._write("alias", thing_id, "")
            return

        self.seen.add(thing_id)
        typename = type(thing).__name__
        method = f"save_{typename}"
        assert hasattr(self, method), \
            f"Unknown object type {typename}"
        getattr(self, method)(thing)
    # [/save]

    def save_bool(self, thing):
        self._write("bool", id(thing), thing)

    def save_float(self, thing):
        self._write("float", id(thing), thing)

    def save_int(self, thing):
        self._write("int", id(thing), thing)

    def save_list(self, thing):
        self._write("list", id(thing), len(thing))
        for item in thing:
            self.save(item)

    def save_set(self, thing):
        self._write("set", id(thing), len(thing))
        for item in thing:
            self.save(item)

    def save_str(self, thing):
        lines = thing.split("\n")
        self._write("str", id(thing), len(lines))
        for line in lines:
            print(line, file=self.writer)

    def save_dict(self, thing):
        self._write("dict", id(thing), len(thing))
        for (key, value) in thing.items():
            self.save(key)
            self.save(value)

class LoadAlias(LoadObjects):
    def __init__(self,reader):
        super().__init__(reader)
        self.seen = {}
    
    def load(self, first_read=False):
        if first_read:
            line = self.reader.readline()[:-1]
            _, verNum = line.split(':')
            if verNum == str(1):
                return LoadObjects(self.reader).load()
    
        line = self.reader.readline()[:-1]
        print(f"-load with line {repr(line)} and seen {self.seen}")
        assert line, "Nothing to read"
        fields = line.split(":", maxsplit=2)
        assert len(fields) == 3, f"Badly-formed line{line}"
        key, ident, value = fields
        if key == "alias":
            assert ident in self.seen
            return self.seen[ident]
        
        method = f"load_{key}"
        assert hasattr(self, method), f"Unknown object type {key}"
        return getattr(self, method)(ident, value)

    def load_bool(self, ident, value):
        self.seen[ident] = super().load_bool(value)
        return self.seen[ident]

    def load_float(self, ident, value):
        self.seen[ident] = super().load_float(value)
        return self.seen[ident]

    def load_int(self, ident, value):
        self.seen[ident] = super().load_int(value)
        return self.seen[ident]

    def load_str(self, ident, value):
        self.seen[ident] = super().load_str(value)
        return self.seen[ident]

    # [load_list]
    def load_list(self, ident, length):
        result = []
        self.seen[ident] = result
        for _ in range(int(length)):
            result.append(self.load())
        return result
    # [/load_list]

    def load_set(self, ident, length):
        result = set()
        self.seen[ident] = result
        for _ in range(int(length)):
            result.add(self.load())
        return result

    def load_dict(self, ident, length):
        result = {}
        self.seen[ident] = result
        for _ in range(int(length)):
            k = self.load()
            v = self.load()
            result[k] = v
        return result


def roundtrip(fixture):
    # writer = StringIO()
    with open('first.txt', 'w') as writer:
        SaveAlias(writer).save(fixture,first_write=True)

    # reader = StringIO(writer.getvalue())
    with open('first.txt', 'r') as reader:
        return LoadObjects(reader).load(first_read=True)
# [/roundtrip]

def test_no_aliasing():
    fixture = [True, 1, "word"]
    assert roundtrip(fixture) == fixture

def test_duplicated_string():
    fixture = ["word", "word"]
    assert roundtrip(fixture) == fixture

def test_aliased_list():
    fixture = ["word"]
    fixture.append(fixture)
    result = roundtrip(fixture)
    assert len(result) == 2
    assert result[0] == "word"  
    assert isinstance(result[1], list)
    assert len(result[1]) == 2
    assert result[1][0] == "word"

if __name__ == '__main__':
   

    test_no_aliasing()
    test_aliased_list()
    test_duplicated_string()