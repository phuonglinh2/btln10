import csv
from datetime import datetime
from reports.base_report import BaseReport


class FinalReport(BaseReport):
    """
    Báo cáo tổng kết dự án
    - Snapshot cuối cùng của dự án
    - Chỉ được tạo SAU KHI dự án kết thúc
    - Người lập phải là PM của dự án
    """

    CSV_FILE = "final_reports.csv"

    def __init__(
        self,
        project_id="",
        report_id="",
        author_id="",
        report_date=None,
        stats=None,
        is_loading=False
    ):
        super().__init__(
            report_id=report_id,
            project_id=project_id,
            author_id=author_id,
            created_date=report_date or datetime.now()
        )

        self.is_loading = is_loading

        # ===== SNAPSHOT DATA =====
        stats = stats or {}

        self.project_name = stats.get("project_name", "")
        self.customer = stats.get("customer", "")
        self.project_start_date = stats.get("project_start_date")
        self.actual_end_date = stats.get("actual_end_date")
        self.duration_days = stats.get("duration_days", 0)

        self.total_tasks = stats.get("total_tasks", 0)
        self.completed_tasks = stats.get("completed_tasks", 0)
        self.ontime_tasks = stats.get("ontime_tasks", 0)
        self.overdue_tasks = stats.get("overdue_tasks", 0)
        self.cancelled_tasks = stats.get("cancelled_tasks", 0)
        self.overall_progress = stats.get("overall_progress", 0.0)
        self.project_status = stats.get("project_status", "N/A")

    # ======================================================
    # LOAD DATA + VALIDATION
    # ======================================================
    def input_info(self, project_manager, task_manager, staff_manager):

        project = project_manager.find_by_id(self.project_id)
        if not project:
            raise ValueError(f"Không tìm thấy dự án {self.project_id}")

        pm_id = getattr(project, "pm_id", None)
        if not pm_id:
            raise ValueError("Dự án chưa được gán Project Manager")

        if self.author_id != pm_id:
            raise PermissionError(
                f"Chỉ PM của dự án ({pm_id}) mới được lập báo cáo tổng kết"
            )

        author = staff_manager.find_by_id(self.author_id)
        if not author or getattr(author, "management_title", "") != "Project Manager":
            raise PermissionError("Người lập báo cáo không phải Project Manager")

        self.project_name = project.project_name
        self.customer = project.customer
        self.project_start_date = self._parse_date(project.start_date)
        self.actual_end_date = self._parse_date(project.actual_end_date)
        self.project_status = project.status_project

        self._validate_report_date()

        tasks = [t for t in task_manager.task_list if t.project_id == self.project_id]

        self.total_tasks = len(tasks)
        self.completed_tasks = len([t for t in tasks if t.status_task == "Completed"])
        self.cancelled_tasks = len([t for t in tasks if t.status_task == "Cancelled"])

        self.overdue_tasks = 0
        for t in tasks:
            if t.deadline and t.completed_date:
                if self._parse_date(t.completed_date) > self._parse_date(t.deadline):
                    self.overdue_tasks += 1

        self.ontime_tasks = max(0, self.completed_tasks - self.overdue_tasks)

        if self.project_start_date and self.actual_end_date:
            self.duration_days = (self.actual_end_date - self.project_start_date).days

        if self.total_tasks > 0:
            self.overall_progress = round(
                (self.completed_tasks / self.total_tasks) * 100, 2
            )
        else:
            self.overall_progress = 0.0

    # ======================================================
    # VALIDATION
    # ======================================================
    def _validate_report_date(self):
        if not self.actual_end_date:
            raise ValueError("Dự án chưa có ngày kết thúc thực tế")

        if self.created_date.date() < self.actual_end_date.date():
            raise ValueError(
                "Ngày lập báo cáo phải >= ngày kết thúc dự án"
            )

    def _parse_date(self, d):
        if isinstance(d, datetime):
            return d
        if isinstance(d, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(d, fmt)
                except ValueError:
                    pass
        return None

    # ======================================================
    # LOAD FROM CSV
    # ======================================================
    @classmethod
    def from_dict(cls, data):
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        created_raw = data.get("created_date")
        try:
            created_date = datetime.strptime(
                created_raw, "%Y-%m-%d %H:%M:%S"
            ) if created_raw else datetime.now()
        except ValueError:
            created_date = datetime.now()

        return cls(
            project_id=data.get("project_id", ""),
            report_id=data.get("report_id", ""),
            author_id=data.get("author_id", ""),
            report_date=created_date,
            stats={
                "project_name": data.get("project_name", ""),
                "customer": data.get("customer", ""),
                "project_start_date": data.get("project_start_date"),
                "actual_end_date": data.get("actual_end_date"),
                "duration_days": safe_int(data.get("duration_days")),
                "total_tasks": safe_int(data.get("total_tasks")),
                "completed_tasks": safe_int(data.get("completed_tasks")),
                "ontime_tasks": safe_int(data.get("ontime_tasks")),
                "overdue_tasks": safe_int(data.get("overdue_tasks")),
                "cancelled_tasks": safe_int(data.get("cancelled_tasks")),
                "overall_progress": safe_float(data.get("overall_progress")),
                "project_status": data.get("project_status", ""),
            },
            is_loading=True
        )

    # ======================================================
    # HIỂN THỊ 
    # ======================================================
    def display_info(self):
        print("\n--- CHI TIẾT BÁO CÁO TỔNG KẾT ---")
        print(f"Mã báo cáo      : {self.report_id}")
        print(f"Mã dự án        : {self.project_id}")
        print(f"Tên dự án       : {self.project_name}")
        print(f"Khách hàng      : {self.customer}")
        print(f"Người lập       : {self.author_id}")
        print(f"Ngày lập        : {self.created_date.strftime('%d/%m/%Y')}")

        print(f"Tổng task       : {self.total_tasks}")
        print(f"Hoàn thành      : {self.completed_tasks}")
        print(f"Đúng hạn        : {self.ontime_tasks}")
        print(f"Quá hạn         : {self.overdue_tasks}")
        print(f"Hủy             : {self.cancelled_tasks}")
        print(f"Tiến độ (%)     : {self.overall_progress}")
        print(f"Trạng thái DA   : {self.project_status}")

    # ======================================================
    # CSV
    # ======================================================
    @staticmethod
    def csv_fields():
        return [
            "project_id", "report_id", "author_id", "created_date",
            "project_name", "customer", "project_start_date", "actual_end_date",
            "duration_days", "total_tasks", "completed_tasks", "ontime_tasks",
            "overdue_tasks", "cancelled_tasks", "overall_progress", "project_status",
        ]

    def as_dict(self):
        def fmt(d): return d.strftime("%d/%m/%Y") if d else ""

        data = super().as_dict()
        data.update({
            "project_name": self.project_name,
            "customer": self.customer,
            "project_start_date": fmt(self.project_start_date),
            "actual_end_date": fmt(self.actual_end_date),
            "duration_days": self.duration_days,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "ontime_tasks": self.ontime_tasks,
            "overdue_tasks": self.overdue_tasks,
            "cancelled_tasks": self.cancelled_tasks,
            "overall_progress": self.overall_progress,
            "project_status": self.project_status,
        })
        return data

    def save(self):
        return self.add_item(self.CSV_FILE)
