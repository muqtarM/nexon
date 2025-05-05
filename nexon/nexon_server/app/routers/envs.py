from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import SessionLocal
from app.models.environment import Environment
from app.schemas.environment import (
    EnvironmentOut, EnvironmentCreate, EnvironmentUpdate
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/envs", tags=["environments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=EnvironmentOut, status_code=status.HTTP_201_CREATED)
def create_env(
        payload: EnvironmentCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
):
    # Check uniqueness
    if db.query(Environment).filter_by(name=payload.name).first():
        raise HTTPException(409, f"Environment '{payload.name}' already exists")
    env = Environment(
        name=payload.name,
        role=payload.role,
        packages=payload.packages,
    )
    db.add(env)
    db.commit()
    db.refresh(env)
    return env


@router.get("/", response_model=List[EnvironmentOut])
def list_envs(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user),
):
    return db.query(Environment).all()


@router.get("/{name}", response_model=EnvironmentOut)
def get_env(
        name: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user),
):
    env = db.query(Environment).get(name)
    if not env:
        raise HTTPException(404, f"Environment '{name}' not found")
    return env


@router.patch("/{name}", response_model=EnvironmentOut)
def update_env(
        name: str,
        payload: EnvironmentUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    env = db.query(Environment).get(name)
    if not env:
        raise HTTPException(404, f"Environment '{name}' not found")
    if payload.role is not None:
        env.role = payload.role
    if payload.packages is not None:
        env.packages = payload.packages
    db.commit()
    db.refresh(env)
    return env


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_env(
        name: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    env = db.query(Environment).get(name)
    if not env:
        raise HTTPException(404, f"Environment '{name}' not found")
    db.delete(env)
    db.commit()
