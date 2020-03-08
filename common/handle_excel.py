# 该文件处理读取Excel中的数据和写入

import openpyxl


class ReadExcel(object):

    def __init__(self, file_name, sheet_name):
        self.file_name = file_name
        self.sheet_name = sheet_name

    def open_excel_file(self):
        self.wb = openpyxl.load_workbook(self.file_name)
        # 选择表单
        self.sh = self.wb[self.sheet_name]

    def read_data(self):
        """读取数据"""
        self.open_excel_file()
        data = list(self.sh.rows)
        title = [i.value for i in data[0]]
        cases = []
        for i in data[1:]:
            value = [c.value for c in i]
            case = dict(zip(title, value))
            cases.append(case)
        return cases

    def write_data(self, row, column, value):
        """写入数据"""
        self.open_excel_file()
        self.sh.cell(row=row, column=column, value=value)
        self.wb.save(self.file_name)
