import random
import math
import re
import hashlib


class KandyInt(int):
    def is_odd(self) -> bool:
        """ Return True if self is odd. """
        return bool(self % 2)  # self % 2 => 0: even; 1: odd

    def is_even(self) -> bool:
        """ Return True if self is even. """
        return not bool(self % 2)  # not self % 2 => 1: even; 0: odd

    def is_positive(self) -> bool:
        """ Return True if self >= 0 """
        return (self >= 0)

    def get_percent_of(self, totalvalue=1) -> float:
        """ Return the percent of self/totalvalue """
        return (self / totalvalue) * 100

    def get_percent(self, percent=100) -> float:
        """ Return the percent selected of self """
        return self * (percent / 100)

    def random(self) -> int:
        """ Choice a random number between (self and -self) """
        return random.randint(-self, self)

    def between(self, value1, value2) -> bool:
        """ Return the if self is between value1 and value2 """
        return (self >= value1 and self <= value2)

    def round(self, decimals=0) -> int:
        if decimals == 0:
            return self

        elif decimals >= 1:
            return float(self)

        elif decimals <= -1:
            return round(self*(10**decimals))*10**(-decimals)

    def ceil(self, decimals=0) -> int:
        if decimals == 0:
            return self

        elif decimals >= 1:
            return float(self)

        elif decimals <= -1:
            return math.ceil(self*(10**decimals))*10**(-decimals)

    def floor(self, decimals=0) -> int:
        if decimals == 0:
            return self

        elif decimals >= 1:
            return float(self)

        elif decimals <= -1:
            return math.floor(self*(10**decimals))*10**(-decimals)

    def limit_range(self, start_range=0, end_range=100) -> int:
        return int(min(end_range, max(start_range, self)))

    def integer_part(self) -> int:
        return self

    def decimal_part(self) -> int:
        return 0

    def is_integer(self) -> bool:
        return True


class KandyFloat(float):
    def is_odd(self) -> bool:
        """ Return True if int(self) is odd. """
        return bool(int(self) % 2)  # self % 2 => 0: even; 1: odd

    def is_even(self) -> bool:
        """ Return True if int(self) is even. """
        return not bool(int(self) % 2)  # not self % 2 => 1: even; 0: odd

    def is_positive(self) -> bool:
        """ Return True if self >= 0 """
        return (self >= 0)

    def get_percent_of(self, totalvalue=1) -> float:
        """ Return the percent of self/totalvalue """
        return (self / totalvalue)*100

    def get_percent(self, percent=100) -> float:
        """ Return the percent selected of self """
        return self * (percent / 100)

    def random(self) -> float:
        """ Choice a random number between (self and -self) """
        rand = random.random()
        distance = self + self
        return -self + (rand*distance)

    def between(self, value1, value2) -> bool:
        """ Return the if self is between value1 and value2 """
        return (self >= value1 and self <= value2)

    def round(self, decimals=0) -> float:
        if decimals == 0:
            return round(self, 0)

        elif decimals >= 1:
            return float(self)

        elif decimals <= -1:
            return round(self*(10**decimals))*10**(-decimals)

    def ceil(self, decimals=0) -> float:
        if decimals == 0:
            return math.ceil(self)

        else:
            return round(math.ceil(self*(10**(decimals)))*10**(-decimals), decimals)

    def floor(self, decimals=0) -> float:
        if decimals == 0:
            return math.floor(self)

        else:
            return round(math.floor(self*(10**(decimals)))*10**(-decimals), decimals)

    def limit_range(self, start_range=0, end_range=100):
        return min(end_range, max(start_range, self))

    def integer_part(self) -> int:
        return int(self)

    def decimal_part(self) -> int:
        return self - int(self)


