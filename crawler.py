import requests
from bs4 import BeautifulSoup
import os

def download_page(url, path, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(path, "w", encoding="utf-8") as file:
            file.write(response.text)
        return response.text
    except requests.RequestException as e:
        print(f"Ошибка при скачивании {url}: {e}")
        return None

def find_links(html, base_url="https://ru.wikipedia.org"):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    urls = set()
    for link in links:
        href = link.get('href')
        if href and href.startswith("/wiki/") and not ":" in href:
            urls.add(base_url + href)
    return urls

def main():
    start_url = "https://ru.wikipedia.org/wiki/Россия"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    output_dir = "downloaded_pages"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    downloaded_urls = set()
    urls_to_download = {start_url}

    index_file_path = os.path.join(output_dir, "index.txt")

    i = 0
    while urls_to_download and i < 100:
        url = urls_to_download.pop()
        if url in downloaded_urls:
            continue
        print(f"Скачивание: {url}")
        file_name = f"page_{i+1}.html"
        file_path = os.path.join(output_dir, file_name)
        html = download_page(url, file_path, headers)
        if html:
            with open(index_file_path, "a", encoding="utf-8") as index_file:
                index_file.write(f"{i+1}: {url}\n")
            downloaded_urls.add(url)
            urls_to_download.update(find_links(html))
            i += 1

    print("Скачивание завершено и индексный файл создан")

if __name__ == '__main__':
    main()
