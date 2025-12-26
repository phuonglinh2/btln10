from managers.staff_manager import StaffManager
from managers.project_manager import ProjectManager
from managers.task_manager import TaskManager
from managers.weekly_report_manager import WeeklyReportManager
from managers.final_report_manager import FinalReportManager
from models.progress import Progress


def staff_menu(staff_manager):
    while True:
        print("\n--- QUẢN LÝ NHÂN VIÊN ---")
        print("1. Thêm nhân viên")
        print("2. Cập nhật nhân viên")
        print("3. Xóa nhân viên")
        print("4. Tìm kiếm nhân viên")
        print("5. Hiển thị danh sách nhân viên")
        print("0. Quay lại")

        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            staff_manager.add_staff()
        elif choice == "2":
            staff_manager.update_staff()
        elif choice == "3":
            staff_manager.delete_staff()
        elif choice == "4":
            staff_manager.search_staff()
        elif choice == "5":
            staff_manager.display_all()
        elif choice == "0":
            break
        else:
            print("Lựa chọn không hợp lệ")


def project_menu(project_manager):
    while True:
        print("\n--- QUẢN LÝ DỰ ÁN ---")
        print("1. Thêm dự án")
        print("2. Cập nhật dự án")
        print("3. Xóa dự án")
        print("4. Tìm kiếm dự án")
        print("5. Hiển thị danh sách dự án")
        print("6. Xem nhân viên tham gia vào dự án")
        print("0. Quay lại")

        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            project_manager.add_project()
        elif choice == "2":
            project_manager.update_project()
        elif choice == "3":
            project_manager.delete_project()
        elif choice == "4":
            project_manager.search_project()
        elif choice == "5":
            project_manager.display_all_projects()
        elif choice == "6":
            project_manager.get_members_of_project()
        elif choice == "0":
            break
        else:
            print("Lựa chọn không hợp lệ.")


def task_menu(task_manager):
    while True:
        print("\n--- QUẢN LÝ CÔNG VIỆC ---")
        print("1. Thêm task")
        print("2. Cập nhật task")
        print("3. Xóa task")
        print("4. Tìm kiếm task")
        print("5. Hiển thị danh sách task")
        print("6. Kiểm tra task quá hạn")
        print("0. Quay lại")

        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            task_manager.add_task()
        elif choice == "2":
            task_manager.update_task()
        elif choice == "3":
            task_manager.delete_task()
        elif choice == "4":
            task_manager.search_task()
        elif choice == "5":
            task_manager.display_all_tasks()
        elif choice == "6":
            task_manager.display_overdue_tasks()
        elif choice == "0":
            break
        else:
            print("Lựa chọn không hợp lệ.")


def progress_menu(project_manager, task_manager):
    print("\n--- KIỂM TRA TIẾN ĐỘ DỰ ÁN ---")
    progress = Progress(
        project_list=project_manager.items, 
        all_tasks=task_manager.task_list
    )
    progress.display_summary_with_tasks()


def report_menu(weekly_manager, final_manager, project_manager, staff_manager, task_manager):
    while True:
        print("\n--- QUẢN LÝ BÁO CÁO ---")
        print("1. Báo cáo tuần (Weekly Report)")
        print("2. Báo cáo tổng kết (Final Report)")
        print("0. Quay lại")

        choice = input("Chọn chức năng: ").strip()

        # ===== MENU BÁO CÁO TUẦN =====
        if choice == "1":
            while True:
                print("\n--- BÁO CÁO TUẦN ---")
                print("1. Tạo báo cáo tuần mới")
                print("2. Xem chi tiết báo cáo (Đầy đủ)")
                print("3. Tìm kiếm báo cáo")
                print("4. Hiển thị danh sách (Tóm tắt)")
                print("5. Xóa báo cáo")
                print("0. Quay lại")

                c = input("Chọn chức năng: ").strip()
                
                if c == "1":
                    weekly_manager.create_report(project_manager, staff_manager, task_manager)
                elif c == "2":
                    weekly_manager.view_report_detail(project_manager, staff_manager, task_manager)
                elif c == "3":
                    weekly_manager.search_report()
                elif c == "4":
                    weekly_manager.display_all()
                elif c == "5":
                    weekly_manager.delete_report()
                elif c == "0":
                    break
                else:
                    print("Lựa chọn không hợp lệ.")

        # ===== MENU BÁO CÁO TỔNG KẾT =====
        elif choice == "2":
            while True:
                print("\n--- BÁO CÁO TỔNG KẾT ---")
                print("1. Tạo báo cáo tổng kết mới")
                print("2. Xem chi tiết báo cáo (Đầy đủ)")
                print("3. Tìm kiếm báo cáo")
                print("4. Hiển thị danh sách (Tóm tắt)")
                print("5. Xóa báo cáo")
                print("0. Quay lại")

                c = input("Chọn chức năng: ").strip()
                
                if c == "1":
                    final_manager.create_report(project_manager, staff_manager, task_manager)
                elif c == "2":
                    final_manager.view_report_detail(project_manager, staff_manager, task_manager)
                elif c == "3":
                    final_manager.search_report()
                elif c == "4":
                    final_manager.display_all()
                elif c == "5":
                    final_manager.delete_report()
                elif c == "0":
                    break
                else:
                    print("Lựa chọn không hợp lệ.")

        elif choice == "0":
            break
        else:
            print("Lựa chọn không hợp lệ.")


def main():
    # 1. Khởi tạo StaffManager
    staff_manager = StaffManager("staff.csv")

    # 2. Khởi tạo TaskManager (TRUYỀN staff_manager VÀO)
    # Lúc này TaskManager đã biết StaffManager là ai
    task_manager = TaskManager(
        filename="tasks.csv", 
        staff_manager=staff_manager
    )

    # 3. Khởi tạo ProjectManager
    project_manager = ProjectManager(
        "projects.csv",
        staff_manager=staff_manager,
        task_manager=task_manager
    )

    # =========================================================================
    # BƯỚC KẾT NỐI QUAN TRỌNG (DEPENDENCY INJECTION)
    # =========================================================================
    
    # 4.1. Cập nhật project_manager cho task_manager (như cũ)
    # Để TaskManager validate ngày tháng dựa trên Project
    task_manager.project_manager = project_manager

    # 4.2. [MỚI THÊM] Cập nhật task_manager cho staff_manager
    # Để khi xóa Staff -> StaffManager gọi sang TaskManager để unassign task
    # (Lưu ý: Bạn phải chắc chắn đã thêm hàm set_task_manager vào class StaffManager rồi nhé)
    staff_manager.set_task_manager(task_manager)

    # =========================================================================

    # 5. Khởi tạo các manager báo cáo
    weekly_report_manager = WeeklyReportManager("weekly_reports.csv")
    final_report_manager = FinalReportManager("final_reports.csv")
    while True:
        print("\n===== HỆ THỐNG QUẢN LÝ DỰ ÁN =====")
        print("1. Quản lý nhân viên")
        print("2. Quản lý dự án")
        print("3. Quản lý công việc")
        print("4. Kiểm tra tiến độ")
        print("5. Quản lý báo cáo")
        print("0. Thoát chương trình")

        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            staff_menu(staff_manager)
        elif choice == "2":
            project_menu(project_manager)
        elif choice == "3":
            task_menu(task_manager)
        elif choice == "4":
            progress_menu(project_manager, task_manager)
        elif choice == "5":
            # Truyền tất cả Manager cần thiết vào report_menu
            report_menu(
                weekly_report_manager, 
                final_report_manager, 
                project_manager, 
                staff_manager, 
                task_manager
            )
        elif choice == "0":
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()