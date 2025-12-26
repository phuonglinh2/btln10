from managers.ProjectItem_manager import ProjectItemManager
from models.project import Project
import csv


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

    # ==================================================
    # FILE
    # ==================================================
    def save_to_file(self):
        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for obj in self.items:
                writer.writerow(obj.to_dict())

    # ==================================================
    # BASIC FIND
    # ==================================================
    def find_by_id(self, project_id):
        return next(
            (p for p in self.items if p.project_id == project_id),
            None
        )

    # ==================================================
    # CRUD
    # ==================================================
    def add_project(self):
        print("\n--- THÊM DỰ ÁN ---")
        project = Project()
        project.input_info(
            existing_project_ids=[p.project_id for p in self.items],
            staff_manager=self.staff_manager
        )
        self.items.append(project)
        self.save_to_file()
        print("Thêm dự án thành công")

    def update_project(self):
        print("\n--- CẬP NHẬT DỰ ÁN ---")

        # Bắt buộc nhập mã dự án
        while True:
            project_id = input("Nhập mã dự án: ").strip()
            if not project_id:
                print("Bạn phải nhập mã dự án để có thể cập nhật!")
                continue

            project = self.find_by_id(project_id)
            if not project:
                print(f"Không tìm thấy dự án '{project_id}'. Nhập lại.")
                continue

            break 
        project.update_info()
        self.save_to_file()
        print("Cập nhật dự án thành công")

    def delete_project(self):
        print("\n--- XÓA DỰ ÁN ---")

        # Bắt buộc nhập mã dự án
        while True:
            project_id = input("Nhập mã dự án: ").strip()
            if not project_id:
                print("Bạn phải nhập mã dự án!")
                continue

            project = self.find_by_id(project_id)
            if not project:
                print(f"Không tìm thấy dự án '{project_id}'. Nhập lại.")
                continue

            break  
        confirm = input(
            f"Xác nhận xóa dự án {project.project_name}? (y/n): "
        ).strip().lower()

        if confirm != "y":
            print("Đã hủy thao tác")
            return

        # ----- HỦY TASK -----
        for task_id in project.task_list[:]:
            task = self.task_manager.find_by_id(task_id)
            if task:
                task.status = "Cancelled"
                self.staff_manager.remove_task_from_all_staff(task_id)
                self.task_manager.items.remove(task)

        self.items.remove(project)

        self.save_to_file()
        self.task_manager.save_to_file()
        self.staff_manager.save_to_file()

        print("Đã xóa dự án")

    # ==================================================
    # SEARCH & DISPLAY
    # ==================================================
    def search_project(self):
        keyword = input("Nhập mã hoặc khách hàng: ").strip().lower()

        if not keyword:
            print("Không được để trống")
            return

        result = [
            p for p in self.items
            if keyword in p.project_id.lower()
            or keyword in p.customer.lower()
        ]

        if not result:
            print("Không tìm thấy dự án")
            return
        print(
            f"{'Mã DA':<10} | {'Tên dự án':<25} | {'Khách hàng':<20} | "
            f"{'Ngày BD':<12} | {'Ngày DK':<12} | {'Ngày TT':<12} | "
            f"{'Ngân sách':<12} | {'Trạng thái':<15}"
        )
        for p in result:
            p.display_info()

    def get_members_of_project(self):
        print("\n--- DANH SÁCH NHÂN VIÊN THAM GIA DỰ ÁN ---")
        project_id = input("Nhập mã dự án: ").strip()

        # 1. Kiểm tra dự án tồn tại
        project = self.find_by_id(project_id)
        if not project:
            print("Dự án không tồn tại.")
            return

        # 2. Lấy danh sách task thuộc dự án này từ TaskManager
        # Lưu ý: Cần kiểm tra xem task_manager có tồn tại không
        if not self.task_manager:
            print("Chưa kết nối với Task Manager.")
            return

        tasks_of_project = [
            t for t in self.task_manager.task_list 
            if t.project_id == project_id
        ]

        if not tasks_of_project:
            print("Dự án này chưa có công việc nào.")
            return

        # 3. Lấy tập hợp các assignee_id
        member_ids = {t.assignee_id for t in tasks_of_project if t.assignee_id and t.assignee_id != "Unassigned"}
        if not member_ids:
            print("Dự án chưa phân công công việc cho nhân viên.")
            return

        print(f"\nDanh sách thành viên tham gia dự án {project.project_name} ({len(member_ids)} người):")
        print(f"{'Mã NV':<10} | {'Họ Tên':<25} | {'Vai Trò':<15}")

        # 4. Hiển thị thông tin chi tiết từ StaffManager
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
            # Nếu không có staff_manager thì chỉ in ID
            for mid in member_ids:
                print(f"- {mid}")

    def display_all_projects(self):
        if not self.items:
            print("Danh sách dự án trống")
            return

        print("\n================ THÔNG TIN DỰ ÁN ================")
        print(
            f"{'Mã DA':<10} | {'Tên dự án':<25} | {'Khách hàng':<20} | "
            f"{'Ngày BD':<12} | {'Ngày DK':<12} | {'Ngày TT':<12} | "
            f"{'Ngân sách':<12} | {'Trạng thái':<15}"
        )
        print("-"*100)
        for p in self.items:
            p.display_info()
        