from fastapi import APIRouter
from typing import List
from nexon_cli.core.package_manager import PackageManager
from nexon_web.models.pkg_model import PackageSummary

router = APIRouter()


@router.get("/", response_model=List[PackageSummary])
def list_packages():
    pm = PackageManager()
    data = pm.list_packages()   # returns Dict[str, List[str]]
    return [PackageSummary(name=n, versions=v) for n, v in data.items()]
