class Progress:
    def __init__(self, project_list, all_tasks):
        """
        project_list: danh sách tất cả Project
        all_tasks: danh sách tất cả Task object
        """
        # Nhập mã dự án
        while True:
            pid = input("Nhập mã dự án để tính tiến độ: ").strip()
            
            # --- [FIX 1] Tìm dự án an toàn (chấp nhận cả .id lẫn .project_id) ---
            found_p = None
            for p in project_list:
                # Lấy ID an toàn: ưu tiên project_id, nếu không có thì lấy id
                current_p_id = getattr(p, 'project_id', getattr(p, 'id', ''))
                if current_p_id == pid:
                    found_p = p
                    break
            
            if not found_p:
                print("Dự án không tồn tại. Nhập lại.")
                continue
            
            self.project = found_p
            self.pid = pid # Lưu lại pid đã nhập để dùng về sau
            break

        # --- [FIX 2] Lọc Task ---
        self.tasks = [t for t in all_tasks if t.project_id == self.pid]

    # Tổng số task (bỏ qua task Cancelled)
    def total_tasks(self):
        return len([t for t in self.tasks if t.status_task != "Cancelled"])

    # Task theo trạng thái (bỏ qua Cancelled khi tính tổng)
    def tasks_by_status(self, status):
        if status == "Cancelled":
            return [t for t in self.tasks if t.status_task == "Cancelled"]
        return [t for t in self.tasks if t.status_task == status]

    # Tỉ lệ tiến độ (%) (bỏ qua Cancelled)
    def progress_rate(self):
        total = self.total_tasks()
        if total == 0:
            return 0
        completed = len(self.tasks_by_status("Completed"))
        return round((completed / total) * 100, 2)

    # Hiển thị bảng tổng quan và chi tiết task
    def display_summary_with_tasks(self):
        total = self.total_tasks()
        completed = len(self.tasks_by_status("Completed"))
        in_progress = len(self.tasks_by_status("In Progress"))
        todo = len(self.tasks_by_status("To Do"))
        cancelled = len(self.tasks_by_status("Cancelled"))

        # --- [FIX 3] Lấy tên dự án an toàn (tránh lỗi has no attribute 'name') ---
        p_name = getattr(self.project, 'project_name', getattr(self.project, 'name', 'Unknown'))
        p_id = getattr(self.project, 'project_id', getattr(self.project, 'id', self.pid))

        print(f"\n=== TIẾN ĐỘ DỰ ÁN: {p_name} ({p_id}) ===")
        print(f"Tổng công việc       : {total}")
        print(f"Đã hoàn thành        : {completed}")
        print(f"Đang thực hiện       : {in_progress}")
        print(f"Công việc mới        : {todo}")
        print(f"Công việc đóng/hủy   : {cancelled}")
        print(f"Tỉ lệ tiến độ (%)    : {self.progress_rate()}%")

        if self.tasks:
            print("\nChi tiết công việc:")
            print(f"{'Task ID':20} | {'Name':25} | {'Assignee':10} | {'Priority':8} | {'Status':12}")
            print("-"*85)
            for t in self.tasks:
                # --- [FIX 4] Lấy thuộc tính task an toàn (tránh lỗi t.id vs t.task_id) ---
                tid = getattr(t, 'id', getattr(t, 'task_id', ''))
                tname = getattr(t, 'name', getattr(t, 'task_name', ''))
                
                print(f"{tid:<20} | {tname:<25} | {t.assignee_id:<10} | {t.priority:<8} | {t.status_task:<12}")