from http import HTTPStatus

import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.usefixtures('many_news')
def test_news_count(client, home_url):
    """Проверяем количество новостей на главной странице."""
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('many_news')
def test_news_order(client, home_url):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('many_comments')
def test_comments_order(client, news_detail_url):
    """
    Комментарии на странице отдельной новости отсортированы
    от старых к новым: старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news_detail_url):
    """
    Анонимному пользователю не видна форма для отправки
    комментария на странице отдельной новости.
    """
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_detail_url):
    """
    Авторизованному пользователю видна форма для отправки
    комментария на странице отдельной новости.
    """
    response = author_client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
