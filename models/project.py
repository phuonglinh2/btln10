# File project.py
import re
from datetime import datetime
from models.ProjectItem import ProjectItem
from managers.staff_manager import StaffManager


class Project(ProjectItem):
    STATUS_LIST = [
        "Chưa khởi động",
        "Đang thực hiện",
        "Tạm dừng",
        "Hoàn thành",
        "Hủy"
    ]

    def __init__(self):
        super().__init__()  # id, name, description, start_date

        # ===== PROJECT-SPECIFIC =====
        self.project_id = ""          
        self.project_name = ""        
        self.customer = ""
        self.expected_end_date = None
        self.actual_end_date = None
        self.budget = 0.0
        self.status_project = ""

        # ===== Thêm PM ID =====
        self.pm_id = None  # ID của Project Manager thuộc dự án này

        # dữ liệu dẫn xuất – KHÔNG LƯU CSV
        self.member_list = []
        self.task_list = []

    # ================= CSV =================
    @staticmethod
    def csv_fields():
        return [
            "project_id",
            "project_name",
            "customer",
            "description",
            "start_date",
            "expected_end_date",
            "actual_end_date",
            "budget",
            "status_project",
            "pm_id",  # thêm
        ]

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "customer": self.customer,
            "description": self.description,
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else "",
            "expected_end_date": self.expected_end_date.strftime("%Y-%m-%d") if self.expected_end_date else "",
            "actual_end_date": self.actual_end_date.strftime("%Y-%m-%d") if self.actual_end_date else "",
            "budget": self.budget,
            "status_project": self.status_project,
            "pm_id": self.pm_id,  # thêm
        }

    @classmethod
    def from_dict(cls, data: dict):
        p = cls()
        p.project_id = data.get("project_id", "")
        p.id = p.project_id
        p.project_name = data.get("project_name", "")
        p.name = p.project_name
        p.customer = data.get("customer", "")
        p.description = data.get("description", "")
        p.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d") if data.get("start_date") else None
        p.expected_end_date = datetime.strptime(data["expected_end_date"], "%Y-%m-%d") if data.get("expected_end_date") else None
        p.actual_end_date = datetime.strptime(data["actual_end_date"], "%Y-%m-%d") if data.get("actual_end_date") else None
        p.budget = float(data.get("budget", 0))
        p.status_project = data.get("status_project", "")
        p.pm_id = data.get("pm_id", None)  # thêm
        return p

    # ================= INPUT =================
    def input_info(self, existing_project_ids=None, staff_manager=None):
        if existing_project_ids is None:
            existing_project_ids = []

        # ===== PROJECT ID =====
        while True:
            pid = input("Nhập mã dự án (PYY_NNNNN): ").strip()
            if not re.fullmatch(r"P\d{2}_\d{5}", pid):
                print("Sai định dạng (VD: P25_00001)")
                continue
            if pid in existing_project_ids:
                print("Mã dự án đã tồn tại")
                continue
            self.project_id = pid
            self.id = pid
            break

        # ===== NAME =====
        while True:
            name = input("Nhập tên dự án: ").strip()
            if len(name) < 2:
                print("Tên tối thiểu 2 ký tự")
                continue
            self.project_name = name.title()
            self.name = self.project_name
            break

        # ===== CUSTOMER =====
        while True:
            customer = input("Nhập khách hàng: ").strip()
            if not customer:
                print("Không được để trống")
                continue
            self.customer = customer.title()
            break

        # ===== DESCRIPTION =====
        self.description = input("Nhập mô tả dự án: ").strip()

        # ===== START DATE =====
        self.input_start_date()

        # ===== EXPECTED END DATE =====
        while True:
            try:
                d = datetime.strptime(input("Ngày hoàn thành dự kiến (dd/mm/yyyy): "), "%d/%m/%Y")
                if d < self.start_date:
                    print("Ngày dự kiến phải >= ngày bắt đầu")
                    continue
                self.expected_end_date = d
                break
            except ValueError:
                print("Sai định dạng ngày")

        # ===== ACTUAL END DATE =====
        while True:
            s = input("Ngày hoàn thành thực tế (Enter nếu chưa xong): ").strip()
            if not s:
                self.actual_end_date = None
                break
            try:
                d = datetime.strptime(s, "%d/%m/%Y")
                if d < self.start_date:
                    print("Ngày thực tế phải >= ngày bắt đầu")
                    continue
                self.actual_end_date = d
                break
            except ValueError:
                print("Sai định dạng ngày")

        # ===== BUDGET =====
        while True:
            try:
                self.budget = float(input("Ngân sách dự kiến: "))
                if self.budget <= 0:
                    print("Ngân sách phải > 0")
                    continue
                break
            except ValueError:
                print("Phải là số")

        # ===== STATUS =====
        while True:
            print("Chọn trạng thái:")
            for i, st in enumerate(self.STATUS_LIST, 1):
                print(f"{i}. {st}")
            try:
                self.status_project = self.STATUS_LIST[int(input("Chọn: ")) - 1]
                break
            except:
                print("Lựa chọn không hợp lệ")

        # ===== PROJECT MANAGER =====
        while True:
            pm_id = input("Nhập mã PM của dự án: ").strip()
            if not pm_id:
                print("PM không được để trống")
                continue

            if not staff_manager:
                print("StaffManager chưa được truyền vào")
                continue

            staff = staff_manager.find_by_id(pm_id)
            if not staff:
                print("Nhân viên không tồn tại")
                continue
            if staff.management_title != "Project Manager":
                print("Nhân viên này không phải Project Manager")
                continue

            self.pm_id = pm_id
            break


    # ================= DISPLAY =================
    def display_info(self):
        actual = self.actual_end_date.strftime("%d/%m/%Y") if self.actual_end_date else "Chưa hoàn thành"
        print(
            f"{self.project_id:<10} | {self.project_name:<25} | {self.customer:<20} | "
            f"{self.start_date.strftime('%d/%m/%Y'):<12} | "
            f"{self.expected_end_date.strftime('%d/%m/%Y'):<12} | "
            f"{actual:<12} | {self.budget:<12,.0f} | {self.status_project:<15} | PM: {self.pm_id}"
        )
