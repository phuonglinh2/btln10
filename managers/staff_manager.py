#file staff_manager.py
import csv
import re
from models.staff import Staff

CAP_DO_HOP_LE = ["Intern", "Junior", "Senior"]

VAI_TRO_HOP_LE = [
    "Business Analyst", "Developer", "Tester",
    "UI/UX Designer", "Technical Lead",
    "Implementation Consultant", "DevOps Engineer",
    "Quality Assurance"
]

CHUC_DANH_QUAN_LY = ["Team Leader", "Project Manager"]


class StaffManager:
    """
    Quản lý nghiệp vụ Nhân viên
    - Lưu staff.csv
    - Không lưu project_list (suy ra từ task)
    """

    def __init__(self, filename="staffs.csv"):
        self.filename = filename
        self.staff_list = []
        self.load_from_file()
        self.task_manager = None
    def set_task_manager(self, task_manager):
        self.task_manager = task_manager
    # ==================================================
    # FILE
    # ==================================================
    def load_from_file(self):
        self.staff_list = []

        try:
            with open(self.filename, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    staff = Staff(
                        staff_id=row["staff_id"],
                        full_name=row["full_name"],
                        age=int(row["age"]),
                        level=row["level"],
                        role=row["role"],
                        management_title=row["management_title"] or None,
                        task_list=row["task_list"].split(";") if row["task_list"] else []
                    )
                    self.staff_list.append(staff)
        except FileNotFoundError:
            pass

    def save_to_file(self):
        with open(self.filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "staff_id",
                    "full_name",
                    "age",
                    "level",
                    "role",
                    "management_title",
                    "task_list",
                ]
            )
            writer.writeheader()

            for s in self.staff_list:
                writer.writerow({
                    "staff_id": s.staff_id,
                    "full_name": s.full_name,
                    "age": s.age,
                    "level": s.level,
                    "role": s.role,
                    "management_title": s.management_title or "",
                    "task_list": ";".join(s.task_list),
                })

    # ==================================================
    # CRUD
    # ==================================================
    def add_staff(self):
        staff = Staff()
        staff.input_info(self.staff_list)
        self.staff_list.append(staff)
        self.save_to_file()
        print("Thêm nhân viên thành công")

    def update_staff(self):
        max_try = 3
        count = 0

        while count < max_try:
            staff_id = input("Nhập mã nhân viên cần cập nhật: ").strip()
            staff = self.find_by_id(staff_id)

            if staff:
                staff.update_info()
                self.save_to_file()
                print("Cập nhật nhân viên thành công")
                return True
            else:
                count += 1
                print(f"Không tìm thấy nhân viên ({count}/{max_try} lần)")

        print("Bạn đã nhập sai mã nhân viên quá 3 lần. Thoát chức năng cập nhật.")
        return False


    def delete_staff(self):
        max_try = 3
        count = 0

        while count < max_try:
            staff_id = input("Nhập mã nhân viên muốn xóa: ").strip()
            staff = next((s for s in self.staff_list if s.staff_id == staff_id), None)

            if not staff:
                count += 1
                print(f"Không tìm thấy nhân viên ({count}/{max_try} lần)")
                continue

            confirm = input(
                f"Bạn chắc chắn muốn xóa nhân viên {staff_id} vĩnh viễn? (y/n): "
            ).lower()

            if confirm != 'y':
                print("Đã hủy thao tác xóa.")
                return  
            
            # 1. Xóa nhân viên khỏi danh sách
            self.staff_list.remove(staff)

            # 2. Cập nhật task (nếu có)
            if self.task_manager:
                self.task_manager.unassign_staff(staff_id)
            else:
                print("Cảnh báo: Chưa kết nối TaskManager.")

            # 3. Lưu file
            self.save_to_file()
            print(f"Đã xóa nhân viên {staff_id} thành công.")
            return  

        print("Bạn đã nhập sai mã nhân viên quá 3 lần. Thoát chức năng xóa.")
        return   


    # ==================================================
    # DISPLAY
    # ==================================================
    def display_all(self):
        if not self.staff_list:
            print("Danh sách nhân viên trống")
            return

        print("\n=== DANH SÁCH NHÂN VIÊN ===")
        
        print(f"| {'Mã NV':<10} | {'Họ và tên':<15} | {'Tuổi':<3} | {'Cấp độ':<10} | {'Vai trò':<15} | {'Chức danh QL':<10} | {'Công việc':<25} |")

        for s in self.staff_list:
            s.display_info()
            
    # ==================================================
    # SEARCH 
    # ==================================================
    def search_staff(self):
        while True:
            keyword = input(
                "Nhập mã NV / họ tên / vai trò: "
            ).strip()

            if not keyword:
                print("Không được để trống từ khóa")
                continue

            keyword_lower = keyword.lower()

            # -------- CASE 1: MÃ NHÂN VIÊN --------
            if keyword.upper().startswith("NV_"):
                if not re.fullmatch(r"NV_\d{5}", keyword.upper()):
                    print("Mã nhân viên sai định dạng (VD: NV_00001)")
                    continue

                result = [
                    s for s in self.staff_list
                    if s.staff_id.upper() == keyword.upper()
                ]

            # -------- CASE 2: VAI TRÒ --------
            elif keyword in VAI_TRO_HOP_LE:
                result = [
                    s for s in self.staff_list
                    if s.role == keyword
                ]

            # -------- CASE 3: HỌ TÊN --------
            else:
                if not re.fullmatch(r"[A-Za-zÀ-ỹ\s]+", keyword):
                    print("Từ khóa tìm kiếm không hợp lệ")
                    continue

                result = [
                    s for s in self.staff_list
                    if keyword_lower in s.full_name.lower()
                ]

            if not result:
                print("Không tìm thấy nhân viên phù hợp")
                continue

            # --- HIỂN THỊ KẾT QUẢ ---
            print(f"\nKẾT QUẢ TÌM KIẾM ({len(result)} nhân viên):")
            print(f"| {'Mã NV':<10} | {'Họ và tên':<15} | {'Tuổi':<3} | {'Cấp độ':<10} | {'Vai trò':<15} | {'Chức danh QL':<10} | {'Công việc':<25} |")
            # 2. In từng dòng dữ liệu
            for s in result:
                s.display_info()
            return

    # ==================================================
    # NGHIỆP VỤ LIÊN KẾT
    # ==================================================
    def find_by_id(self, staff_id):
        return next(
            (s for s in self.staff_list if s.staff_id == staff_id),
            None
        )

    def remove_task_from_all_staff(self, task_id):
        """
        Khi task bị xóa hoặc hủy
        → gỡ task khỏi toàn bộ nhân viên
        """
        changed = False

        for s in self.staff_list:
            if task_id in s.task_list:
                s.task_list.remove(task_id)
                changed = True

        if changed:
            self.save_to_file()

    def add_task_to_staff(self, staff_id, task_id):
        """
        Khi giao task cho nhân viên
        """
        staff = self.find_by_id(staff_id)
        if not staff:
            return

        if task_id not in staff.task_list:
            staff.task_list.append(task_id)
            self.save_to_file()
