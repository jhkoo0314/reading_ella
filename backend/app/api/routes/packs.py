"""Routes for serving public reading packs."""

from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.pack import PackLoadResponse
from backend.app.services.pack_loader import (
    PackNotFoundError,
    PackRequestError,
    PackServiceError,
    PackValidationError,
    get_public_pack_by_id,
    get_random_public_pack,
)


router = APIRouter(prefix="/packs")


@router.get("", response_model=PackLoadResponse, summary="Load one public pack by level or pack_id")
def read_pack(
    level: str | None = Query(default=None),
    pack_id: str | None = Query(default=None),
    lang: str = Query(default="ko"),
) -> PackLoadResponse:
    try:
        if pack_id and level:
            raise PackRequestError("pack_id와 level은 동시에 보내지 않습니다.")
        if pack_id:
            return get_public_pack_by_id(pack_id, lang=lang)
        if level:
            return get_random_public_pack(level, lang=lang)
        raise PackRequestError("pack_id 또는 level 중 하나는 반드시 보내야 합니다.")
    except PackRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except PackServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{pack_id}", response_model=PackLoadResponse, summary="Load one public pack by pack_id")
def read_pack_by_id(pack_id: str, lang: str = Query(default="ko")) -> PackLoadResponse:
    try:
        return get_public_pack_by_id(pack_id, lang=lang)
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except PackServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
