from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.group_schema import GroupCreate, GroupRead
from app.service.group_service import GroupService
from app.configuration.database import get_db

group_service = GroupService()
router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupCreate, db: AsyncSession = Depends(get_db)):
    return await group_service.create_new_group(db, group)

@router.get("/", response_model=list[GroupRead])
async def get_groups(db: AsyncSession = Depends(get_db)):
    return await group_service.fetch_all_groups(db)

@router.get("/{group_id}", response_model=GroupRead)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    group = await group_service.fetch_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group
