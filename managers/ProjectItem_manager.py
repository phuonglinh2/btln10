import csv
from datetime import datetime


class ProjectItemManager:
    def __init__(self, filename, cls, fieldnames, id_field="id"):
        self.filename = filename
        self.cls = cls
        self.fieldnames = fieldnames
        self.id_field = id_field
        self.items = []
        self.load_from_file()

    # ================= FILE =================
    def load_from_file(self):
        self.items = []
        try:
            with open(self.filename, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    obj = self.cls.from_dict(row)
                    self.items.append(obj)
        except FileNotFoundError:
            pass

    def save_to_file(self):
        with open(self.filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for obj in self.items:
                writer.writerow(obj.to_dict())  # <- sửa ở đây


    # ================= CRUD =================
    # Thêm item
    def add_item(self, obj):
        if any(getattr(x, self.id_field) == getattr(obj, self.id_field) for x in self.items):
            print("ID đã tồn tại")
            return False
        self.items.append(obj)
        self.save_to_file()
        print("Thêm thành công")
        return True
    # Sửa item
    def update_item(self, item_id):
        for obj in self.items:
            if getattr(obj, self.id_field) == item_id:
                print("Nhập thông tin mới (Enter để giữ nguyên):")

                for field in self.fieldnames:
                    if field == self.id_field:
                        continue
                    old_val = getattr(obj, field)
                    new_val = input(f"{field} ({old_val}): ").strip()
                    if not new_val:
                        continue
                    # format ngày nếu là datetime
                    if isinstance(old_val, datetime):
                        try:
                            new_val = datetime.strptime(new_val, "%d/%m/%Y")
                        except ValueError:
                            print(f"Sai định dạng ngày ở {field}")
                            continue

                    setattr(obj, field, new_val)

                self.save_to_file()
                print("Cập nhật thành công")
                return True
        print("Không tìm thấy")
        return False
    # Xóa item
    def delete_item(self, item_id):
        for obj in self.items:
            if getattr(obj, self.id_field) == item_id:
                self.items.remove(obj)
                self.save_to_file()
                print("Đã xóa")
                return True
        print("Không tìm thấy")
        return False
    # Tìm kiếm item
    def search_item(self, keyword):
        keyword = keyword.lower()
        return [
            obj for obj in self.items
            if any(keyword in str(v).lower() for v in obj.to_dict().values())
        ]

    # Hiển thị tất cả item
    def display_all(self):
        if not self.items:
            print("Danh sách trống")
            return

        print(" | ".join(f"{f.upper():<18}" for f in self.fieldnames))
        print("-" * 100)

        for obj in self.items:
            row = []
            for f in self.fieldnames:
                val = getattr(obj, f)
                if isinstance(val, datetime):
                    val = val.strftime("%d/%m/%Y")
                row.append(f"{str(val):<18}")
            print(" | ".join(row))
