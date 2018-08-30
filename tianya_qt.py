
from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QLineEdit, QTextBrowser, QVBoxLayout)

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote


class Dialog(QDialog):

    def __init__(self):
        super(Dialog, self).__init__()

        self.urlWidget = QLineEdit()
        self.urlWidget.setPlaceholderText("输入链接地址")

        self.centralWidget = QTextBrowser()
        self.centralWidget.setPlainText("")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.button(QDialogButtonBox.Ok).setText("开始")
        buttonBox.button(QDialogButtonBox.Cancel).setText("退出")
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.urlWidget)
        mainLayout.addWidget(self.centralWidget)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.setFixedSize(500, 300)
        self.setWindowTitle("天涯帖子抓取")

    def accept(self):
        url = self.urlWidget.text()
        if not url.strip():
            return
        aaa, bbb = url.rsplit(".", 1)
        ccc, ddd = aaa.rsplit("-", 1)
        base_url = ccc + "-" + "{page}" + "." + bbb

        # self.centralWidget.append(base_url)
        # self.centralWidget.append(self.urlWidget.text())

        self.init_tianya(base_url)
        self.run()

    def init_tianya(self, base_url):
        self.base_url = base_url
        self.total_page = 1
        self.title = None
        self.landlord = None
        self.landlord_text = []
        self.all_text = []
        self.base_path = "log"

    def get_title_total_page(self, soup):
        head = soup.find("div", id="post_head")
        title = head.find("span", class_="s_title")
        # print(title.text)
        self.title = title.text

        for item in head.find_all("a"):
            if item.text.isdigit():
                # print(item.text)
                self.total_page = int(item.text)
        # print(self.title, self.total_page)
        self.landlord_text.append(self.title)
        self.all_text.append(self.title)
        self.landlord_filename = "_".join([self.title, "landlord.log"])
        self.all_filename = "_".join([self.title, "all.log"])

        self.centralWidget.append(self.title)

    def get_one_page(self, url):
        self.landlord_text = []
        self.all_text = []

        r = requests.get(url)
        # print(url)
        html_doc = r.content
        soup = BeautifulSoup(html_doc, "html.parser")

        if self.title is None:
            self.get_title_total_page(soup)

        self.landlord_text.append(url)
        self.all_text.append(url + "\n")

        for item in soup.find_all("div", class_="atl-item"):
            contents = []
            author = unquote(item.attrs["_host"])
            time = item.attrs.get("js_restime")
            if self.landlord is None:
                self.landlord = author
                self.centralWidget.append("楼主：{author}\t\t总页数：{total_page}\n".format(author=author, total_page=self.total_page))
            # print("-" * 100)
            contents.append("-" * 100)
            # print("{author}\t\t\t{time}".format(author=author, time=time))
            contents.append("{author}\t\t\t{time}".format(author=author, time=time))
            content = item.find("div", class_="bbs-content")

            contents.extend(list(content.strings))
            # for s in content.strings:
            #     print(s)
            if author == self.landlord:
                self.landlord_text.extend(contents)
            self.all_text.extend(contents)

        self.save_to_file()

    def loop_all_pages(self):
        page = 1
        while True:
            url = self.base_url.format(page=page)
            # print(url)
            self.get_one_page(url)

            s = "完成：第 {page}/{total_page} 页".format(page=page, total_page=self.total_page)
            self.centralWidget.append(s)
            QApplication.processEvents()
            page += 1
            if page > self.total_page:
                self.centralWidget.append("已完成。")
                break

    def save_to_file(self):
        def write_file(path, data):
            with open(path, "a", encoding="utf-8") as f:
                f.write(data)
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
        write_file(os.path.join(self.base_path, self.landlord_filename), "\n".join(self.landlord_text))
        write_file(os.path.join(self.base_path, self.all_filename), "\n".join(self.all_text))

    def run(self):
        self.loop_all_pages()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
