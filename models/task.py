import re
import csv
from datetime import datetime
from models.ProjectItem import ProjectItem

# ================= Task =================
class Task(ProjectItem):
    PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]
    STATUS_LIST = ["To Do", "In Progress", "Completed", "Cancelled"]

    def __init__(self, project_id="", task_id="", task_name="", description="", 
                 assignee_id="Unassigned", start_date=None, deadline=None, completed_date=None, 
                 priority="Low", status_task="To Do"):
        super().__init__()
        self.id = task_id
        self.name = task_name
        self.description = description
        self.start_date = start_date
        self.project_id = project_id
        self.assignee_id = assignee_id
        self.deadline = deadline
        self.completed_date = completed_date
        self.priority = priority
        self.status_task = status_task

    # ================= CSV =================
    @staticmethod
    def csv_fields():
        return [
            "project_id", "task_id", "task_name", "task_description",
            "assignee_id", "start_date", "deadline", "completed_date",
            "priority", "status_task",
        ]

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "task_id": self.id,
            "task_name": self.name,
            "task_description": self.description,
            "assignee_id": self.assignee_id,
            "start_date": self.start_date.strftime("%d/%m/%Y") if self.start_date else "",
            "deadline": self.deadline.strftime("%d/%m/%Y") if self.deadline else "",
            "completed_date": self.completed_date.strftime("%d/%m/%Y") if self.completed_date else "",
            "priority": self.priority,
            "status_task": self.status_task,
        }

    @classmethod
    def from_dict(cls, data):
        def parse_date(s):
            try:
                return datetime.strptime(s, "%d/%m/%Y") if s else None
            except ValueError:
                return None
        return cls(
            project_id=data.get("project_id", ""),
            task_id=data.get("task_id", ""),
            task_name=data.get("task_name", ""),
            description=data.get("task_description", ""),
            assignee_id=data.get("assignee_id", "Unassigned"),
            start_date=parse_date(data.get("start_date", "")),
            deadline=parse_date(data.get("deadline", "")),
            completed_date=parse_date(data.get("completed_date", "")),
            priority=data.get("priority", "Low"),
            status_task=data.get("status_task", "To Do"),
        )


    # ================= VALIDATION =================
    def _validate_name(self, name):
        if len(name) < 3:
            raise ValueError("Tên công việc phải ≥ 3 ký tự")
        return name.title()

    def _validate_assignee(self, assignee_id, staff_list):
        if not re.fullmatch(r"NV_\d{5}", assignee_id):
            raise ValueError("Sai định dạng NV_00001")
        if assignee_id not in [s.staff_id for s in staff_list]:
            raise ValueError("Nhân viên không tồn tại trong hệ thống")
        return assignee_id

    def _validate_choice(self, value, valid_list, field_name):
        if value not in valid_list:
            raise ValueError(f"{field_name} không hợp lệ")
        return value

    # ================= INPUT =================
    def input_info(self, staff_list, project=None):
        # 1. Tên công việc
        while True:
            try:
                name = input("Tên công việc: ").strip()
                self.name = self._validate_name(name)
                break
            except ValueError as e:
                print("Lỗi:", e)

        # 2. Mô tả
        self.description = input("Mô tả: ").strip()

        # 3. Người phụ trách
        while True:
            aid = input("Mã nhân viên phụ trách (NV_00001): ").strip()
            try:
                self.assignee_id = self._validate_assignee(aid, staff_list)
                break
            except ValueError as e:
                print("Lỗi:", e)

        # 4. Ngày bắt đầu task
        while True:
            try:
                s_str = input("Ngày bắt đầu (dd/mm/yyyy): ").strip()
                s_date = datetime.strptime(s_str, "%d/%m/%Y")
                if project and project.start_date and s_date < project.start_date:
                    print(f"Ngày bắt đầu task phải ≥ ngày bắt đầu dự án ({project.start_date.strftime('%d/%m/%Y')})")
                    continue
                self.start_date = s_date
                break
            except ValueError:
                print("Ngày không hợp lệ. Nhập lại.")

        # 5. Deadline
        while True:
            try:
                dl_str = input("Deadline (dd/mm/yyyy): ").strip()
                dl = datetime.strptime(dl_str, "%d/%m/%Y")
                if dl < self.start_date:
                    print("Deadline phải ≥ ngày bắt đầu task")
                    continue
                if project:
                    max_end = project.expected_end_date
                    if max_end and dl > max_end:
                        print(f"Deadline phải ≤ ngày kết thúc dự án ({max_end.strftime('%d/%m/%Y')})")
                        continue
                self.deadline = dl
                break
            except ValueError:
                print("Ngày không hợp lệ. Nhập lại.")

        # 6. Priority
        while True:
            try:
                p = input(f"Priority ({'/'.join(self.PRIORITY_LEVELS)}): ").strip()
                self.priority = self._validate_choice(p, self.PRIORITY_LEVELS, "Priority")
                break
            except ValueError as e:
                print("Lỗi:", e)

        # 7. Status
        while True:
            try:
                s = input(f"Status ({'/'.join(self.STATUS_LIST)}): ").strip()
                self.status_task = self._validate_choice(s, self.STATUS_LIST, "Status")
                break
            except ValueError as e:
                print("Lỗi:", e)

        # Nếu Completed mà chưa có ngày hoàn thành
        if self.status_task == "Completed" and not self.completed_date:
            self.completed_date = datetime.now()

    # ================= UPDATE =================
    def update_info(self, staff_list, project=None):
        print("\n--- CẬP NHẬT TASK (Enter để bỏ qua) ---")

        # 1. Tên
        while True:
            new_name = input(f"Tên ({self.name}): ").strip()
            if not new_name:
                break
            try:
                self.name = self._validate_name(new_name)
                break
            except ValueError as e:
                print(f"Lỗi: {e}. Nhập lại hoặc Enter để bỏ qua.")

        # 2. Mô tả
        new_desc = input(f"Mô tả ({self.description}): ").strip()
        if new_desc:
            self.description = new_desc

        # 3. Người phụ trách
        while True:
            new_aid = input(f"Nhân viên phụ trách ({self.assignee_id}): ").strip()
            if not new_aid:
                break
            try:
                self.assignee_id = self._validate_assignee(new_aid, staff_list)
                break
            except ValueError as e:
                print(f"Lỗi: {e}. Nhập lại hoặc Enter để bỏ qua.")

        # 4. Ngày bắt đầu
        while True:
            new_s = input(f"Ngày bắt đầu ({self.start_date.strftime('%d/%m/%Y') if self.start_date else ''}): ").strip()
            if not new_s:
                break
            try:
                s_date = datetime.strptime(new_s, "%d/%m/%Y")
                if project and project.start_date and s_date < project.start_date:
                    print(f"Ngày bắt đầu task phải ≥ ngày bắt đầu dự án. Nhập lại hoặc Enter để bỏ qua.")
                else:
                    self.start_date = s_date
                    break
            except ValueError:
                print("Ngày không hợp lệ. Nhập lại hoặc Enter để bỏ qua.")

        # 5. Deadline
        while True:
            new_dl = input(f"Deadline ({self.deadline.strftime('%d/%m/%Y') if self.deadline else ''}): ").strip()
            if not new_dl:
                break
            try:
                dl = datetime.strptime(new_dl, "%d/%m/%Y")
                if dl < self.start_date:
                    print("Deadline phải ≥ ngày bắt đầu task. Nhập lại hoặc Enter để bỏ qua.")
                elif project:
                    max_end = project.actual_end_date or project.expected_end_date
                    if max_end and dl > max_end:
                        print("Deadline phải ≤ ngày kết thúc dự án. Nhập lại hoặc Enter để bỏ qua.")
                    else:
                        self.deadline = dl
                        break
                else:
                    self.deadline = dl
                    break
            except ValueError:
                print("Ngày không hợp lệ. Nhập lại hoặc Enter để bỏ qua.")

        # 6. Priority
        while True:
            new_priority = input(f"Priority ({self.priority}): ").strip()
            if not new_priority:
                break
            try:
                self.priority = self._validate_choice(new_priority, self.PRIORITY_LEVELS, "Priority")
                break
            except ValueError as e:
                print(f"Lỗi: {e}. Nhập lại hoặc Enter để bỏ qua.")

        # 7. Status
        while True:
            new_status = input(f"Status ({self.status_task}): ").strip()
            if not new_status:
                break
            try:
                self.status_task = self._validate_choice(new_status, self.STATUS_LIST, "Status")
                break
            except ValueError as e:
                print(f"Lỗi: {e}. Nhập lại hoặc Enter để bỏ qua.")


        # Ngày hoàn thành tự động
        if self.status_task == "Completed" and not self.completed_date:
            self.completed_date = datetime.now()
        elif self.status_task != "Completed":
            self.completed_date = None

    # ================= DISPLAY =================
    def display_info(self):
        s_date = self.start_date.strftime("%d/%m/%Y") if self.start_date else "--/--/----"
        d_date = self.deadline.strftime("%d/%m/%Y") if self.deadline else "--/--/----"
        assignee_display = self.assignee_id if self.assignee_id else "Unassigned"
        print(
            f"{self.project_id:<12} | "
            f"{self.id:<18} | "
            f"{self.name:<20} | "
            f"{assignee_display:<12} | "
            f"{s_date:<10}-{d_date:<10} | "
            f"{self.status_task:<12}"
        )