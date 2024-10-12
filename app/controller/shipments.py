from fastapi import APIRouter, HTTPException
from app.models.shipments import Shipment
from app.schemas.shipments import ShipmentCreate, ShipmentOut

router = APIRouter()

@router.post("/", response_model=ShipmentOut)
async def create_shipment(shipment: ShipmentCreate):
    shipment_obj = await Shipment.create(**shipment.dict())
    return shipment_obj

@router.get("/{shipment_id}", response_model=ShipmentOut)
async def get_shipment(shipment_id: int):
    shipment = await Shipment.get(id=shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment
