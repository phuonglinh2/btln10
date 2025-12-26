from managers.ProjectItem_manager import ProjectItemManager
from models.project import Project
import csv
import re

class ProjectManager(ProjectItemManager):
    """
    Quản lý nghiệp vụ Project – đồng bộ Project / Task / Staff
    """

    def __init__(self, filename, staff_manager, task_manager):
        super().__init__(
            filename=filename,
            cls=Project,
            fieldnames=Project.csv_fields(),
            id_field="project_id"
        )
        self.staff_manager = staff_manager
        self.task_manager = task_manager

    # ================= FILE =================
    def save_to_file(self):
        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for obj in self.items:
                writer.writerow(obj.to_dict())

    # ================= BASIC FIND =================
    def find_by_id(self, project_id):
        return next(
            (p for p in self.items if p.project_id == project_id),
            None
        )

    # ================= HÀM NHẬP MÃ DỰ ÁN HỢP LỆ =================
    def _input_valid_project_id(self):
        while True:
            pid = input("Nhập mã dự án (PYY_NNNNN) hoặc 'exit' để thoát: ").strip()
            if pid.lower() == "exit":
                return None
            if not pid:
                print("Bạn phải nhập mã dự án!")
                continue
            if not re.fullmatch(r"P\d{2}_\d{5}", pid):
                print("Sai định dạng mã dự án (VD: P25_00001)")
                continue
            return pid

    # ================= CRUD =================
    def add_project(self):
        print("\n--- THÊM DỰ ÁN ---")
        project = Project()

        # 1. Nhập thông tin cơ bản dự án (không bao gồm PM)
        project.input_info(
            existing_project_ids=[p.project_id for p in self.items]
        )

        # 2. Nhập PM của dự án
        while True:
            pm_id = input("Nhập mã PM của dự án (Enter để hủy): ").strip()

            if not pm_id:
                print("Đã hủy thêm dự án")
                return  # thoát hàm nếu muốn hủy

            pm = self.staff_manager.find_by_id(pm_id)
            if not pm:
                print("Nhân viên không tồn tại.")
                continue

            if getattr(pm, "management_title", "") != "Project Manager":
                print("Người nhập phải là Project Manager")
                continue

            # Gán PM cho dự án
            project.pm_id = pm_id
            break

        # 3. Thêm dự án vào danh sách và lưu file
        self.items.append(project)
        self.save_to_file()
        print(f"Thêm dự án '{project.project_name}' thành công với PM: {project.pm_id}")

    def update_project(self):
        print("\n--- CẬP NHẬT DỰ ÁN ---")
        project_id = self._input_valid_project_id()
        if not project_id:
            print("Hủy cập nhật dự án")
            return

        project = self.find_by_id(project_id)
        if not project:
            print(f"Không tìm thấy dự án '{project_id}'.")
            return

        project.update_info()

        # Cập nhật PM nếu muốn
        while True:
            pm_id = input(f"Mã PM hiện tại [{getattr(project,'pm_id','')}], nhập mới hoặc Enter để giữ: ").strip()
            if not pm_id:
                break
            pm = self.staff_manager.find_by_id(pm_id)
            if not pm:
                print("Nhân viên không tồn tại.")
                continue
            if getattr(pm, "management_title", "") != "Project Manager":
                print("Người này không phải Project Manager.")
                continue
            project.pm_id = pm_id
            break

        self.save_to_file()
        print("Cập nhật dự án thành công")

    def delete_project(self):
        print("\n--- XÓA DỰ ÁN ---")
        project_id = self._input_valid_project_id()
        if not project_id:
            print("Hủy xóa dự án")
            return

        project = self.find_by_id(project_id)
        if not project:
            print(f"Không tìm thấy dự án '{project_id}'.")
            return

        confirm = input(f"Xác nhận xóa dự án {project.project_name}? (y/n): ").strip().lower()
        if confirm != "y":
            print("Đã hủy thao tác")
            return

        # XÓA TẤT CẢ TASK THUỘC PROJECT (CHA → CON)
        tasks_to_delete = [
            t for t in self.task_manager.items
            if t.project_id == project.project_id
        ]

        for task in tasks_to_delete:
            # gỡ task khỏi tất cả nhân viên
            self.staff_manager.remove_task_from_all_staff(task.id)

            # xóa task khỏi task manager
            self.task_manager.items.remove(task)

        # XÓA PROJECT (CHA)
        self.items.remove(project)

        # LƯU FILE
        self.save_to_file()
        self.task_manager.save_to_file()
        self.staff_manager.save_to_file()

        print(f"Đã xóa dự án {project.project_name} và toàn bộ task liên quan.")


    # ================= SEARCH & DISPLAY =================
    def search_project(self):
        keyword = input("Nhập mã hoặc khách hàng: ").strip().lower()
        if not keyword:
            print("Không được để trống")
            return

        result = [p for p in self.items if keyword in p.project_id.lower() or keyword in p.customer.lower()]
        if not result:
            print("Không tìm thấy dự án")
            return

        print(f"{'Mã DA':<10} | {'Tên dự án':<25} | {'Khách hàng':<20} | {'Ngày BD':<12} | {'Ngày DK':<12} | {'Ngày TT':<12} | {'Ngân sách':<12} | {'Trạng thái':<15}")
        for p in result:
            p.display_info()

    def get_members_of_project(self):
        print("\n--- DANH SÁCH NHÂN VIÊN THAM GIA DỰ ÁN ---")
        project_id = self._input_valid_project_id()
        if not project_id:
            print("Hủy thao tác")
            return

        project = self.find_by_id(project_id)
        if not project:
            print("Dự án không tồn tại.")
            return

        if not self.task_manager:
            print("Chưa kết nối với Task Manager.")
            return

        tasks_of_project = [t for t in self.task_manager.items if t.project_id == project_id]
        if not tasks_of_project:
            print("Dự án này chưa có công việc nào.")
            return

        member_ids = {t.assignee_id for t in tasks_of_project if t.assignee_id and t.assignee_id != "Unassigned"}
        if not member_ids:
            print("Dự án chưa phân công công việc cho nhân viên.")
            return

        print(f"\nDanh sách thành viên tham gia dự án {project.project_name} ({len(member_ids)} người):")
        print(f"{'Mã NV':<10} | {'Họ Tên':<25} | {'Vai Trò':<15}")

        if self.staff_manager:
            found_count = 0
            for staff_id in member_ids:
                staff = self.staff_manager.find_by_id(staff_id)
                if staff:
                    print(f"{staff.staff_id:<10} | {staff.full_name:<25} | {staff.role:<15}")
                    found_count += 1
            if found_count == 0:
                print("(Không tìm thấy thông tin chi tiết nhân viên trong hệ thống)")
        else:
            for mid in member_ids:
                print(f"- {mid}")

    def display_all_projects(self):
        if not self.items:
            print("Danh sách dự án trống")
            return

        print("\n================ THÔNG TIN DỰ ÁN ================")
        print(f"{'Mã DA':<10} | {'Tên dự án':<25} | {'Khách hàng':<20} | {'Ngày BD':<12} | {'Ngày DK':<12} | {'Ngày TT':<12} | {'Ngân sách':<12} | {'Trạng thái':<15}")
        print("-"*100)
        for p in self.items:
            p.display_info()