class KandyStr(str):
    def reverse(self) -> str:
        """ Return the text reversed """
        return self[::-1]

    def replace_with_dict(self, values_dict) -> str:
        """ Replace all ocurrencies, with an dict """
        output = self
        for key, value in values_dict.items():
            output = output.replace(key, value)

        return output

    def replace_regex(self, pattern, newvalue, nmax=-1, flags=None) -> str:
        string = self
        count = 0
        for match in re.finditer(pattern, string, flags):
            pos, endpos = match.span()
            string = string[:pos] + newvalue + string[endpos:]
            count += 1

            if count == nmax:
                break

        return string

    def split_regex(self, pattern, nmax=-1, flags=None) -> tuple:
        return re.split(pattern, self, nmax, flags)

    def find_regex(self, pattern) -> tuple:
        for match in re.finditer(pattern, self):
            pos, endpos = match.span()
            return (match.group(), pos, endpos)

        return None

    def match_regex(self, pattern) -> str:
        return re.match(pattern, self)

    def get_sha3(self, mode=256) -> str:
        encoded = self.encode()
        if mode == 256:
            hashdata = hashlib.sha3_256(encoded)
            return hashdata.hexdigest()

        elif mode == 384:
            hashdata = hashlib.sha3_384(encoded)
            return hashdata.hexdigest()

        elif mode == 512:
            hashdata = hashlib.sha3_512(encoded)
            return hashdata.hexdigest()

        elif mode == 224:
            hashdata = hashlib.sha3_224(encoded)
            return hashdata.hexdigest()

        else:
            raise ValueError("Invalid sha3 mode. Values: 224, 256, 384, 512")

    def simple_encrypt(self, password="password") -> str:
        sha = KandyStr.get_sha3(password)
        random.seed(int(sha, base=16))
        order = random.sample(range(len(self)), len(self))
        output = ""
        for o in order:
            output += self[o]

        return output

    def simple_decrypt(self, password="password") -> str:
        sha = KandyStr.get_sha3(password)
        random.seed(int(sha, base=16))
        order = random.sample(range(len(self)), len(self))
        output = ""
        for pos in range(len(self)):
            output += self[order.index(pos)]

        return output

    def filter(self, func) -> str:
        return "".join(filter(func, self))

    def for_each(self, func) -> str:
        return "".join(map(func, self))

    def map(self, func):
        return map(func, self)

    def unsort(self):
        t = tuple(self)
        output = ""
        for i in random.sample(t, len(t)):
            output += i

        return output


class KandyList(list):
    def random_choice(self, number=1):
        return random.sample(self, number)

    def unsort(self):
        ls = self.copy()
        self.clear()
        for i in random.sample(ls, len(ls)):
            self.append(i)

    def sort_by_position_list(self, order):
        ls = self.copy()
        self.clear()
        for i in order:
            self.append(ls[i])

    def for_each(self, func, save=True):
        if save:
            ls = self.copy()
            self.clear()
            for i in map(func, ls):
                self.append(i)

            return self
        else:
            result = []
            for i in map(func, ls):
                result.append(i)

            return result

    def filter(self, func):
        ls = self.copy()
        self.clear()
        for i in filter(func, ls):
            self.append(i)

    def map(self, func):
        return map(func, self)


class KandyTuple(tuple):
    def random_choice(self, number=1):
        return random.sample(self, number)

    def unsort(self):
        return tuple(random.sample(self, len(self)))

    def sort_by_position_list(self, order):
        ls = []
        for i in order:
            ls.append(self[i])

        return tuple(ls)

    def for_each(self, func):
        return tuple(map(func, self))

    def filter(self, func):
        return tuple(filter(func, self))

    def map(self, func):
        return map(func, self)


class KandyDict(dict):
    def random_choice(self, number=1):
        return random.sample(self.items(), number)

    def unsort(self):
        dc = self.copy()
        self.clear()
        for key, value in tuple(random.sample(dc.items(), len(dc))):
            self[key] = value

    def sort(self):
        dc = self.copy()
        self.clear()
        for key, value in sorted(dc.items()):
            self[key] = value

    def sort_by_keys(self):
        return sorted(self.items(), key=lambda x: x[0])

    def sort_by_value(self):
        return sorted(self.items(), key=lambda x: x[1])

    def for_each(self, func):
        return dict(map(func, self.items()))

    def filter(self, func):
        return dict(filter(func, self.items()))

    def map(self, func):
        return map(func, self.items())
