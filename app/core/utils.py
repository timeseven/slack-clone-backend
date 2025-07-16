import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from nanoid import generate
from redis.asyncio import Redis


async def set_redis_value(
    redis: Redis,
    name: str,
    value: str,
    expires_in: int | timedelta | datetime | None = None,
    nx: bool = False,
    xx: bool = False,
):
    kwargs = {}

    # Handle expiration
    if expires_in is not None:
        if isinstance(expires_in, datetime):
            expires_in = expires_in - datetime.now(timezone.utc)
        if isinstance(expires_in, timedelta):
            kwargs["ex"] = int(expires_in.total_seconds())
        elif isinstance(expires_in, int):
            kwargs["ex"] = expires_in

    # Handle NX and XX
    if nx:
        kwargs["nx"] = True
    if xx:
        kwargs["xx"] = True

    await redis.set(name, value, **kwargs)


async def get_redis_value(redis: Redis, name: str) -> str | None:
    return await redis.get(name)


async def delete_redis_value(redis: Redis, name: str):
    await redis.delete(name)


# Used only in route handlers to compare old object and input data,
# computing fields to update (supports selectively allowing None values).
# Internal service layer updates should directly pass update values without this function.
def compute_update_fields_from_dict(
    old: Any,
    new_data: dict[str, Any],
    include_none_fields: list[str] | None = None,
) -> dict[str, Any]:
    update_fields = {}

    include_fields = new_data.keys()
    include_none_fields = set(include_none_fields or [])

    for field in include_fields:
        # Skip fields that are not in the new data
        if field not in new_data:
            continue

        # Skip fields that are None and not in include_none_fields
        new_value = new_data[field]
        if new_value is None and field not in include_none_fields:
            continue

        # Get the old value
        old_value = getattr(old, field, None) if hasattr(old, field) else old.get(field, None)

        if new_value != old_value:
            update_fields[field] = new_value

    return update_fields


# Avoid 0/O and 1/I/l
SAFE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
ID_SIZE = 11


def generate_short_id(prefix: str = "", size: int = ID_SIZE) -> str:
    return prefix + generate(alphabet=SAFE_ALPHABET, size=size)


def generate_channel_id(channel_type: str) -> str:
    prefix = {"channel": "C", "group_dm": "G"}.get(channel_type)

    if not prefix:
        raise ValueError(f"Invalid channel type: {channel_type}")

    return generate_short_id(prefix)


def generate_dm_id(workspace_id: str, user_id1: str, user_id2: str) -> str:
    sorted_ids = sorted([user_id1, user_id2])
    combined = f"{workspace_id}:{sorted_ids[0]}:{sorted_ids[1]}"

    digest = hashlib.sha256(combined.encode("utf-8")).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return f"D{encoded[:ID_SIZE]}"


# Password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")
