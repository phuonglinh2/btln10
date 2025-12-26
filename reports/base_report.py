from abc import ABC
from datetime import datetime
import csv
import os


class BaseReport(ABC):
    def __init__(self, report_id, project_id, author_id, created_date=None):
        self.report_id = report_id
        self.project_id = project_id
        self.author_id = author_id
        self.created_date = created_date or datetime.now()

    # ================= CHUYỂN OBJECT -> DICT =================
    def as_dict(self):
        """Chuyển object sang dict để lưu CSV"""
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "author_id": self.author_id,
            "created_date": self.created_date.strftime("%Y-%m-%d %H:%M:%S")
        }

    # ================= CSV =================
    @staticmethod
    def load_from_csv(filename):
        """Đọc CSV và trả về danh sách dict"""
        if not os.path.exists(filename):
            return []
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)

    @staticmethod
    def save_to_csv(filename, data_list):
        """Ghi danh sách dict vào CSV"""
        if not data_list:
            return
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data_list[0].keys())
            writer.writeheader()
            writer.writerows(data_list)

    # ================= CÁC PHƯƠNG THỨC =================
    def add_item(self, filename):
        data = BaseReport.load_from_csv(filename)
        data.append(self.as_dict())
        BaseReport.save_to_csv(filename, data)
        return True

    @staticmethod
    def update_item(filename, report_id, new_data):
        data = BaseReport.load_from_csv(filename)
        updated = False
        for row in data:
            if row["report_id"] == report_id:
                row.update({k: v for k, v in new_data.items() if k in row})
                updated = True
                break
        BaseReport.save_to_csv(filename, data)
        return updated

    @staticmethod
    def delete_item(filename, report_id):
        data = BaseReport.load_from_csv(filename)
        new_data = [r for r in data if r["report_id"] != report_id]
        BaseReport.save_to_csv(filename, new_data)
        return True

    @staticmethod
    def search_item(filename, keyword):
        data = BaseReport.load_from_csv(filename)
        keyword = keyword.lower()
        return [r for r in data if keyword in r["report_id"].lower() or keyword in r["project_id"].lower()]

    # ================= HIỂN THỊ =================
    def format_display(self):
        return (
            f"Mã báo cáo   : {self.report_id}\n"
            f"Mã dự án     : {self.project_id}\n"
            f"Người tạo    : {self.author_id}\n"
            f"Ngày tạo     : {self.created_date.strftime('%d/%m/%Y')}"
        )
