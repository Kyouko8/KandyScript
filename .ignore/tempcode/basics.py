
class KandyInt():

    def m_iadd(self, other):
        self.value += self._get_value(other)

    def m_isub(self, other):
        self.value -= self._get_value(other)

    def m_imult(self, other):
        self.value *= self._get_value(other)

    def m_ifloordiv(self, other):
        self.value //= self._get_value(other)

    def m_imod(self, other):
        self.value %= self._get_value(other)

    def m_isubmod(self, other):
        value2 = self._get_value(other)
        self.value = value2 - (self.value % value2)

    def m_ipow(self, other):
        self.value **= self._get_value(other)

    def m_iand(self, other):
        self.value &= self._get_value(other)

    def m_ior(self, other):
        self.value |= self._get_value(other)

    def m_ixor(self, other):
        self.value = int(self.value ^ self._get_value(other))
