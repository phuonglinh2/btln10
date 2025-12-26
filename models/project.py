# models/project.py
import re
from datetime import datetime
from models.ProjectItem import ProjectItem


class Project(ProjectItem):
    STATUS_LIST = [
        "Chưa khởi động",
        "Đang thực hiện",
        "Tạm dừng",
        "Hoàn thành",
        "Hủy"
    ]

    def __init__(self):
        super().__init__()
        self.project_id = ""
        self.project_name = ""
        self.customer = ""
        self.expected_end_date = None
        self.actual_end_date = None
        self.budget = 0.0
        self.status_project = ""
        self.member_list = []  # KHÔNG LƯU CSV
        self.task_list = []    # KHÔNG LƯU CSV
        self.pm_id = ""        # Mã Project Manager

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
            "pm_id",  # thêm trường PM
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
            "pm_id": self.pm_id,
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
        p.pm_id = data.get("pm_id", "")
        return p

    # ================= INPUT =================
    def input_info(self, existing_project_ids=None, staff_manager=None):
        if existing_project_ids is None:
            existing_project_ids = []

        # PROJECT ID
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

        # NAME
        while True:
            name = input("Nhập tên dự án: ").strip()
            if len(name) < 2:
                print("Tên tối thiểu 2 ký tự")
                continue
            self.project_name = name.title()
            self.name = self.project_name
            break

        # CUSTOMER
        while True:
            customer = input("Nhập khách hàng: ").strip()
            if not customer:
                print("Không được để trống")
                continue
            self.customer = customer.title()
            break

        # DESCRIPTION
        self.description = input("Nhập mô tả dự án: ").strip()

        # START DATE
        self.input_start_date()

        # EXPECTED END DATE
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

        # ACTUAL END DATE
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

        # BUDGET
        while True:
            try:
                self.budget = float(input("Ngân sách dự kiến: "))
                if self.budget <= 0:
                    print("Ngân sách phải > 0")
                    continue
                break
            except ValueError:
                print("Phải là số")

        # STATUS
        while True:
            print("Chọn trạng thái:")
            for i, st in enumerate(self.STATUS_LIST, 1):
                print(f"{i}. {st}")

            try:
                choice = int(input("Chọn: "))
                if choice < 1 or choice > len(self.STATUS_LIST):
                    raise ValueError

                status = self.STATUS_LIST[choice - 1]
                today = datetime.now()

                if status == "Hoàn thành":
                    # Chưa tới hạn dự kiến
                    if self.expected_end_date and today < self.expected_end_date:
                        print("Dự án chưa tới ngày hoàn thành dự kiến → không thể chọn 'Hoàn thành'")
                        continue

                    # Có ngày thực tế nhưng sai logic
                    if self.actual_end_date and self.actual_end_date > today:
                        print("Ngày hoàn thành thực tế không hợp lệ")
                        continue

                self.status_project = status
                break

            except ValueError:
                print("Lựa chọn không hợp lệ")


        # PM (bắt buộc)
        if staff_manager:
            while True:
                pm_id = input("Nhập mã PM của dự án: ").strip()
                if not pm_id:
                    print("Phải nhập PM hoặc gõ 'exit' để hủy")
                    continue
                if pm_id.lower() == "exit":
                    print("Hủy nhập dự án.")
                    return False
                staff = staff_manager.find_by_id(pm_id)
                if not staff:
                    print("Nhân viên không tồn tại.")
                    continue
                if getattr(staff, "management_title", "") != "Project Manager":
                    print("Người nhập phải là Project Manager")
                    continue
                self.pm_id = pm_id
                break

        return True
