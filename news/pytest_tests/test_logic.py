from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


@pytest.mark.usefixtures('news')
def test_anonymous_user_cant_create_comment(
    client, news_detail_url, form_data
):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(news_detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.usefixtures('news')
def test_user_can_create_comment(
    author_client, news_detail_url, form_data, author, news
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(news_detail_url, data=form_data)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)

    comments_count = Comment.objects.count()
    assert comments_count == 1

    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.usefixtures('news')
def test_user_cant_use_bad_words(
    author_client, news_detail_url, bad_words_data
):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    response = author_client.post(news_detail_url, data=bad_words_data)

    form = response.context['form']
    assertFormError(form, 'text', WARNING)

    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.usefixtures('comment')
def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND

    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.usefixtures('comment')
def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.usefixtures('comment')
def test_author_can_edit_comment(
    author_client, edit_url, new_comment_text, url_to_comments, comment
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(edit_url, data=new_comment_text)
    assertRedirects(response, url_to_comments)

    comment.refresh_from_db()
    assert comment.text == new_comment_text['text']


@pytest.mark.usefixtures('comment')
def test_user_cant_edit_comment_of_another_user(
    reader_client, edit_url, new_comment_text, comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = reader_client.post(edit_url, data=new_comment_text)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
