from typing import Optional
from typing_extensions import Protocol

from Crypto.PublicKey.RSA import RsaKey

class Hash(Protocol):
    def digest(self) -> bytes: ...

class PKCS115_SigScheme:
    def __init__(self, rsa_key: RsaKey) -> None: ...
    def can_sign(self) -> bool: ...
    def sign(self, msg_hash: Hash) -> bytes: ...
    def verify(self, msg_hash: Hash, signature: bytes) -> bool: ...


def new(rsa_key: RsaKey) -> PKCS115_SigScheme: ...
