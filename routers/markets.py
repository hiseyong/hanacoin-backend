from fastapi import APIRouter, Depends, Query, HTTPException
from database.connection import get_connection
from auth.session import get_current_user
from models.market import ProductCreateRequest, ProductResponse, ProductCommentCreate, ProductCommentResponse
from typing import List, Optional

router = APIRouter(
    prefix="/markets",
    tags=["Markets"]
)


# 상품 등록
@router.post("/products", response_model=dict)
async def create_product(
    data: ProductCreateRequest,
    user: dict = Depends(get_current_user)  # dict 형태 전체 사용자 정보
):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO products (seller_id, title, description, price, category)
                VALUES (%s, %s, %s, %s, %s)
            """, (user['id'], data.title, data.description, data.price, data.category))
            conn.commit()
        return {"msg": "Product created successfully"}
    finally:
        conn.close()

# 상품 전체 조회
@router.get("/products", response_model=List[ProductResponse])
async def list_products(category: Optional[str] = Query(None, description="카테고리 필터")):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if category:
                cursor.execute("""
                    SELECT p.id, p.title, p.description, p.price, p.category, p.created_at, u.username AS seller
                    FROM products p
                    JOIN users u ON p.seller_id = u.id
                    WHERE p.is_active = TRUE AND p.category = %s
                    ORDER BY p.created_at DESC
                """, (category,))
            else:
                cursor.execute("""
                    SELECT p.id, p.title, p.description, p.price, p.category, p.created_at, u.username AS seller
                    FROM products p
                    JOIN users u ON p.seller_id = u.id
                    WHERE p.is_active = TRUE
                    ORDER BY p.created_at DESC
                """)
            return cursor.fetchall()
    finally:
        conn.close()


# 단일 상품 조회
@router.get("/product/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.title, p.description, p.price, p.category, p.created_at, u.username AS seller
                FROM products p
                JOIN users u ON p.seller_id = u.id
                WHERE p.id = %s AND p.is_active = TRUE
            """, (product_id,))
            product = cursor.fetchone()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return product
    finally:
        conn.close()

@router.post("/comments", response_model=dict)
async def add_comment(data: ProductCommentCreate, user=Depends(get_current_user)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 상품 존재 확인
            cursor.execute("SELECT id FROM products WHERE id = %s AND is_active = TRUE", (data.product_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Product not found")

            # 댓글 삽입
            cursor.execute("""
                INSERT INTO product_comments (product_id, user_id, content)
                VALUES (%s, %s, %s)
            """, (data.product_id, user["id"], data.content))
            conn.commit()
            return {"msg": "Comment added"}
    finally:
        conn.close()


# 댓글 조회
@router.get("/comments/{product_id}", response_model=list[ProductCommentResponse])
async def get_comments(product_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT pc.id, pc.product_id, u.username, pc.content, pc.created_at
                FROM product_comments pc
                JOIN users u ON pc.user_id = u.id
                WHERE pc.product_id = %s
                ORDER BY pc.created_at DESC
            """, (product_id,))
            return cursor.fetchall()
    finally:
        conn.close()