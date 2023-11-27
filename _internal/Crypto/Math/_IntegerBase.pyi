from typing import Optional, Union, Callable

RandFunc = Callable[[int],int]

class IntegerBase:

    def __init__(self, value: Union[IntegerBase, int]): ...

    def __int__(self) -> int: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def to_bytes(self, block_size: Optional[int]=0, byteorder: str= ...) -> bytes: ...
    @staticmethod
    def from_bytes(byte_string: bytes, byteorder: Optional[str] = ...) -> IntegerBase: ...
    def __eq__(self, term: object) -> bool: ...
    def __ne__(self, term: object) -> bool: ...
    def __lt__(self, term: Union[IntegerBase, int]) -> bool: ...
    def __le__(self, term: Union[IntegerBase, int]) -> bool: ...
    def __gt__(self, term: Union[IntegerBase, int]) -> bool: ...
    def __ge__(self, term: Union[IntegerBase, int]) -> bool: ...
    def __nonzero__(self) -> bool: ...
    def is_negative(self) -> bool: ...
    def __add__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __sub__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __mul__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __floordiv__(self, divisor: Union[IntegerBase, int]) -> IntegerBase: ...
    def __mod__(self, divisor: Union[IntegerBase, int]) -> IntegerBase: ...
    def inplace_pow(self, exponent: int, modulus: Optional[Union[IntegerBase, int]]=None) -> IntegerBase: ...
    def __pow__(self, exponent: int, modulus: Optional[int]) -> IntegerBase: ...
    def __abs__(self) -> IntegerBase: ...
    def sqrt(self, modulus: Optional[int]) -> IntegerBase: ...
    def __iadd__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __isub__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __imul__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __imod__(self, divisor: Union[IntegerBase, int]) -> IntegerBase: ...
    def __and__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __or__(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def __rshift__(self, pos: Union[IntegerBase, int]) -> IntegerBase: ...
    def __irshift__(self, pos: Union[IntegerBase, int]) -> IntegerBase: ...
    def __lshift__(self, pos: Union[IntegerBase, int]) -> IntegerBase: ...
    def __ilshift__(self, pos: Union[IntegerBase, int]) -> IntegerBase: ...
    def get_bit(self, n: int) -> bool: ...
    def is_odd(self) -> bool: ...
    def is_even(self) -> bool: ...
    def size_in_bits(self) -> int: ...
    def size_in_bytes(self) -> int: ...
    def is_perfect_square(self) -> bool: ...
    def fail_if_divisible_by(self, small_prime: Union[IntegerBase, int]) -> None: ...
    def multiply_accumulate(self, a: Union[IntegerBase, int], b: Union[IntegerBase, int]) -> IntegerBase: ...
    def set(self, source: Union[IntegerBase, int]) -> IntegerBase: ...
    def inplace_inverse(self, modulus: Union[IntegerBase, int]) -> IntegerBase: ...
    def inverse(self, modulus: Union[IntegerBase, int]) -> IntegerBase: ...
    def gcd(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    def lcm(self, term: Union[IntegerBase, int]) -> IntegerBase: ...
    @staticmethod
    def jacobi_symbol(a: Union[IntegerBase, int], n: Union[IntegerBase, int]) -> IntegerBase: ...
    @staticmethod
    def _tonelli_shanks(n: Union[IntegerBase, int], p: Union[IntegerBase, int]) -> IntegerBase : ...
    @classmethod
    def random(cls, **kwargs: Union[int,RandFunc]) -> IntegerBase : ...
    @classmethod
    def random_range(cls, **kwargs: Union[int,RandFunc]) -> IntegerBase : ...

