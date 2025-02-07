from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
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
staff_service = Staff()

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


@router.get("/last-id")
def get_last_id(db: Session = Depends(get_db)):
    return staff.get_last_product_id(db)

@router.get("/last-client_id")
def get_last_client_id(db: Session = Depends(get_db)):
    return staff.get_last_client_id(db)

@router.get("/last-order-id", response_model=ResponseModel)
def get_last_order_id(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    staff.is_staff(current_user)
    last_order_id = staff.get_last_order_id(db)

    return ResponseModel(
        code=200,
        status="success",
        message="Last order ID retrieved successfully",
        result=last_order_id
    )
    
@router.put("/products")
def update_product(
    product_info: UpdateProduct,  # Accept JSON data in request body
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    staff.is_staff(current_user)
    return staff.update_product(product_info=product_info, db=db)

@router.get("/pawns", response_model=ResponseModel)
def get_all_pawn_records(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # ✅ Requires authentication
    cus_id: int = Query(None, description="Filter by Customer ID"),
    cus_name: str = Query(None, description="Filter by Customer Name"),
    phone_number: str = Query(None, description="Filter by Phone Number")
):
    """
    Retrieve all pawn transactions with optional filters (ID, Name, Phone Number).
    If no filters are provided, return all pawn records.
    Requires authentication (only staff or admin can access).
    """
    # ✅ Authorization Check: Only staff/admin can access
    if current_user["role"] not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied. Only staff can access.")

    return staff.get_all_pawns(db=db, cus_id=cus_id, cus_name=cus_name, phone_number=phone_number)

@router.get("/next-pawn-id", response_model=ResponseModel)
def get_next_pawn_id_api(db: Session = Depends(get_db)):
    """
    API to get the next available Pawn ID.
    """
    return staff.get_next_pawn_id(db=db)
