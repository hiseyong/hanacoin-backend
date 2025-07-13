from ecdsa import SigningKey, SECP256k1
import hashlib
import binascii

def generate_wallet_keys():
    sk = SigningKey.generate(curve=SECP256k1)
    private_key = sk.to_string().hex()
    vk = sk.get_verifying_key()
    public_key = vk.to_string().hex()

    # 예: 공개키 해시 → 지갑 주소 (간단히 RIPEMD160 해시 예시)
    sha256_pk = hashlib.sha256(binascii.unhexlify(public_key)).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_pk)
    wallet_address = ripemd160.hexdigest()

    return private_key, public_key, wallet_address