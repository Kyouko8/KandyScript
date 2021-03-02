# Cifrado

class CompressBytes():
    def __init__(self, basedict=None):
        self.basedict = self._get_basedict(basedict)

    def _get_basedict(self, dict_obj):
        output = {}
        if dict_obj is None:
            dict_obj = {}

        output.update(dict_obj)
        for n in range(0, 255):
            output[bytes((n,))] = n

        return output

    def compress(self, text, char_map=None):
        if char_map is None:
            char_map = self.basedict.copy()

        if isinstance(text, bytes):
            bytes_text = text

        else:
            bytes_text = str(text).encode()

        last = max(char_map.values()) + 1
        # compress_text = b""
        w = b""
        for t in bytes_text:
            char = bytes((t,))
            w_char = w+char
            if w_char in char_map:
                w = w_char
            else:
                print(w)
                char_map[w_char] = last
                last += 1
                w = char

        print(w)
        print(char_map)


c = CompressBytes()
c.compress("Hola mundo, hola mundo, hola mundo, hola mundo, hola mundo, hola mundo, hola mundo")
