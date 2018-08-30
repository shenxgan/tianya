import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote


class TianYa():
    def __init__(self, base_url):
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

    def get_one_page(self, url):
        self.landlord_text = []
        self.all_text = []

        r = requests.get(url)
        print(url)
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
            page += 1
            if page > self.total_page:
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


if __name__ == "__main__":
    base_url = "http://bbs.tianya.cn/post-house-252774-{page}.shtml"
    # base_url = "http://bbs.tianya.cn/post-stocks-2021229-{page}.shtml"
    # base_url = "http://bbs.tianya.cn/post-stocks-2022329-{page}.shtml"
    ty = TianYa(base_url)
    ty.run()
