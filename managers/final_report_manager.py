import csv
from datetime import datetime
from reports.final_report import FinalReport


class FinalReportManager:
    def __init__(self, filename="final_reports.csv"):
        self.filename = filename

    # ======================================================
    # CREATE FINAL REPORT
    # ======================================================
    def create_report(self, project_manager, staff_manager, task_manager):
        print("\n--- TẠO BÁO CÁO TỔNG KẾT ---")

        # ===== 1. CHỌN DỰ ÁN =====
        while True:
            pid = input("Nhập mã dự án cần tổng kết: ").strip()
            project = project_manager.find_by_id(pid)

            if not project:
                print("Dự án không tồn tại.")
                continue

            if project.status_project not in ("Hoàn thành", "Hủy"):
                print("Chỉ được lập báo cáo khi dự án đã hoàn thành hoặc bị hủy.")
                continue

            break

        # ===== 2. CHỌN PM (ĐÚNG PM CỦA DỰ ÁN) =====
        while True:
            sid = input("Nhập mã PM lập báo cáo: ").strip()
            author = staff_manager.find_by_id(sid)

            if not author:
                print("Nhân viên không tồn tại.")
                continue

            if getattr(author, "management_title", "") != "Project Manager":
                print("Người này không phải Project Manager.")
                continue

            if getattr(author, "management_title", "") != "Project Manager":
                print("Chỉ Project Manager mới được lập báo cáo.")
                continue
            break

        # ===== 3. MÃ BÁO CÁO =====
        expected_id = f"FR{project.project_id}"
        print(f"Định dạng mã báo cáo: {expected_id}")

        while True:
            rid = input("Nhập mã báo cáo: ").strip()
            if rid != expected_id:
                print("Mã báo cáo không đúng định dạng.")
                continue
            break

        # ===== 4. TẠO BÁO CÁO =====
        try:
            report = FinalReport(
                project_id=project.project_id,
                report_id=rid,
                author_id=author.staff_id,
                report_date=datetime.now(),
                is_loading=False
            )

            # Nạp dữ liệu + validate
            report.input_info(
                project_manager=project_manager,
                task_manager=task_manager,
                staff_manager=staff_manager
            )

            report.display_info()

            confirm = input("Xác nhận lưu báo cáo? (y/n): ").lower()
            if confirm == "y":
                report.save()
                print("Đã lưu báo cáo tổng kết.")
            else:
                print("Đã hủy lưu báo cáo.")

        except Exception as e:
            print(f"Lỗi khi tạo báo cáo: {e}")

    # ======================================================
    # VIEW DETAIL
    # ======================================================
    def view_report_detail(self):
        print("\n--- XEM BÁO CÁO TỔNG KẾT ---")
        rid = input("Nhập mã báo cáo: ").strip()

        data = next(
            (r for r in self._load_all() if r["report_id"] == rid),
            None
        )

        if not data:
            print("Không tìm thấy báo cáo.")
            return

        report = FinalReport.from_dict(data)
        report.display_info()

    # ======================================================
    # SEARCH
    # ======================================================
    def search_report(self):
        keyword = input("Nhập mã báo cáo hoặc mã dự án: ").strip().lower()
        if not keyword:
            return

        results = [
            r for r in self._load_all()
            if keyword in r["report_id"].lower()
            or keyword in r["project_id"].lower()
        ]

        if not results:
            print("Không có báo cáo phù hợp.")
            return

        self._display_table(results)

    # ======================================================
    # DISPLAY ALL
    # ======================================================
    def display_all(self):
        data = self._load_all()
        if not data:
            print("Chưa có báo cáo tổng kết.")
            return

        self._display_table(data)

    # ======================================================
    # DELETE
    # ======================================================
    def delete_report(self):
        rid = input("Nhập mã báo cáo cần xóa: ").strip()
        data = self._load_all()

        if not any(r["report_id"] == rid for r in data):
            print("Không tìm thấy báo cáo.")
            return

        confirm = input(f"Xóa báo cáo {rid}? (y/n): ").lower()
        if confirm != "y":
            return

        updated = [r for r in data if r["report_id"] != rid]

        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FinalReport.csv_fields())
            writer.writeheader()
            writer.writerows(updated)

        print("Đã xóa báo cáo.")

    # ======================================================
    # INTERNAL
    # ======================================================
    def _load_all(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []

    def _display_table(self, data):
        print(
            f"| {'Mã BC':<15} | {'Dự án':<12} | {'Tên dự án':<25} | "
            f"{'Tiến độ':<8} | {'Kết quả':<15} |"
        )
        for r in data:
            print(
                f"| {r['report_id']:<15} | {r['project_id']:<12} | "
                f"{r['project_name'][:24]:<25} | "
                f"{r['overall_progress']:<8}% | "
                f"{r['project_status']:<15} |"
            )
