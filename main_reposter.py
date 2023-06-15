import os
import re
import requests
from bs4 import BeautifulSoup
import hashlib

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # for test mode
    # with open('soup.html', 'w', encoding='utf-8') as file:
    #     file.write(str(soup))

    # Keep only the links that match the specified pattern
    pattern = re.compile(r'^https:\/\/finance\.yahoo\.com\/.*\.html$')
    links = [link.get('href') for link in soup.find_all('a', href=pattern)]
    return links

def load_hashes(hashes_file_path):
    hashes = {}
    if os.path.isfile(hashes_file_path):
        with open(hashes_file_path, 'r') as file:
            for line in file:
                link, hash_value = line.strip().split('|')
                hashes[link] = hash_value
    return hashes

def save_hashes(hashes, hashes_file_path):
    with open(hashes_file_path, 'w') as file:
        for link, hash_value in hashes.items():
            file.write(f'{link}|{hash_value}\n')

def check_new_links(previous_hashes, links_for_work, new_link_list, hashes_file_path):
    for link in links_for_work:
        content_hash = hashlib.sha256(link.encode()).hexdigest()
        if link not in previous_hashes:
            previous_hashes[link] = content_hash
            new_link_list.append(link)
            continue
        # print(previous_hashes[link], ' - previous_hashes[link]', previous_hashes[link] != content_hash , content_hash )
        if previous_hashes.get(link) != content_hash:
            previous_hashes[link] = content_hash
            new_link_list.append(link)
            print(link)
        save_hashes(previous_hashes, hashes_file_path)
    return new_link_list

def main(hashes_file_path, url):

    # Specify the path to the file for saving hashes
    if not os.path.isfile(hashes_file_path):
        open(hashes_file_path, 'w').close()
        print(f'Created file {hashes_file_path}')

    previous_hashes = load_hashes(hashes_file_path)

    print('previous_hashes: \n', previous_hashes)

    links_for_work = get_links(url)
    print(links_for_work)
    new_link_list = []  # links to send
    print("Checking links for freshness.")

    check_new_links(previous_hashes, links_for_work, new_link_list, hashes_file_path)
    print(new_link_list, ' - links to send')

    write_new_links(links_for_work, hashes_file_path)  # clear the file and write only the fresh links

    return new_link_list

def write_new_links(links_for_work, hashes_file_path):
    with open(hashes_file_path, 'w') as f:
        f.write('')
    try:
        with open(hashes_file_path, 'w') as file:
            for link in links_for_work:
                content_hash = hashlib.sha256(link.encode()).hexdigest()
                file.write(f'{link}|{content_hash}\n')
    except TypeError as e:
        print("[Attention] Link list is empty. Check the program")
    print(f"File {hashes_file_path} updated.")

def start_repost_links(hashes_file_path, url):
    new_links = main(hashes_file_path, url)
    if len(new_links) == 0:
        return "New links not found" 
    return new_links

if __name__ == "__main__":
    url = 'https://finance.yahoo.com/'
    hashes_file_path = 'hashes.txt'
    main(hashes_file_path, url)
