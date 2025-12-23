"""
Utility functions for UUID7 generation.
UUID7 is time-ordered and sortable, making it suitable for use as primary keys.
"""
from uuid import UUID
from uuid_utils import uuid7 as generate_uuid7


def uuid7() -> UUID:
    """
    Generate a UUID7 (time-ordered UUID).
    UUID7 values are sortable and increase over time.
    """
    generated = generate_uuid7()
    if isinstance(generated, UUID):
        return generated
    return UUID(str(generated))

