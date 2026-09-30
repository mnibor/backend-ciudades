"""CRUD routes for the ``cities`` resource."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import City
from app.schemas import CityCreate, CityRead, CityUpdate

router = APIRouter(prefix="/cities", tags=["cities"])


def _name_taken(
    db: Session,
    name: str,
    exclude_id: int | None = None,
) -> bool:
    """Return True when another city already owns ``name``.

    Uniqueness is enforced case-insensitively at the application level
    (``Buenos Aires`` and ``buenos aires`` collide). The database unique
    index stays case-sensitive on purpose: this demo keeps a single, clear
    place where the rule is expressed.
    """
    stmt = select(City.id).where(func.lower(City.name) == name.lower())
    if exclude_id is not None:
        stmt = stmt.where(City.id != exclude_id)
    return db.scalar(stmt) is not None


@router.post("", response_model=CityRead, status_code=201)
def create_city(payload: CityCreate, db: Session = Depends(get_db)) -> City:
    if _name_taken(db, payload.name):
        raise HTTPException(
            status_code=409,
            detail=f"City '{payload.name}' already exists.",
        )

    city = City(name=payload.name)
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


@router.get("", response_model=list[CityRead])
def list_cities(db: Session = Depends(get_db)) -> list[City]:
    return list(db.scalars(select(City).order_by(City.name)).all())


@router.get("/{city_id}", response_model=CityRead)
def get_city(city_id: int, db: Session = Depends(get_db)) -> City:
    city = db.scalar(select(City).where(City.id == city_id))
    if city is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found.")
    return city


@router.put("/{city_id}", response_model=CityRead)
def update_city(
    city_id: int,
    payload: CityUpdate,
    db: Session = Depends(get_db),
) -> City:
    city = db.scalar(select(City).where(City.id == city_id))
    if city is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found.")

    if payload.name is not None:
        if _name_taken(db, payload.name, exclude_id=city_id):
            raise HTTPException(
                status_code=409,
                detail=f"City '{payload.name}' already exists.",
            )
        city.name = payload.name

    db.commit()
    return city


@router.delete("/{city_id}", status_code=204)
def delete_city(city_id: int, db: Session = Depends(get_db)) -> None:
    city = db.scalar(select(City).where(City.id == city_id))
    if city is None:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found.")

    db.delete(city)
    db.commit()
