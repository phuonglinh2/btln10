import re

# ================= CONSTANT =================
CAP_DO_HOP_LE = ["Intern", "Junior", "Senior"]

VAI_TRO_HOP_LE = [
    "Business Analyst", "Developer", "Tester",
    "UI/UX Designer", "Technical Lead",
    "Implementation Consultant", "DevOps Engineer",
    "Quality Assurance"
]

CHUC_DANH_QUAN_LY = ["Team Leader", "Project Manager"]


class Staff:
    """
    Lớp Staff lưu thông tin cá nhân.
    project_list và task_list chỉ dùng để hiển thị / lưu CSV
    """

    def __init__(
        self,
        staff_id="",
        full_name="",
        age=0,
        level="",
        role="",
        management_title=None,
        project_list=None,
        task_list=None
    ):
        self.staff_id = staff_id
        self.full_name = full_name
        self.age = age
        self.level = level
        self.role = role
        self.management_title = management_title

        self.project_list = project_list or []
        self.task_list = task_list or []

    # ================= CSV =================
    @staticmethod
    def csv_fields():
        return [
            "staff_id",
            "full_name",
            "age",
            "level",
            "role",
            "management_title",
            "project_list",
            "task_list",
        ]

    def to_dict(self):
        return {
            "staff_id": self.staff_id,
            "full_name": self.full_name,
            "age": self.age,
            "level": self.level,
            "role": self.role,
            "management_title": self.management_title or "",
            "project_list": "|".join(self.project_list),
            "task_list": "|".join(self.task_list),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            staff_id=data.get("staff_id", ""),
            full_name=data.get("full_name", ""),
            age=int(data.get("age", 0)),
            level=data.get("level", ""),
            role=data.get("role", ""),
            management_title=data.get("management_title") or None,
            project_list=[],
            task_list=[],
        )

    # ================= INPUT =================
    def input_info(self, staff_list):
        """Nhập thông tin nhân viên mới"""
        # ===== STAFF ID =====
        while True:
            try:
                value = input("Nhập mã NV (NV_00001): ").strip()
                self.staff_id = self.validate_staff_id(value, staff_list)
                break
            except ValueError as e:
                print("Lỗi:", e)

        # ===== FULL NAME =====
        while True:
            try:
                value = input("Nhập họ tên: ").strip()
                self.full_name = self.validate_name(value)
                break
            except ValueError as e:
                print("Lỗi:", e)

        # ===== AGE =====
        while True:
            try:
                value = input("Nhập tuổi: ").strip()
                self.age = self.validate_age(value)
                break
            except ValueError as e:
                print("Lỗi:", e)

        # ===== LEVEL =====
        while True:
            print("Cấp độ hợp lệ:", ", ".join(CAP_DO_HOP_LE))
            value = input("Nhập cấp độ: ").strip().title()
            if value in CAP_DO_HOP_LE:
                self.level = value
                break
            print("Cấp độ không hợp lệ. Nhập lại.")

        # ===== ROLE =====
        while True:
            print("Vai trò hợp lệ:", ", ".join(VAI_TRO_HOP_LE))
            value = input("Nhập vai trò: ").strip().title()
            if value in VAI_TRO_HOP_LE:
                self.role = value
                break
            print("Vai trò không hợp lệ. Nhập lại.")

        # ===== MANAGEMENT TITLE =====
        while True:
            print("Chức danh quản lý (Enter nếu không có):")
            print(", ".join(CHUC_DANH_QUAN_LY))
            value = input("Nhập chức danh: ").strip().title()
            if value == "":
                self.management_title = None
                break
            if value in CHUC_DANH_QUAN_LY:
                self.management_title = value
                break
            print("Chức danh quản lý không hợp lệ. Nhập lại hoặc Enter để bỏ qua.")

    # ================= UPDATE =================
    def update_info(self):
        print("\n--- CẬP NHẬT NHÂN VIÊN ---")
        print("(Enter để giữ nguyên giá trị cũ)\n")

        # Họ tên
        name = input(f"Họ tên ({self.full_name}): ").strip()
        if name:
            self.full_name = self.validate_name(name)

        # Tuổi
        age = input(f"Tuổi ({self.age}): ").strip()
        if age:
            self.age = self.validate_age(age)

        # Cấp độ
        while True:
            print(f"Cấp độ hiện tại: {self.level if self.level else 'Chưa có'}")
            new_lv = input("Cấp độ mới (Enter nếu không thay đổi): ").strip().title()
            if new_lv == "":
                break
            if new_lv in CAP_DO_HOP_LE:
                self.level = new_lv
                break
            print("Cấp độ không hợp lệ. Nhập lại.")
            print("Cấp độ hợp lệ:", ", ".join(CAP_DO_HOP_LE))

        # Vai trò
        while True:
            print(f"Vai trò hiện tại: {self.role if self.role else 'Chưa có'}")
            new_role = input("Vai trò mới (Enter nếu không thay đổi): ").strip().title()
            if new_role == "":
                break
            if new_role in VAI_TRO_HOP_LE:
                self.role = new_role
                break
            print("Vai trò không hợp lệ. Nhập lại.")
            print("Vai trò hợp lệ:", ", ".join(VAI_TRO_HOP_LE))

        # Chức danh quản lý
        print(f"Chức danh QL hiện tại: {self.management_title or 'Không có'}")
        while True:
            print("Chức danh hợp lệ:", ", ".join(CHUC_DANH_QUAN_LY))
            mt = input(f"Chức danh QL mới (Enter nếu không thay đổi): ").strip().title()
            if mt == "":
                break
            if mt in CHUC_DANH_QUAN_LY:
                self.management_title = mt
                break
            print("Chức danh quản lý không hợp lệ. Nhập lại hoặc Enter để bỏ qua.")

        print("Đã cập nhật thông tin nhân viên.")

    # ================= VALIDATE =================
    def validate_staff_id(self, ma_nv, staff_list):
        if not re.match(r"^NV_\d{5}$", ma_nv):
            raise ValueError("Mã nhân viên phải theo định dạng NV_00001")
        if any(s.staff_id == ma_nv for s in staff_list):
            raise ValueError("Mã nhân viên đã tồn tại")
        return ma_nv

    def validate_name(self, name):
        if not re.match(r"^[A-Za-zÀ-ỹ\s]+$", name):
            raise ValueError("Tên không hợp lệ")
        return " ".join(w.capitalize() for w in name.split())

    def validate_age(self, age):
        age = int(age)
        if not 18 <= age <= 65:
            raise ValueError("Tuổi không hợp lệ")
        return age

    def validate_choice(self, value, valid_list, field):
        if value not in valid_list:
            raise ValueError(f"{field} không hợp lệ")
        return value

    def validate_management_title(self, value):
        if value == "":
            return None
        if value not in CHUC_DANH_QUAN_LY:
            raise ValueError("Chức danh quản lý không hợp lệ")
        return value

    # ================= DISPLAY =================
    def display_info(self):
        task_str = ", ".join(self.task_list) or "-"
        print(
            f"| {self.staff_id:<10} "
            f"| {self.full_name:<15} "
            f"| {self.age:<3} "
            f"| {self.level:<10} "
            f"| {self.role:<20} "
            f"| {(self.management_title or '-'):<15} "
            f"| {task_str:<25} |"
        )
