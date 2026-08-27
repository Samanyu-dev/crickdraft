from fastapi import APIRouter

from ..tournaments import list_tournaments

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


@router.get("")
def get_tournaments():
    return list_tournaments()
