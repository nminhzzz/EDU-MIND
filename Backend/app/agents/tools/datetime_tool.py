from datetime import datetime, timezone, timedelta


def get_current_date(offset_hours: int = 7) -> str:
    """
    Trả về ngày hiện tại dưới dạng YYYY-MM-DD dựa trên múi giờ chỉ định (Mặc định UTC+7 cho Việt Nam).
    Sử dụng hoàn toàn thư viện chuẩn của Python.
    """
    tz = timezone(timedelta(hours=offset_hours))
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d")


def get_current_day_of_week(offset_hours: int = 7) -> str:
    """
    Trả về thứ trong tuần hiện tại (Ví dụ: Monday, Tuesday...)
    """
    tz = timezone(timedelta(hours=offset_hours))
    now = datetime.now(tz)
    return now.strftime("%A")
