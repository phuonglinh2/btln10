# task_manager.py
import re
from datetime import datetime
from models.task import Task
from managers.ProjectItem_manager import ProjectItemManager


class TaskManager(ProjectItemManager):
    def __init__(self, filename="tasks.csv", project_manager=None, staff_manager=None):
        super().__init__(
            filename=filename,
            cls=Task,
            fieldnames=Task.csv_fields(),
            id_field="id"
        )
        self.project_manager = project_manager
        self.staff_manager = staff_manager
        self.task_list = self.items 

    # ================= FIND =================
    def find_by_id(self, task_id):
        return next((t for t in self.items if t.id == task_id), None)

    # ================= CRUD =================
    def add_task(self):
        print("\n--- THÊM TASK ---")
        task = Task()
        existing_ids = [t.id for t in self.items]

        # --- Chọn dự án ---
        while True:
            project_id = input("Nhập mã dự án (PYY_NNNNN): ").strip()
            if not re.fullmatch(r"P\d{2}_\d{5}", project_id):
                print("Sai định dạng dự án. VD: P25_00001")
                continue

            project = self.project_manager.find_by_id(project_id)
            if not project:
                print("Dự án không tồn tại.")
                continue
            break

        # --- Mã task ---
        prefix = f"T{project_id}_"
        while True:
            print(f"Mã task bắt buộc theo định dạng: {prefix}NNNNN")
            task_id = input("Nhập mã task: ").strip()
            if not re.fullmatch(rf"{prefix}\d{{5}}", task_id):
                print("Sai định dạng mã task.")
                continue
            if task_id in existing_ids:
                print("Mã task đã tồn tại.")
                continue
            break

        task.id = task_id
        task.project_id = project_id

        # --- Nhập thông tin ---
        staff_list = self.staff_manager.staff_list if self.staff_manager else []
        task.input_info(staff_list, project)

        # --- Validate ngày ---
        if task.start_date < project.start_date:
            print("Ngày bắt đầu task < ngày bắt đầu dự án. Tự chỉnh.")
            task.start_date = project.start_date

        if task.deadline > project.expected_end_date:
            print("Deadline task > ngày kết thúc dự kiến dự án. Tự chỉnh.")
            task.deadline = project.expected_end_date

        # --- Gán task cho staff ---
        if task.assignee_id and self.staff_manager:
            staff = self.staff_manager.find_by_id(task.assignee_id)
            if staff:
                staff.task_list.append(task.id)

        self.items.append(task)
        self.save_to_file()

        if self.staff_manager:
            self.staff_manager.save_to_file()

        print(f"Đã thêm task {task.id} thành công!")

    def update_task(self):
        print("\n--- CẬP NHẬT TASK ---")
        task_id = input("Nhập mã task: ").strip()
        task = self.find_by_id(task_id)

        if not task:
            print("Không tìm thấy task.")
            return

        staff_list = self.staff_manager.staff_list if self.staff_manager else []
        project = self.project_manager.find_by_id(task.project_id)

        task.update_info(staff_list, project)

        self.save_to_file()
        print("Cập nhật task thành công!")

    def delete_task(self):
        print("\n--- XÓA TASK ---")
        task_id = input("Nhập mã task: ").strip()
        task = self.find_by_id(task_id)

        if not task:
            print("Không tìm thấy task.")
            return

        confirm = input("Xóa vĩnh viễn? (y/n): ").lower()
        if confirm != "y":
            return

        if task.assignee_id and self.staff_manager:
            staff = self.staff_manager.find_by_id(task.assignee_id)
            if staff and task.id in staff.task_list:
                staff.task_list.remove(task.id)

        self.items.remove(task)
        self.save_to_file()

        if self.staff_manager:
            self.staff_manager.save_to_file()

        print("Đã xóa task.")

    # ================= DISPLAY =================
    def display_all_tasks(self):
        if not self.items:
            print("Danh sách task trống.")
            return

        print(f"{'Dự án':<12} | {'ID':<18} | {'Tên':<20} | {'Assignee':<12} | {'Deadline':<12} | {'Status':<12}")
        for t in self.items:
            print(
                f"{t.project_id:<12} | {t.id:<18} | {t.name:<20} | "
                f"{t.assignee_id or 'Unassigned':<12} | "
                f"{t.deadline.strftime('%d/%m/%Y') if t.deadline else '--':<12} | "
                f"{t.status_task:<12}"
            )

    def display_overdue_tasks(self):
        print("\n--- TASK QUÁ HẠN ---")
        today = datetime.now()
        overdue = [
            t for t in self.items
            if t.deadline and t.deadline < today and t.status_task != "Completed"
        ]

        if not overdue:
            print("Không có task quá hạn.")
            return

        for t in overdue:
            print(f"{t.id} | {t.name} | Deadline: {t.deadline.strftime('%d/%m/%Y')}")

    def unassign_staff(self, staff_id):
        updated = False
        for t in self.items:
            if t.assignee_id and t.assignee_id.strip().upper() == staff_id.strip().upper():
                t.assignee_id = "Unassigned"
                updated = True

        if updated:
            self.save_to_file()
            print(f"Đã gỡ task khỏi nhân viên {staff_id}")
