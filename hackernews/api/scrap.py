import os

import requests
from bs4 import BeautifulSoup as bs

from hackernews.models import Post

news_url = 'https://news.ycombinator.com/'
posts_db_limit = int(os.environ['POSTS_DB_LIMIT']) if os.environ.get('POSTS_DB_LIMIT') else None


def delete_old_posts():
    current_count = Post.objects.count()
    if current_count + 30 > posts_db_limit:
        count_to_remove = current_count + 30 - posts_db_limit
        posts_to_remove = Post.objects.values_list('pk')[:count_to_remove]
        Post.objects.filter(pk__in=posts_to_remove).delete()


def scrap():
    responce = requests.get(news_url)
    if responce.status_code != 200:
        raise ConnectionError(f'{news_url} status code: {responce.status_code}')
    html = responce.content
    soup = bs(html, 'html.parser')
    posts = soup.find_all('a', class_='storylink')
    if not posts:
        raise ConnectionError(f'No posts found at page {news_url}')
    if not len(posts) == 30:
        raise ConnectionError(f'Page {news_url} contains only {len(posts)} posts of 30')

    if posts_db_limit:
        delete_old_posts()

    for post in reversed(posts):
        title = post.text
        url = post['href']
        Post.create(title, url)
