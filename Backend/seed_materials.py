# -*- coding: utf-8 -*-
import asyncio
import sys
from app.database.mysql import SessionLocal
from app.database.mongodb import get_mongodb_db, get_mongo_client
from app.models.subject import Subject
from app.services.embedding_service import save_study_material

# Định nghĩa dữ liệu tài liệu học tập mẫu cho 7 môn học
MATERIALS_DATA = {
    "TOAN": {
        "topic": "Đạo hàm và ứng dụng của Đạo hàm trong khảo sát hàm số",
        "content": """Đạo hàm là một khái niệm cơ bản trong toán giải tích, biểu diễn tốc độ thay đổi của một hàm số tại một điểm cụ thể. 
Định nghĩa toán học của đạo hàm f'(x) của hàm số f(x) tại điểm x0 được cho bởi giới hạn: f'(x0) = lim (Δx -> 0) [f(x0 + Δx) - f(x0)] / Δx.

Các quy tắc đạo hàm cơ bản bao gồm:
1. Đạo hàm của hằng số bằng 0: (c)' = 0.
2. Đạo hàm của hàm lũy thừa: (x^n)' = n * x^(n-1).
3. Đạo hàm của tổng/hiệu: (u ± v)' = u' ± v'.
4. Quy tắc tích: (u * v)' = u' * v + u * v'.
5. Quy tắc thương: (u / v)' = (u' * v - u * v') / v^2.

Ứng dụng lớn nhất của đạo hàm trong chương trình phổ thông là Khảo sát sự biến thiên và Vẽ đồ thị hàm số:
- Xét tính đơn điệu: Nếu f'(x) > 0 với mọi x thuộc khoảng K thì hàm số đồng biến trên K. Nếu f'(x) < 0 thì hàm số nghịch biến trên K.
- Tìm cực trị: Nếu đạo hàm f'(x) đổi dấu từ dương sang âm khi đi qua x0 thì x0 là điểm cực đại. Ngược lại, nếu f'(x) đổi dấu từ âm sang dương thì x0 là điểm cực tiểu.
- Tìm giá trị lớn nhất (GTLN) và nhỏ nhất (GTNN) trên một đoạn [a, b]: Ta tính giá trị của hàm số tại các điểm cực trị thuộc đoạn và tại hai đầu mút a, b, sau đó so sánh các giá trị này."""
    },
    "LY": {
        "topic": "Dao động điều hòa và các đại lượng đặc trưng",
        "content": """Dao động điều hòa là dao động trong đó li độ của vật là một hàm cosin (hoặc sin) của thời gian. 
Phương trình dao động điều hòa tổng quát có dạng: x = A * cos(ωt + φ).

Trong đó, các đại lượng đặc trưng bao gồm:
1. Li độ (x): Vị trí của vật so với gốc tọa độ (vị trí cân bằng), đơn vị thường dùng là cm hoặc m.
2. Biên độ (A): Li độ cực đại của vật, luôn luôn dương (A > 0).
3. Tần số góc (ω): Đại lượng đặc trưng cho tốc độ biến thiên của pha dao động, đơn vị rad/s.
4. Chu kỳ (T): Khoảng thời gian vật thực hiện một dao động toàn phần, T = 2π / ω (đơn vị giây).
5. Tần số (f): Số dao động toàn phần thực hiện được trong 1 giây, f = 1 / T = ω / 2π (đơn vị Hz).
6. Pha dao động (ωt + φ): Đại lượng xác định trạng thái dao động của vật tại thời điểm t.
7. Pha ban đầu (φ): Xác định trạng thái của vật tại thời điểm t = 0.

Vận tốc và Gia tốc trong dao động điều hòa:
- Vận tốc v là đạo hàm bậc nhất của li độ theo thời gian: v = x' = -ω * A * sin(ωt + φ). Vận tốc đạt cực đại v_max = ωA khi vật đi qua vị trí cân bằng theo chiều dương.
- Gia tốc a là đạo hàm bậc nhất của vận tốc (bậc hai của li độ): a = v' = x'' = -ω^2 * A * cos(ωt + φ) = -ω^2 * x. Gia tốc luôn hướng về vị trí cân bằng và ngược dấu với li độ."""
    },
    "HOA": {
        "topic": "Khái niệm về Este và chất béo (Lipid)",
        "content": """Este là hợp chất hữu cơ được hình thành khi thay thế nhóm -OH của axit cacboxylic bằng nhóm -OR' của ancol.
Công thức tổng quát của este đơn chức, mạch hở tạo bởi axit no và ancol no là: C_n H_{2n} O_2 (với n ≥ 2).

Phản ứng Este hóa (Điều chế este):
Este được điều chế bằng cách đun hồi lưu hỗn hợp axit cacboxylic và ancol với xúc tác axit sunfuric đặc (H2SO4):
R-COOH + R'-OH <=> R-COOR' + H2O (Phản ứng thuận nghịch).

Tính chất hóa học của este:
1. Phản ứng thủy phân trong môi trường axit (Phản ứng thuận nghịch):
R-COOR' + H2O <=> R-COOH + R'-OH (Xúc tác H+, đun nóng).
2. Phản ứng thủy phân trong môi trường kiềm (Phản ứng xà phòng hóa - một chiều):
R-COOR' + NaOH -> R-COONa + R'-OH (đun nóng).

Chất béo (Lipit) là trieste của glixerol với các axit béo (axit cacboxylic đơn chức có mạch cacbon dài không phân nhánh). Công thức cấu tạo chung có dạng: (R-COO)3 C3H5.
Các axit béo phổ biến bao gồm:
- Axit panmitic: C15H31COOH (no)
- Axit stearic: C17H35COOH (no)
- Axit oleic: C17H33COOH (không no, 1 liên kết đôi)
- Axit linoleic: C17H31COOH (không no, 2 liên kết đôi)"""
    },
    "ANH": {
        "topic": "Các cấu trúc câu điều kiện (Conditional Sentences Type 1, 2, 3)",
        "content": """Câu điều kiện được dùng để diễn tả một sự việc có thể xảy ra hoặc không xảy ra dựa trên một điều kiện nhất định. Mỗi câu điều kiện gồm hai mệnh đề: Mệnh đề điều kiện (If-clause) và Mệnh đề chính (Main clause).

1. Câu điều kiện loại 1 (Real Conditional):
- Ý nghĩa: Diễn tả điều kiện có thật ở hiện tại hoặc tương lai, có thể xảy ra.
- Cấu trúc: If + S + V(hiện tại đơn), S + will/can/must + V_infinitive.
- Ví dụ: If it rains tomorrow, we will cancel the picnic.

2. Câu điều kiện loại 2 (Unreal Conditional at Present):
- Ý nghĩa: Diễn tả điều kiện không có thật ở hiện tại hoặc trái ngược với thực tế ở hiện tại.
- Cấu trúc: If + S + V_ed/V2 (đối với to be, dùng 'were' cho tất cả các ngôi), S + would/could + V_infinitive.
- Ví dụ: If I had a lot of money, I would buy a sports car.

3. Câu điều kiện loại 3 (Unreal Conditional in the Past):
- Ý nghĩa: Diễn tả điều kiện không có thật trong quá khứ, trái ngược với thực tế đã xảy ra trong quá khứ.
- Cấu trúc: If + S + Had + V_ed/V3, S + would/could + have + V_ed/V3.
- Ví dụ: If she had studied harder, she would have passed the exam last week.

Cấu trúc đảo ngữ của câu điều kiện:
- Loại 1: Should + S + V_infinitive, S + will + V.
- Loại 2: Were + S + to-V (hoặc Were + S + Noun/Adj), S + would + V.
- Loại 3: Had + S + V_ed/V3, S + would have + V_ed/V3."""
    },
    "TIN": {
        "topic": "Cấu trúc dữ liệu danh sách liên kết (Linked List)",
        "content": """Danh sách liên kết (Linked List) là một cấu trúc dữ liệu tuyến tính, trong đó các phần tử (Node) không được lưu trữ tại các vị trí bộ nhớ liền kề nhau mà được kết nối thông qua các con trỏ (Pointer).

Mỗi Node trong danh sách liên kết đơn gồm hai phần:
1. Phần dữ liệu (Data): Lưu trữ thông tin thực tế của phần tử.
2. Phần liên kết (Next): Lưu trữ địa chỉ bộ nhớ của Node tiếp theo trong danh sách. Phần tử cuối cùng của danh sách trỏ đến NULL để đánh dấu điểm kết thúc.

So sánh giữa Danh sách liên kết và Mảng (Array):
- Kích thước: Mảng có kích thước cố định (tĩnh), trong khi Danh sách liên kết có kích thước động, dễ dàng mở rộng khi runtime.
- Chi phí chèn/xóa: Chèn hoặc xóa phần tử trong Danh sách liên kết rất nhanh O(1) nếu đã biết vị trí, không cần dịch chuyển các phần tử khác như mảng O(n).
- Truy cập ngẫu nhiên: Mảng hỗ trợ truy cập ngẫu nhiên O(1) qua index, trong khi Danh sách liên kết phải duyệt tuyến tính O(n) từ đầu danh sách (Head) để tìm kiếm phần tử.

Các thao tác cơ bản trên Danh sách liên kết đơn:
- Duyệt danh sách (Traversal): Bắt đầu từ Head, di chuyển qua từng Node bằng cách gán node = node.next cho đến khi gặp NULL.
- Thêm Node mới: Có ba trường hợp: thêm vào đầu, thêm vào cuối, hoặc thêm vào sau một Node bất kỳ.
- Xóa Node: Cần tìm Node đứng trước Node cần xóa, đổi con trỏ Next của Node đứng trước sang trỏ tới Node đứng sau Node cần xóa, sau đó giải phóng bộ nhớ của Node bị xóa."""
    },
    "VAN": {
        "topic": "Phân tích giá trị nhân đạo trong tác phẩm Vợ Nhặt của Kim Lân",
        "content": """Tác phẩm "Vợ Nhặt" của nhà văn Kim Lân là một trong những truyện ngắn xuất sắc nhất của văn học hiện thực Việt Nam, tái hiện chân thực bức tranh thảm khốc của nạn đói năm 1945, đồng thời ngợi ca vẻ đẹp nhân bản, khát vọng sống và tình người ấm áp của những người lao động nghèo.

Giá trị nhân đạo sâu sắc của tác phẩm được thể hiện qua các khía cạnh sau:
1. Sự đồng cảm, xót thương sâu sắc với số phận con người: Kim Lân đau đớn trước cảnh người chết đói "như ngả rạ" và thân phận rẻ rúng của con người trong nạn đói. Nhân vật "thị" - người vợ nhặt - không tên, không tuổi, bị cái đói xô đẩy đến mức đánh mất cả lòng tự trọng, chấp nhận theo không anh Tràng chỉ sau bốn bát bánh đúc.
2. Phát hiện và trân trọng khát vọng hạnh phúc của người lao động: Dù đối mặt với cái chết cận kề, anh Tràng vẫn dám cưới vợ, bà cụ Tứ vẫn giang tay đón nhận nàng dâu mới bằng tình thương mẫu tử bao la. Ngọn đèn dầu thắp sáng trong đêm tân hôn chính là biểu tượng cho niềm tin, tình yêu thương vượt qua bóng tối của cái đói, cái chết.
3. Niềm tin bất diệt vào tương lai tươi sáng: Kim Lân không đẩy nhân vật vào bước đường cùng. Kết thúc tác phẩm là hình ảnh lá cờ đỏ sao vàng và đoàn người đi phá kho thóc Nhật trong tâm trí Tràng. Đó là lối thoát, là hướng đi mang tính cách mạng mở ra tương lai cho những người nghèo đói."""
    },
    "SINH": {
        "topic": "Cơ chế di truyền ở cấp độ phân tử: Quá trình phiên mã và dịch mã",
        "content": """Quá trình truyền thông tin di truyền từ DNA đến Protein ở cấp độ phân tử được thực hiện thông qua hai cơ chế chính: Phiên mã và Dịch mã.

1. Quá trình Phiên mã (Transcription):
- Định nghĩa: Là quá trình tổng hợp RNA dựa trên mạch khuôn của DNA. Quá trình này diễn ra trong nhân tế bào ở sinh vật nhân thực hoặc tế bào chất ở sinh vật nhân sơ.
- Cơ chế: Enzym RNA polymerase bám vào vùng khởi động (promoter) của gen, tháo xoắn và tách hai mạch DNA. Enzym chỉ sử dụng mạch khuôn 3'->5' để tổng hợp mạch RNA theo chiều 5'->3' theo nguyên tắc bổ sung (A liên kết với U, T liên kết với A, G liên kết với C, C liên kết với G).
- Kết quả: Tạo ra các phân tử mARN, tARN hoặc rARN. Ở sinh vật nhân thực, mARN sơ khai phải trải qua quá trình cắt bỏ các intron và nối các exon để tạo thành mARN trưởng thành trước khi ra ngoài tế bào chất.

2. Quá trình Dịch mã (Translation):
- Định nghĩa: Là quá trình tổng hợp chuỗi polypeptide (protein) dựa trên thông tin di truyền mã hóa trên mARN. Diễn ra tại ribosome ở tế bào chất.
- Cơ chế: Gồm hai giai đoạn chính là Hoạt hóa axit amin và Tổng hợp chuỗi polypeptide. Axit amin được hoạt hóa liên kết với tARN tương ứng. Ribosome dịch chuyển dọc mARN theo từng bộ ba (codon) từ đầu 5' đến 3'. Các tARN mang axit amin đối mã (anticodon) bổ sung vào khớp với codon trên mARN để hình thành liên kết peptit giữa các axit amin.
- Kết quả: Khi ribosome tiếp xúc với bộ ba kết thúc (UAA, UAG, UGA), quá trình dịch mã kết thúc, chuỗi polypeptide được giải phóng và cắt bỏ axit amin mở đầu (Met ở nhân thực hoặc fMet ở nhân sơ) để tạo thành protein hoàn chỉnh có chức năng sinh học."""
    }
}

