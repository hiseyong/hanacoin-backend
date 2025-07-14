from fastapi import APIRouter, Depends
from database.connection import get_connection
from auth.session import get_current_user

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)

@router.get("/recommended_deal")
async def get_recommended_deals(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.title, p.price, p.category, p.created_at, u.username AS seller
                FROM products p
                JOIN users u ON p.seller_id = u.id
                WHERE p.is_active = TRUE
                ORDER BY p.created_at DESC
                LIMIT 5
            """)
            products = cursor.fetchall()

        return {"recommended": products}
    finally:
        conn.close()