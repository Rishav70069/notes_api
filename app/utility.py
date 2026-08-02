from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")


def verify_password(plain_password, hashed_password) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


# Always performs a hash verification to reduce timing differences.
def verify_password_or_dummy(plain_password: str, hashed_password: str | None) -> bool:

    if hashed_password is None:
        password_hash.verify(plain_password, DUMMY_HASH)
        return False

    return password_hash.verify(plain_password, hashed_password)
