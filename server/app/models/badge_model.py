from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Text,
)

from app.database.database import Base


class Badge(Base):
    """
    Model đại diện cho bảng badges trong database

    Attributes:
        id (int): ID của huy hiệu, là primary key
        name (str): Tên của huy hiệu
        icon (str): Biểu tượng hoặc mã emoji đại diện cho huy hiệu
        image_url (str): Đường dẫn đến hình ảnh huy hiệu (nếu có)
        description (text): Mô tả chi tiết về huy hiệu
        category (str): Danh mục của huy hiệu (Thành tựu, Kỹ năng, Tiến độ...)
        criteria (text): Tiêu chí để đạt được huy hiệu
        points (int): Số điểm thưởng khi đạt được huy hiệu
        rarity (str): Độ hiếm của huy hiệu (Phổ biến, Hiếm, Cực hiếm...)
        is_hidden (bool): Huy hiệu có ẩn khỏi người dùng cho đến khi đạt được không
        is_active (bool): Huy hiệu có đang hoạt động không
        created_at (DateTime): Thời điểm tạo huy hiệu
        updated_at (DateTime): Thời điểm cập nhật gần nhất
    """

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="Achievement")
    criteria = Column(Text, nullable=True)
    points = Column(Integer, default=0)
    rarity = Column(String(50), default="Common")
    is_hidden = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