async def seed_materials_rag():
    print("Initializing MongoDB connection...")
    db_mongo = get_mongodb_db()
    
    db_mysql = SessionLocal()
    try:
        print("Checking subjects in MySQL database...")
        for code, data in MATERIALS_DATA.items():
            subject = db_mysql.query(Subject).filter(Subject.code == code).first()
            if not subject:
                print(f"⚠️ Subject {code} not found in MySQL. Skipping.")
                continue
            
            print(f"Indexing RAG study material for {subject.name} (ID={subject.id})...")
            # Kiểm tra xem tài liệu môn học này đã tồn tại trong MongoDB chưa
            existing = await db_mongo.study_material_embeddings.find_one({"subject_id": subject.id, "topic": data["topic"]})
            if existing:
                print(f"ℹ️ Material '{data['topic']}' already exists for subject {subject.name}. Skipping.")
                continue
            
            # Lưu tài liệu học tập, tự động tạo vector embedding bằng Gemini API
            doc_id = await save_study_material(
                db_mongo=db_mongo,
                subject_id=subject.id,
                topic=data["topic"],
                content=data["content"]
            )
            print(f"✔ Embedded and saved document ID {doc_id} for subject {subject.name}!")
            
        print("✔ MongoDB Atlas vector documents seeding completed successfully!")
    except Exception as e:
        print(f"❌ Error seeding MongoDB materials: {e}")
    finally:
        db_mysql.close()
        client = get_mongo_client()
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(seed_materials_rag())
