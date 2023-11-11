import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


# def add_links(url, links_set: set, level: int = 0):
#     response = requests.get(url)
#     html = response.text
#     soup = BeautifulSoup(html, "html.parser")

#     links_soup = soup.find_all("a", href=True)

#     for link_soup in links_soup:
#         href = link_soup["href"]

#         if "moulton.house.gov" in href:
#             if href.startswith("//"):
#                 href = href.replace("//", "https://")
#             links_set.add(href)
#         elif href.startswith("/"):
#             links_set.add(url + href)

#     if level > 0:
#         new_links = set()
#         for link in links_set:
#             add_links(link, new_links, level - 1)

#         links_set.update(new_links)

#     return links_set


def fetch_links(url):
    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        links_soup = soup.find_all("a", href=True)

        links = set()
        for link_soup in links_soup:
            href = link_soup["href"]
            if "moulton.house.gov" in href and 'sites/evo' not in href:
                if href.startswith("//"):
                    href = href.replace("//", "https://")
                links.add(href)
            elif href.startswith("/"):
                links.add(url + href)
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return set()


def add_links_parallel(url, level=0):
    links_set = fetch_links(url)

    if level > 0:
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(add_links_parallel, link, level - 1): link
                for link in links_set
            }
            for future in concurrent.futures.as_completed(future_to_url):
                child_links = future.result()
                links_set.update(child_links)

    return links_set


# links_set = set()
# add_links("https://moulton.house.gov", links_set, 2)

links_set = add_links_parallel("https://moulton.house.gov", 2)
print(len(links_set))


links_str = ""
for link in links_set:
    links_str += link + "\n"
open("links.txt", "w").write(links_str)
