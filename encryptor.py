# ============================================================
#  encryptor.py — Core File Encryption / Decryption Logic
#  (Fixed version of the Encryptor class from app2.py)
# ============================================================

from Crypto.Cipher import AES, DES, DES3, Blowfish, ChaCha20, ARC4, CAST
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class Encryptor:
    """Supports AES, DES, 3DES, Blowfish, ChaCha20, RC4, CAST."""

    SUPPORTED = ['AES', 'DES', '3DES', 'Blowfish', 'ChaCha20', 'RC4', 'CAST']

    def __init__(self, algorithm: str):
        if algorithm not in self.SUPPORTED:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        self.algorithm = algorithm

    # ------------------------------------------------------------------
    # Key Generation
    # ------------------------------------------------------------------

    def generate_key(self) -> bytes:
        """Generate a random key appropriate for the selected algorithm."""
        sizes = {
            'AES':      32,   # 256-bit
            'DES':       8,   # 64-bit
            '3DES':     24,   # 192-bit
            'Blowfish': 16,   # 128-bit
            'ChaCha20': 32,   # 256-bit
            'RC4':      16,   # 128-bit
            'CAST':     16,   # 128-bit
        }
        return get_random_bytes(sizes[self.algorithm])

    # ------------------------------------------------------------------
    # Encryption
    # ------------------------------------------------------------------

    def file_encrypt(self, key: bytes, original_file: str, encrypted_file: str):
        """
        Encrypt original_file and write the result to encrypted_file.
        File format:
          EAX block ciphers : nonce (16B) | tag (16B) | ciphertext
          ChaCha20          : nonce (12B) | ciphertext
          RC4               : ciphertext  (stream, no nonce/tag)
        """
        with open(original_file, 'rb') as f:
            data = f.read()

        if self.algorithm in ('AES', 'DES', '3DES', 'Blowfish', 'CAST'):
            cipher_map = {
                'AES':      lambda: AES.new(key, AES.MODE_EAX),
                'DES':      lambda: DES.new(key, DES.MODE_EAX),
                '3DES':     lambda: DES3.new(key, DES3.MODE_EAX),
                'Blowfish': lambda: Blowfish.new(key, Blowfish.MODE_EAX),
                'CAST':     lambda: CAST.new(key, CAST.MODE_EAX),
            }
            cipher = cipher_map[self.algorithm]()
            padded = pad(data, cipher.block_size)
            ciphertext, tag = cipher.encrypt_and_digest(padded)
            with open(encrypted_file, 'wb') as f:
                f.write(cipher.nonce)    # 16 bytes
                f.write(tag)             # 16 bytes
                f.write(ciphertext)

        elif self.algorithm == 'ChaCha20':
            cipher = ChaCha20.new(key=key)
            ciphertext = cipher.encrypt(data)
            with open(encrypted_file, 'wb') as f:
                f.write(cipher.nonce)    # 12 bytes
                f.write(ciphertext)

        elif self.algorithm == 'RC4':
            cipher = ARC4.new(key)
            ciphertext = cipher.encrypt(data)
            with open(encrypted_file, 'wb') as f:
                f.write(ciphertext)

    # ------------------------------------------------------------------
    # Decryption
    # ------------------------------------------------------------------

    def file_decrypt(self, key: bytes, encrypted_file: str, decrypted_file: str):
        """
        Decrypt encrypted_file and write the plaintext to decrypted_file.
        Raises ValueError if integrity check fails.
        """
        with open(encrypted_file, 'rb') as f:

            if self.algorithm in ('AES', 'DES', '3DES', 'Blowfish', 'CAST'):
                block_sizes = {
                    'AES':      16,
                    'DES':       8,
                    '3DES':      8,
                    'Blowfish':  8,
                    'CAST':      8
                }
                bs         = block_sizes[self.algorithm]
                nonce      = f.read(16)
                tag        = f.read(bs)
                ciphertext = f.read()

                cipher_map = {
                    'AES':      lambda: AES.new(key,  AES.MODE_EAX,      nonce=nonce),
                    'DES':      lambda: DES.new(key,  DES.MODE_EAX,      nonce=nonce),
                    '3DES':     lambda: DES3.new(key, DES3.MODE_EAX,     nonce=nonce),
                    'Blowfish': lambda: Blowfish.new(key, Blowfish.MODE_EAX, nonce=nonce),
                    'CAST':     lambda: CAST.new(key, CAST.MODE_EAX,     nonce=nonce),
                }
                cipher    = cipher_map[self.algorithm]()
                decrypted = cipher.decrypt_and_verify(ciphertext, tag)
                decrypted = unpad(decrypted, cipher.block_size)

            elif self.algorithm == 'ChaCha20':
                nonce      = f.read(8)
                ciphertext = f.read()
                cipher    = ChaCha20.new(key=key, nonce=nonce)
                decrypted = cipher.decrypt(ciphertext)

            elif self.algorithm == 'RC4':
                ciphertext = f.read()
                cipher    = ARC4.new(key)
                decrypted = cipher.decrypt(ciphertext)

            else:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")

        with open(decrypted_file, 'wb') as f:
            f.write(decrypted)
