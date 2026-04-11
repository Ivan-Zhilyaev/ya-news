from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Фикстура автоматически разрешает доступ к БД для всех тестов."""
    pass


@pytest.fixture
def news():
    """Фикстура создает одну новость."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def news_id_for_args(news):
    """Фикстура возвращает id новости для подстановки в args."""
    return (news.id,)


@pytest.fixture
def news_detail_url(news):
    """Фикстура возвращает URL страницы детального просмотра новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def many_news():
    """Фикстура создает 11 новостей (на 1 больше лимита на главной)."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def author(django_user_model):
    """Фикстура создает автора комментария."""
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    """Фикстура создает читателя (не автора)."""
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    """Фикстура возвращает клиент с авторизованным автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Фикстура возвращает клиент с авторизованным читателем."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(author, news):
    """Фикстура создает комментарий к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comment_id_for_args(comment):
    """Фикстура возвращает id комментария для подстановки в args."""
    return (comment.id,)


@pytest.fixture
def many_comments(news, author):
    """Фикстура создает 10 комментариев с разными датами."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def edit_url(comment):
    """Фикстура возвращает URL страницы редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    """Фикстура возвращает URL страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_to_comments(news_detail_url):
    """Фикстура возвращает URL с якорем #comments."""
    return f'{news_detail_url}#comments'


@pytest.fixture
def form_data():
    """Фикстура возвращает данные для формы комментария."""
    return {'text': 'Текст комментария'}


@pytest.fixture
def bad_words_data():
    """Фикстура возвращает данные с запрещёнными словами."""
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def new_comment_text():
    """Фикстура возвращает новый текст для обновления комментария."""
    return {'text': 'Обновлённый комментарий'}
