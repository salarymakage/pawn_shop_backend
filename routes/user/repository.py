from fastapi import HTTPException
from routes.user.model import *
from sqlalchemy.orm import Session
from entities import *
from response_model import ResponseModel
from typing import List, Dict
# from app.models import Client, Pawn
from sqlalchemy.sql import func, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict

class Staff:
    def is_staff(self, current_user: dict):
        if current_user['role'] != 'admin':
            raise HTTPException(
                status_code=403,
                detail="Permission denied",
            )
            
    def create_client(self, client_info: CreateClient, db: Session, not_exist: bool = False):
        existing_client = db.query(Account).filter(Account.phone_number == client_info.phone_number).first()
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="Phone Number already registered",
            )
        
        if not_exist:
            try:
                client = Account(
                    cus_name = client_info.cus_name, 
                    address = client_info.address,
                    phone_number = client_info.phone_number,)
                db.add(client)
                db.commit()
                db.refresh(client)
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error occurred: {str(e)}")
                raise HTTPException(status_code=500, detail="Database error occurred.")
            
            return client
            
        client = Account(
            cus_name = client_info.cus_name, 
            address = client_info.address,
            phone_number = client_info.phone_number,)
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        return ResponseModel(
            code=200,
            status="Success",
            message="Client created successfully"
        )
        
    def create_product(self, product_info: CreateProduct, db: Session, current_user: dict):
        existing_product = db.query(Product).filter(Product.prod_name == func.lower(product_info.prod_name)).first()
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="Product already exists",
            )
            
        if product_info.amount != None and product_info.unit_price != None:
            product = Product(
                prod_name = func.lower(product_info.prod_name),
                unit_price = product_info.unit_price,
                amount = product_info.amount,
                user_id = current_user['id'])
            db.add(product)
            db.commit()
            db.refresh(product)
            
        else: 
            product = Product(prod_name = func.lower(product_info.prod_name), user_id = current_user['id'])
            db.add(product)
            db.commit()
            db.refresh(product)
            return product
        
        
        return ResponseModel(
            code=200,
            status="Success",
            message="Product created successfully"
        )
        
    def create_order(self, order_info: CreateOrder, db: Session, current_user: dict):
        existing_customer = db.query(Account).filter(
            and_(
                or_(
                    Account.phone_number == order_info.phone_number, 
                    func.lower(Account.cus_name) == func.lower(order_info.cus_name),
                    Account.cus_id == order_info.cus_id
                ), 
                Account.role == 'user'
            )
        ).first()
        if not existing_customer:
            existing_customer = self.create_client(CreateClient(cus_name=order_info.cus_name, phone_number=order_info.phone_number, address=order_info.address), db, True)
        
        order = Order(
            cus_id = existing_customer.cus_id,
            order_deposit = order_info.order_deposit)
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        for product in order_info.order_product_detail:
            existing_product = db.query(Product).filter(Product.prod_name == func.lower(product.prod_name)).first()
            if not existing_product:
                prod = self.create_product(CreateProduct(prod_name=product.prod_name), db, current_user)
                order_detail = OrderDetail(
                    order_id = order.order_id,
                    prod_id = prod.prod_id,
                    order_weight = product.order_weight,
                    order_amount = product.order_amount,
                    product_sell_price = product.product_sell_price,
                    product_labor_cost = product.product_labor_cost,
                    product_buy_price = product.product_buy_price)
                
            else: 
                order_detail = OrderDetail(
                    order_id = order.order_id,
                    prod_id = existing_product.prod_id,
                    order_weight = product.order_weight,
                    order_amount = product.order_amount,
                    product_sell_price = product.product_sell_price,
                    product_labor_cost = product.product_labor_cost,
                    product_buy_price = product.product_buy_price)
            
            db.add(order_detail)
            db.commit()
            db.refresh(order_detail)
        
        return ResponseModel(
            code=200,
            status="Success",
            message="Order created successfully"
        )
        
    def create_pawn(self, pawn_info: CreatePawn, db: Session, current_user: dict):
        if pawn_info.pawn_date > pawn_info.pawn_expire_date:
            raise HTTPException(
                status_code=400,
                detail="Pawn date must be before expire date",
            )
            
        existing_customer = db.query(Account).filter(
            and_(
                or_(
                    Account.phone_number == pawn_info.phone_number, 
                    func.lower(Account.cus_name) == func.lower(pawn_info.cus_name),
                    Account.cus_id == pawn_info.cus_id
                ), 
                Account.role == 'user'
            )
        ).first()
        if not existing_customer:
            existing_customer = self.create_client(CreateClient(cus_name=pawn_info.cus_name, phone_number=pawn_info.phone_number, address=pawn_info.address), db, True)
        
        if pawn_info.pawn_date is None:
            pawn_info.pawn_date = datetime.utcnow()
            
        pawn = Pawn(
            cus_id = existing_customer.cus_id,
            pawn_date = pawn_info.pawn_date,
            pawn_deposit = pawn_info.pawn_deposit,
            pawn_expire_date = pawn_info.pawn_expire_date)
        
        db.add(pawn)
        db.commit()
        db.refresh(pawn)
        
        for product in pawn_info.pawn_product_detail:
            existing_product = db.query(Product).filter(Product.prod_name == func.lower(product.prod_name)).first()
            if not existing_product:
                prod = self.create_product(CreateProduct(prod_name=product.prod_name), db, current_user)
                pawn_detail = PawnDetail(
                    pawn_id = pawn.pawn_id,
                    prod_id = prod.prod_id,
                    pawn_weight = product.pawn_weight,
                    pawn_amount = product.pawn_amount,
                    pawn_unit_price = product.pawn_unit_price)
            else: 
                pawn_detail = PawnDetail(
                    pawn_id = pawn.pawn_id,
                    prod_id = existing_product.prod_id,
                    pawn_weight = product.pawn_weight,
                    pawn_amount = product.pawn_amount,
                    pawn_unit_price = product.pawn_unit_price)
                
            
            db.add(pawn_detail)
            db.commit()
            db.refresh(pawn_detail)
        
        return ResponseModel(
            code=200,
            status="Success",
            message="Pawn created successfully"
        )
        
    def get_product(self, db: Session):
        products = db.query(Product).all()
        if not products:
            raise HTTPException(
                status_code=404,
                detail="Products not found",
            )
        serialized_products = [
            {
                "id": product.prod_id,
                "name": product.prod_name,
                "price": product.unit_price,
                "amount": product.amount,
            }
            for product in products
        ]
        return ResponseModel(
            code=200,
            status="Success",
            result=serialized_products
        )
    
    # def get_product(self, db: Session):
    #     products = db.query(Product).all()
    #     if not products:
    #         raise HTTPException(
    #             status_code=404,
    #             detail="Products not found",
    #         )
    #     serialized_products = []
    #     for product in products:
    #         # Default values
    #         unit_price = product.unit_price
    #         amount = product.amount  # Default to product.amount
    #         order_amount = None  # Default in case no OrderDetail exists
            
    #         # Check and fallback for unit_price and amount
    #         if unit_price is None or amount is None:
    #             order_detail = db.query(OrderDetail).filter(
    #                 OrderDetail.prod_id == product.prod_id
    #             ).first()
    #             if order_detail:
    #                 unit_price = unit_price or order_detail.product_buy_price
    #                 amount = amount or order_detail.order_amount  # Fallback for amount
    
    #         serialized_products.append(
    #             {
    #                 "id": product.prod_id,
    #                 "name": product.prod_name,
    #                 "price": unit_price,
    #                 "amount": amount,  # Use the fallback value
    #             }
    #         )
    #     return ResponseModel(
    #         code=200,
    #         status="Success",
    #         result=serialized_products
    #     )


    def get_product(self, db: Session):
        products = db.query(Product).all()
        if not products:
            raise HTTPException(
                status_code=404,
                detail="Products not found",
            )
        serialized_products = [
            {
                "id": product.prod_id,
                "name": product.prod_name,
                "price": product.unit_price,
                "amount": product.amount,
            }
            for product in products
        ]
        return ResponseModel(
            code=200,
            status="Success",
            result=serialized_products
        )


    def get_client(self, db: Session):
        clients = db.query(Account).filter(Account.role == 'user').all()
        return ResponseModel(
            code=200,
            status="Success",
            result=clients
        )
        
    def get_order_detail(
        self,
        db: Session,
        cus_id: Optional[int] = None, 
        cus_name: Optional[str] = None, 
        phone_number: Optional[str] = None,
    ):
        orders = (
            db.query(
                Account.cus_name,
                Account.phone_number,
                Order.order_id,
                Order.order_deposit,
                Product.prod_name,
                Product.prod_id,
                OrderDetail.order_weight,
                OrderDetail.order_amount,
                OrderDetail.product_sell_price,
                OrderDetail.product_labor_cost,
                OrderDetail.product_buy_price,
                Order.order_date,
            )
            .select_from(Account)
            .join(Order, Account.cus_id == Order.cus_id)
            .join(OrderDetail, Order.order_id == OrderDetail.order_id)
            .join(Product, OrderDetail.prod_id == Product.prod_id)
            .filter(
                and_(
                    or_(
                        Account.cus_id == cus_id,
                        Account.phone_number == phone_number,
                        func.lower(Account.cus_name) == func.lower(str(cus_name)),
                    ),
                    Account.role == "user",
                )
            )
            .all()
        )

        grouped_orders = defaultdict(lambda: {
            "order_deposit": 0,
            "order_date": "",
            "products": [],
        })

        for order in orders:
            order_id = order[2]

            if not grouped_orders[order_id]["order_date"]:
                grouped_orders[order_id].update(
                    {
                        "order_deposit": order[3],
                        "order_date": order[11],
                    }
                )

            product = {
                "prod_name": order[4],
                "prod_id": order[5],
                "order_weight": order[6],
                "order_amount": order[7],
                "product_sell_price": order[8],
                "product_labor_cost": order[9],
                "product_buy_price": order[10],
            }

            grouped_orders[order_id]["products"].append(product)

        return list(grouped_orders.values())

    def get_client_order(self, db: Session, cus_id: Optional[int] = None, cus_name: Optional[str] = None, phone_number: Optional[str] = None,):
        client = db.query(Account).filter(
            and_(
                or_(
                    Account.cus_id == cus_id,
                    Account.phone_number == phone_number,
                    func.lower(Account.cus_name) == func.lower(cus_name)
                    ), 
                Account.role == 'user'
                )
            ).first()
        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found",
            )
            
        get_detail_order = self.get_order_detail(db=db, cus_id=cus_id, cus_name=cus_name, phone_number=phone_number)
        
        if len(get_detail_order) <= 0:
            return ResponseModel(
                code=200,
                status="Success",
                message="Orders not found",
                result=get_detail_order
            )
        
        return ResponseModel(
            code=200,
            status="Success",
            result=get_detail_order
        )
        
    def get_pawn_detail(
        self,
        db: Session,
        cus_id: Optional[int] = None,
        phone_number: Optional[str] = None,
        cus_name: Optional[str] = None,
    ):
        pawns = (
            db.query(
                Account.phone_number,
                Account.cus_name,
                Pawn.pawn_id,
                Pawn.pawn_deposit,
                Product.prod_name,
                Product.prod_id,
                PawnDetail.pawn_weight,
                PawnDetail.pawn_amount,
                PawnDetail.pawn_unit_price,
                Pawn.pawn_date,
                Pawn.pawn_expire_date,
            )
            .select_from(Account)
            .join(Pawn, Account.cus_id == Pawn.cus_id)
            .join(PawnDetail, Pawn.pawn_id == PawnDetail.pawn_id)
            .join(Product, PawnDetail.prod_id == Product.prod_id)
            .filter(
                and_(
                    or_(
                        Pawn.cus_id == cus_id,
                        Account.phone_number == phone_number,
                        func.lower(Account.cus_name) == func.lower(str(cus_name)),
                    ),
                    Account.role == "user",
                )
            )
            .all()
        )

        grouped_pawns = defaultdict(lambda: {
            "pawn_deposit": 0,
            "pawn_date": "",
            "pawn_expire_date": "",
            "products": [],
        })

        for pawn in pawns:
            pawn_id = pawn[2]
            if not grouped_pawns[pawn_id]["pawn_date"]:
                grouped_pawns[pawn_id].update(
                    {
                        "pawn_deposit": pawn[3],
                        "pawn_date": pawn[9],
                        "pawn_expire_date": pawn[10],
                    }
                )
            product = {
                "prod_name": pawn[4],
                "prod_id": pawn[5],
                "pawn_weight": pawn[6],
                "pawn_amount": pawn[7],
                "pawn_unit_price": pawn[8],
            }
            product_exists = any(p["prod_id"] == product["prod_id"] for p in grouped_pawns[pawn_id]["products"])

            if not product_exists:
                grouped_pawns[pawn_id]["products"].append(product)

        return list(grouped_pawns.values())
        
    def get_client_pawn(self, db: Session, cus_id: Optional[int] = None, cus_name: Optional[str] = None, phone_number: Optional[str] = None):
        client = db.query(Account).filter(
            and_(
                or_(
                    Account.cus_id == cus_id,
                    Account.phone_number == phone_number,
                    func.lower(Account.cus_name) == func.lower(cus_name)
                    ), 
                Account.role == 'user'
                )
            ).first()
        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found",
            )
            
        get_detail_pawn = self.get_pawn_detail(db=db, cus_id=client.cus_id)
        if len(get_detail_pawn) <= 0:
            return ResponseModel(
                code=200,
                status="Success",
                message="Pawns not found",
                result=get_detail_pawn
            )
        
        return ResponseModel(
            code=200,
            status="Success",
            result=get_detail_pawn
        )
        
    def delete_product_by_id(self, product_id: int, db: Session):
        """
        Deletes a product by its ID.
        """
        product = db.query(Product).filter(Product.prod_id == product_id).first()
        if not product:
            # Instead of raising an exception, return a success message
            return ResponseModel(
                code=200,
                status="Success",
                message=f"Product with ID {product_id} not found but considered deleted"
            )

        try:
            db.delete(product)
            db.commit()
            return ResponseModel(
                code=200,
                status="Success",
                message=f"Product with ID {product_id} deleted successfully"
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error occurred: {str(e)}",
            )


    def delete_product_by_name(self, product_name: str, db: Session):
        """
        Deletes a product by its name.
        """
        product = db.query(Product).filter(func.lower(Product.prod_name) == func.lower(product_name)).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with name '{product_name}' not found",
            )
        
        try:
            db.delete(product)
            db.commit()
            return ResponseModel(
                code=200,
                status="Success",
                message=f"Product with name '{product_name}' deleted successfully"
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error occurred: {str(e)}",
            )

    def delete_all_products(self, db: Session):
        """
        Deletes all products from the database.
        """
        try:
            num_deleted = db.query(Product).delete()
            db.commit()
            return ResponseModel(
                code=200,
                status="Success",
                message=f"All products deleted successfully. Total deleted: {num_deleted}",
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error occurred: {str(e)}",
            )
            
    def get_product_by_id(self, product_id: int, db: Session) -> Dict:
        """
        Fetch a product by its ID and return it in a serialized format.
        """
        product = db.query(Product).filter(Product.prod_id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found"
            )
        # Serialize the product
        return {
            "id": product.prod_id,  # Changed key name to match the format in `get_product`
            "name": product.prod_name,
            "price": product.unit_price,
            "amount": product.amount,
        }
        
    def get_product_by_name(self, product_name: str, db: Session) -> List[Dict]:
        """
        Fetch products by their name and return them in a serialized format.
        """
        products = db.query(Product).filter(Product.prod_name.ilike(f"%{product_name}%")).all()
        if not products:
            raise HTTPException(
                status_code=404,
                detail=f"No products found with name '{product_name}'"
            )
        # Serialize the products
        return [
            {
                "id": product.prod_id,  # Changed key name to match the format in `get_product`
                "name": product.prod_name,
                "price": product.unit_price,
                "amount": product.amount,
            }
            for product in products
        ]
 
    def get_last_product_id(self, db: Session):
        try:
            # Get the last product by `prod_id`
            last_product = db.query(Product).order_by(Product.prod_id.desc()).first()
            if not last_product:
                raise HTTPException(
                    status_code=404,
                    detail="No products found in the database."
                )
            next_prodict_id = last_product.prod_id + 1
            return {"last_product_id": next_prodict_id}
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error occurred: {str(e)}"
            )

    def get_last_client_id(self, db: Session):
        # Get the most recent client/user based on their ID
        client = db.query(Account).filter(Account.role == "user").order_by(Account.cus_id.desc()).first()
        if not client:
            raise HTTPException(
                status_code=404,
                detail="No clients found in the database."
            )
        next_client_id = client.cus_id + 1
    
        return ResponseModel(
            code=200,
            status="Success",
            result={
                "id": next_client_id,
                # "name": client.cus_name,
                # "phone_number": client.phone_number,
                # "address": client.address,
            }
        )  
        
    def get_last_order_id(self, db: Session):
        last_order_id = (
            db.query(Order.order_id)
            .order_by(Order.order_id.desc())  # Get latest order ID
            .limit(1)
            .scalar()
        )
        return {"last_order_id": last_order_id} if last_order_id else {"message": "No orders found"} 

    def update_product(self, product_info: UpdateProduct, db: Session):
        """
        Updates only `unit_price` and `amount` of a product.
        The product is identified using either `product_id` or `product_name`.
        """
        product_id = product_info.product_id
        product_name = product_info.product_name
    
        if product_id is None and not product_name:
            raise HTTPException(status_code=400, detail="Provide either a product ID or product name for update.")
    
        # Fetch the product using ID or name
        query = db.query(Product)
        
        if product_id:
            product = query.filter(Product.prod_id == product_id).first()
        else:
            product = query.filter(func.lower(Product.prod_name) == func.lower(product_name)).first()
    
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
    
        try:
            # Update only provided fields
            updated_fields = []
            if product_info.unit_price is not None:
                product.unit_price = product_info.unit_price
                updated_fields.append("unit_price")
            
            if product_info.amount is not None:
                product.amount = product_info.amount
                updated_fields.append("amount")
    
            if not updated_fields:
                raise HTTPException(status_code=400, detail="No valid fields provided for update.")
    
            db.commit()
            db.refresh(product)
    
            return ResponseModel(
                code=200,
                status="Success",
                message=f"Product updated successfully ({', '.join(updated_fields)} updated)."
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}")

    def get_all_pawns(self, db: Session, cus_id: int = None, cus_name: str = None, phone_number: str = None):
        """
        Retrieve all pawn transactions with customer and product details.
        If search parameters (cus_id, cus_name, phone_number) are provided, filter the records.
        Otherwise, return all records.
        """
        query = (
            db.query(
                Account.cus_id,
                Account.cus_name,
                Account.phone_number,
                Account.address,
                Pawn.pawn_id,
                Pawn.pawn_deposit,
                Pawn.pawn_date,
                Pawn.pawn_expire_date,
                Product.prod_id,
                Product.prod_name,
                PawnDetail.pawn_weight,
                PawnDetail.pawn_amount,
                PawnDetail.pawn_unit_price,
            )
            .join(Pawn, Account.cus_id == Pawn.cus_id)
            .join(PawnDetail, Pawn.pawn_id == PawnDetail.pawn_id)
            .join(Product, PawnDetail.prod_id == Product.prod_id)
        )

        # ✅ Apply filters if search parameters are provided
        if cus_id or cus_name or phone_number:
            query = query.filter(
                and_(
                    or_(
                        (cus_id is not None and Account.cus_id == cus_id),
                        (cus_name is not None and func.lower(Account.cus_name).contains(func.lower(cus_name))),
                        (phone_number is not None and Account.phone_number.contains(phone_number)),
                    ),
                    Account.role == "user"
                )
            )

        query = query.order_by(Pawn.pawn_id.desc())  # Sort by latest pawn records
        pawns = query.all()

        if not pawns:
            return ResponseModel(
                code=200,
                status="Success",
                message="No pawn records found",
                result=[]
            )

        # ✅ Group the results by cus_id
        grouped_pawns = defaultdict(lambda: {
            "cus_id": 0,
            "customer_name": "",
            "phone_number": "",
            "address": "",
            "pawn_deposit": 0,
            "pawn_date": "",
            "pawn_expire_date": "",
            "products": [],
        })

        for pawn in pawns:
            cus_id = pawn[0]  # Extract cus_id

            # Populate customer details only once
            if not grouped_pawns[cus_id]["customer_name"]:
                grouped_pawns[cus_id].update({
                    "cus_id": pawn[0],
                    "customer_name": pawn[1],
                    "phone_number": pawn[2],
                    "address": pawn[3],
                    "pawn_deposit": pawn[5],
                    "pawn_date": pawn[6],
                    "pawn_expire_date": pawn[7],
                })

            # Add product details
            product = {
                "prod_id": pawn[8],
                "prod_name": pawn[9],
                "pawn_weight": pawn[10],
                "pawn_amount": pawn[12],
                "pawn_unit_price": pawn[11],
            }

            grouped_pawns[cus_id]["products"].append(product)

        return ResponseModel(
            code=200,
            status="Success",
            result=list(grouped_pawns.values())
        )
        
    def get_next_pawn_id(self, db: Session):
        """
        Retrieve the last pawn ID and return the next available ID.
        """
        last_pawn = db.query(Pawn.pawn_id).order_by(Pawn.pawn_id.desc()).first()
        
        if not last_pawn:
            return ResponseModel(
                code=200,
                status="Success",
                result={"next_pawn_id": 1}  # If no records exist, start from 1
            )
    
        next_pawn_id = last_pawn.pawn_id + 1
    
        return ResponseModel(
            code=200,
            status="Success",
            result={"next_pawn_id": next_pawn_id}
        )
