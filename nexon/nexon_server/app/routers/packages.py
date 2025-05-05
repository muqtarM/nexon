from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import SessionLocal
from app.models.package import Package
from app.schemas.package import PackageOut, PackageCreate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/packages", tags=["packages"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PackageOut, status_code=status.HTTP_201_CREATED)
def create_package(
        payload: PackageCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    # Composite PK check
    if db.query(Package).filter_by(name=payload.name, version=payload.version).first():
        raise HTTPException(409, "Package-version already exists")
    pkg = Package(
        name=payload.name,
        version=payload.version,
        description=payload.description,
        spec=payload.spec,
    )
    db.add(pkg)
    db.commit()
    db.refresh(pkg)
    return pkg


@router.get("/", response_model=List[PackageOut])
def list_packages(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    return db.query(Package).all()


@router.get("/{name}/{version}", response_model=PackageOut)
def get_package(
        name: str,
        version: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    pkg = db.query(Package).get((name, version))
    if not pkg:
        raise HTTPException(404, "Package not found")
    return pkg


@router.delete("/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package(
        name: str,
        version: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    pkg = db.query(Package).get((name, version))
    if not pkg:
        raise HTTPException(404, "Package not found")
    db.delete(pkg)
    db.commit()
