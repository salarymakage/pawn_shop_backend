from pydantic import BaseModel
from datetime import date
from typing import Optional

class BuyProducts(BaseModel):
    prod_name: str
    order_weight: float
    order_amount: int
    product_sell_price: float
    product_labor_cost: float
    product_buy_price: float
    
class PawnProducts(BaseModel):
    prod_name: str
    pawn_weight: float
    pawn_amount: int
    pawn_unit_price: float
    
class CreateClient(BaseModel):
    cus_name: str
    address: str
    phone_number: str
    
class CreateProduct(BaseModel):
    prod_name: str
    unit_price: Optional[float] = None
    amount: Optional[int] = None
    
class CreateOrder(BaseModel):
    cus_id: Optional[int] = 0
    cus_name: str
    address: str
    phone_number: str
    order_deposit: float
    order_product_detail: list[BuyProducts]
    
class CreatePawn(BaseModel):
    cus_id: Optional[int] = 0
    cus_name: str
    address: str
    phone_number: str
    pawn_deposit: Optional[float] = 0
    pawn_date: Optional[date] = None
    pawn_expire_date: date
    pawn_product_detail: list[PawnProducts]
    
class GetClient(CreateClient):
    cus_id: int