from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from response_model import ResponseModel
from routes.oauth2.repository import get_current_user
from routes.user.repository import Staff
from routes.user.model import *

router = APIRouter(
    tags=["Staff"],
    prefix="/staff"
)

staff = Staff()

""" Manage Client """
@router.post("/client", response_model=ResponseModel)
def create_client(client_info: CreateClient, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.create_client(client_info, db)

@router.get("/client", response_model=ResponseModel[List[GetClient]])
def get_all_client(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.get_client(db)

""" Manage Product """
@router.post("/product", response_model = ResponseModel)
def create_product(product_info: CreateProduct, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.create_product(product_info, db, current_user)

@router.get("/product", response_model=ResponseModel)
def get_all_product(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.get_product(db=db)

""" Order and Payment """
@router.post("/order", response_model = ResponseModel)
def create_order(order_info: CreateOrder, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.create_order(order_info, db, current_user)

@router.get("/order", response_model=ResponseModel)
def get_client_order(cus_id: Optional[int] = None, cus_name: Optional[str] = None, phone_number: Optional[str] = None, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.get_client_order(db, cus_id, cus_name, phone_number)

""" Manage Pawn and Payment """ 
@router.post("/pawn", response_model = ResponseModel)
def create_pawn(pawn_info: CreatePawn, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.create_pawn(pawn_info, db, current_user)

@router.get("/pawn", response_model=ResponseModel)
def get_pawn_by_id(cus_id: Optional[int] = None, cus_name: Optional[str] = None, phone_number: Optional[str] = None, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    return staff.get_client_pawn(db, cus_id, cus_name, phone_number)

"""Delete product by ID"""
@router.delete("/products/{product_id}")
def delete_product_by_id(
    product_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    staff.is_staff(current_user)
    return staff.delete_product_by_id(product_id, db)

"""Delete product by name"""
@router.delete("/products/name/{product_name}")
def delete_product_by_name(
    product_name: str, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    staff.is_staff(current_user)
    return staff.delete_product_by_name(product_name, db)

"""Delete all products"""
@router.delete("/products")
def delete_all_products(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    staff.is_staff(current_user)
    return staff.delete_all_products(db)

@router.get("/products/search/{search_input}", response_model=ResponseModel)
def search_product(
    search_input: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    staff.is_staff(current_user)
    try:
        if search_input.isdigit():
            product = staff.get_product_by_id(int(search_input), db)
            return ResponseModel(
                code=200,
                status="success",
                message="Product retrieved successfully",
                result=product,
            )
        else:
            products = staff.get_product_by_name(search_input, db)
            return ResponseModel(
                code=200,
                status="success",
                message="Products retrieved successfully",
                result=products,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
