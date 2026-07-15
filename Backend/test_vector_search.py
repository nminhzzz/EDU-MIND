# -*- coding: utf-8 -*-
import asyncio
from app.database.mysql import SessionLocal
from app.database.mongodb import get_mongodb_db, get_mongo_client
from app.models.subject import Subject
from app.services.embedding_service import vector_search_materials

async def test_search():
    print("Connecting to databases...")
    db_mongo = get_mongodb_db()
    db_mysql = SessionLocal()
    
    try:
        # Lấy môn Toán học (TOAN)
        subject = db_mysql.query(Subject).filter(Subject.code == "TOAN").first()
        if not subject:
            print("❌ Môn Toán học chưa được seed!")
            return
            
        print(f"Testing RAG vector search for subject: {subject.name} (ID={subject.id})")
        print("Query: 'đạo hàm'")
        
        # Thực hiện tìm kiếm vector RAG qua LangChain
        results = await vector_search_materials(
            db_mongo=db_mongo,
            query_text="đạo hàm",
            subject_id=subject.id,
            top_k=2,
            min_score=0.3  # Giảm min_score để đảm bảo ra kết quả kiểm chứng
        )
        
        print(f"Found {len(results)} results:")
        for i, res in enumerate(results):
            print(f"\nResult {i+1} (Score: {res['score']:.4f}):")
            print(f"Topic: {res['topic']}")
            print(f"Content preview: {res['content'][:150]}...")
            
    except Exception as e:
        print(f"❌ Error during vector search test: {e}")
    finally:
        db_mysql.close()
        client = get_mongo_client()
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(test_search())
