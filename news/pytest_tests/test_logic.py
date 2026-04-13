from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Текст комментария'}
NEW_COMMENT_TEXT = {'text': 'Обновлённый комментарий'}


@pytest.mark.usefixtures('news')
def test_anonymous_user_cant_create_comment(client, news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_before = Comment.objects.count()
    client.post(news_detail_url, data=FORM_DATA)
    comments_after = Comment.objects.count()
    assert comments_before == comments_after


def test_user_can_create_comment(author_client, news_detail_url, author, news):
    """Авторизованный пользователь может отправить комментарий."""
    comments_before = Comment.objects.count()
    response = author_client.post(news_detail_url, data=FORM_DATA)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)

    comments_after = Comment.objects.count()
    assert comments_after == comments_before + 1

    comment = Comment.objects.latest('id')
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.usefixtures('news')
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news_detail_url, bad_word):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    comments_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(news_detail_url, data=bad_words_data)

    comments_after = Comment.objects.count()
    assert comments_before == comments_after

    form = response.context['form']
    assertFormError(form, 'text', WARNING)


@pytest.mark.usefixtures('comment')
def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND

    comments_after = Comment.objects.count()
    assert comments_after == comments_before - 1


@pytest.mark.usefixtures('comment')
def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_before = Comment.objects.count()
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_after = Comment.objects.count()
    assert comments_after == comments_before


def test_author_can_edit_comment(
    author_client, edit_url, url_to_comments, comment
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(edit_url, data=NEW_COMMENT_TEXT)
    assertRedirects(response, url_to_comments)

    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == NEW_COMMENT_TEXT['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    reader_client, edit_url, comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = reader_client.post(edit_url, data=NEW_COMMENT_TEXT)
    assert response.status_code == HTTPStatus.NOT_FOUND

    not_updated_comment = Comment.objects.get(id=comment.id)
    assert not_updated_comment.text == comment.text
    assert not_updated_comment.author == comment.author
    assert not_updated_comment.news == comment.news
