from reports.base_report import BaseReport
from datetime import datetime, timedelta


class WeeklyReport(BaseReport):
    """
    Báo cáo tiến độ dự án theo tuần.
    Ràng buộc thời gian tuần đã xử lý ở WeeklyReportManager.
    """

    WEEKLY_CSV = "weekly_reports.csv"

    def __init__(
        self,
        wreport_id,
        project,
        author,
        task_manager,
        report_date,
        period_start_date,
        period_end_date,
        is_loading=False
    ):
        # ================= PROJECT ID =================
        self.p_id = getattr(project, "project_id", getattr(project, "id", ""))

        # ================= VALIDATE =================
        if not is_loading:
            self._validate_wreport_id(wreport_id)
            self._validate_author(author)

        # ================= BASE =================
        super().__init__(
            report_id=wreport_id,
            project_id=self.p_id,
            author_id=author.staff_id,
            created_date=report_date,
        )

        # ================= ATTR =================
        self.project = project
        self.task_manager = task_manager
        self.period_start_date = period_start_date
        self.period_end_date = period_end_date

        # ================= DATA =================
        self.project_tasks = self._get_project_tasks()
        self.task_list = self._get_tasks_in_week()

        self.total_tasks_count = self._count_total_tasks()
        self.completed_tasks_count = self._count_completed_tasks()

        self.overdue_tasks = self._get_overdue_tasks()
        self.overdue_tasks_count = len(self.overdue_tasks)

        self.actual_progress = self._calculate_progress()
        self.progress_status = self._get_progress_status()

        self.next_period_tasks = self._get_next_period_tasks()

    # ======================================================
    # VALIDATION
    # ======================================================
    def _validate_wreport_id(self, wreport_id):
        if not wreport_id.startswith("WR"):
            raise ValueError("Mã báo cáo phải bắt đầu bằng WR")

        existing = BaseReport.load_from_csv(self.WEEKLY_CSV)
        if any(r["report_id"] == wreport_id for r in existing):
            raise ValueError("Mã báo cáo tuần đã tồn tại")

    def _validate_author(self, author):
        if getattr(author, "management_title", "") != "Project Manager":
            raise PermissionError("Chỉ Project Manager mới được tạo báo cáo tuần")

    # ======================================================
    # CORE DATA
    # ======================================================
    def _get_project_tasks(self):
        return [
            t for t in self.task_manager.task_list
            if t.project_id == self.p_id
        ]

    def _get_tasks_in_week(self):
        return [
            t for t in self.project_tasks
            if (
                (t.start_date and self.period_start_date <= t.start_date <= self.period_end_date)
                or
                (t.deadline and self.period_start_date <= t.deadline <= self.period_end_date)
                or
                (
                    t.start_date and t.deadline
                    and t.start_date < self.period_start_date
                    and t.deadline > self.period_end_date
                )
            )
        ]

    # ======================================================
    # CALCULATION (THEO TUẦN)
    # ======================================================
    def _count_total_tasks(self):
        return len([
            t for t in self.task_list
            if t.status_task != "Cancelled"
        ])

    def _count_completed_tasks(self):
        return len([
            t for t in self.task_list
            if (
                t.status_task == "Completed"
                and t.completed_date
                and self.period_start_date <= t.completed_date <= self.period_end_date
            )
        ])

    def _calculate_progress(self):
        if self.total_tasks_count == 0:
            return 0.0
        return round(
            (self.completed_tasks_count / self.total_tasks_count) * 100,
            2
        )

    def _get_progress_status(self):
        # 1. Có task quá hạn trong tuần → Delay
        if self.overdue_tasks_count > 0:
            return "Delay"

        # 2. Không có task trong tuần
        if self.total_tasks_count == 0:
            return "On Track"

        # 3. Có task nhưng chưa hoàn thành trong tuần
        if self.completed_tasks_count < self.total_tasks_count:
            return "At Risk"

        # 4. Hoàn thành hết
        return "On Track"

    # ======================================================
    # OVERDUE & PLAN
    # ======================================================
    def _get_overdue_tasks(self):
        return [
            t for t in self.task_list
            if (
                t.deadline
                and t.deadline < self.period_end_date
                and t.status_task not in ("Completed", "Cancelled")
            )
        ]

    def _get_next_period_tasks(self):
        next_start = self.period_end_date + timedelta(days=1)
        next_end = next_start + timedelta(days=6)

        p_end = getattr(self.project, "expected_end_date", None)
        if p_end and next_end > p_end:
            next_end = p_end

        return [
            t for t in self.project_tasks
            if (
                t.status_task not in ("Completed", "Cancelled")
                and (
                    (t.start_date and next_start <= t.start_date <= next_end)
                    or
                    (t.deadline and next_start <= t.deadline <= next_end)
                )
            )
        ]

    # ======================================================
    # CSV & DISPLAY
    # ======================================================
    def as_dict(self):
        data = super().as_dict()
        data.update({
            "period_start": self.period_start_date.strftime("%Y-%m-%d"),
            "period_end": self.period_end_date.strftime("%Y-%m-%d"),
            "total_tasks": self.total_tasks_count,
            "completed_tasks": self.completed_tasks_count,
            "overdue_tasks": self.overdue_tasks_count,
            "progress": self.actual_progress,
            "status": self.progress_status,
        })
        return data

    def save(self):
        return self.add_item(self.WEEKLY_CSV)

    def display(self):
        print("\n" + "=" * 70)
        print("BÁO CÁO TIẾN ĐỘ TUẦN".center(70))
        print("=" * 70)

        print("\n[1] THÔNG TIN CHUNG")
        print(f"  Mã báo cáo   : {self.report_id}")
        print(f"  Dự án        : {self.project_id}")
        print(
            f"  Thời gian    : "
            f"{self.period_start_date.strftime('%d/%m/%Y')} -> "
            f"{self.period_end_date.strftime('%d/%m/%Y')}"
        )
        print(f"  Người lập    : {self.author_id}")

        print("\n[2] TÓM TẮT TIẾN ĐỘ")
        print(f"  Tổng CV      : {self.total_tasks_count}")
        print(f"  Hoàn thành   : {self.completed_tasks_count}")
        print(f"  Quá hạn      : {self.overdue_tasks_count}")
        print(f"  Tiến độ      : {self.actual_progress:.2f}%")
        print(f"  Trạng thái   : {self.progress_status}")

        print("\n[3] CÔNG VIỆC TRỄ HẠN")
        if not self.overdue_tasks:
            print("  Không có")
        else:
            for t in self.overdue_tasks:
                d = t.deadline.strftime("%d/%m/%Y") if t.deadline else "N/A"
                print(f"  - {t.id} | {t.name} | Hạn: {d}")

        print("\n[4] KẾ HOẠCH TUẦN SAU")
        if not self.next_period_tasks:
            print("  Không có (hoặc dự án đã kết thúc)")
        else:
            for t in self.next_period_tasks:
                s = t.start_date.strftime("%d/%m/%Y") if t.start_date else "N/A"
                print(f"  - {t.id} | {t.name} | BĐ: {s}")

        print("\n" + "=" * 70)
