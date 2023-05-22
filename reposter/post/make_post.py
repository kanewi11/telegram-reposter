from pathlib import Path
from typing import List, Tuple, Union

from bs4 import BeautifulSoup as bs


class PostMaker:
    INST_MEDIA_SUFFIXES = []

    @staticmethod
    def _html_to_text(html: str) -> str:
        hrefs = []
        html = html.replace('\n', '||')
        soup = bs(html, 'lxml')

        # Удаляем пустые теги
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0:
                tag.extract()

        # Вынимаем ссылку из тега "а" ссылку и вставляем внутрь тега текстом
        a_tags = soup.find_all('a', href=True)
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href in hrefs:
                continue
            hrefs.append(href)
            a_tag.append(f' ({href})')

        text = soup.get_text()
        return text.replace('||', '\n')

    def _make_post_data_inst(self, file_paths: List[str]) -> Tuple[str, List[Union[str, Path]]]:
        return self._make_post_data_vk(file_paths)

    def _make_post_data_vk(self, file_paths: List[str]) -> Tuple[str, List[Union[str, Path]]]:
        text = ''
        files = []
        for file_path in file_paths:
            if file_path.endswith('HTML_text.txt'):
                with open(file_path) as text_file:
                    text = self._html_to_text(text_file.read())
                continue
            elif file_path.endswith('text.txt'):
                continue
            files.append(Path(file_path))
        return text, files

    @staticmethod
    def _get_post_file_paths(post_dir: str) -> List[str]:
        return [path.__str__() for path in Path(post_dir).iterdir() if path.is_file()]
