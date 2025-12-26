from datetime import datetime

class ProjectItem:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.description = ""
        self.start_date = None

    def input_info(self):
        self.id = input("Nhập ID: ").strip()
        self.name = input("Nhập tên: ").strip()
        self.description = input("Nhập mô tả: ").strip()
        self.input_start_date()

    # TÁCH RIÊNG NGÀY BẮT ĐẦU
    def input_start_date(self):
        while True:
            date_str = input("Ngày bắt đầu (dd/mm/yyyy): ").strip()
            try:
                self.start_date = datetime.strptime(date_str, "%d/%m/%Y")
                break
            except ValueError:
                print("Sai định dạng ngày (dd/mm/yyyy)")

    def display_info(self):
        print(
            f"{self.id:<10} | "
            f"{self.name:<25} | "
            f"{self.description:<30} | "
            f"{self.start_date}"
        )
