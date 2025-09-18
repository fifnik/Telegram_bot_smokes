from typing import List, Sequence, Tuple, TypeVar

T = TypeVar("T")


def paginate(items: Sequence[T], page: int, per_page: int = 5) -> Tuple[List[T], int]:
    total = len(items)
    start = max(page - 1, 0) * per_page
    end = start + per_page
    return list(items[start:end]), total
