from users.models import CustomUser, CustomAnonymousUser

def test_access_through_group(db, basic_mock_corpus, group_with_access):
    user = CustomUser.objects.create(username='nice-user', password='secret')
    user.groups.add(group_with_access)
    user.save()
    assert user.has_access(basic_mock_corpus)

def test_superuser_access(basic_mock_corpus, admin_user):
    assert admin_user.has_access(basic_mock_corpus)

def test_no_corpus_access(db, basic_mock_corpus):
    user = CustomUser.objects.create(username='bad-user', password='secret')
    assert not user.has_access(basic_mock_corpus)


def test_public_corpus_access(db, basic_corpus_public):
    user = CustomUser.objects.create(username='new-user', password='secret')
    assert user.has_access(basic_corpus_public)
    anon = CustomAnonymousUser()
    assert anon.has_access(basic_corpus_public)

def test_api_access(db, basic_mock_corpus, group_with_access, auth_client, auth_user):
    # default: no access
    response = auth_client.get('/api/corpus/')
    assert len(response.data) == 0

    # after adding group, access should be granted
    auth_user.groups.add(group_with_access)
    auth_user.save
    response = auth_client.get('/api/corpus/')
    assert len(response.data) == 1
    assert response.data[0].get('name') == basic_mock_corpus

def test_superuser_api_access(admin_client, basic_mock_corpus):
    response = admin_client.get('/api/corpus/')
    assert response.status_code == 200
    assert any(corpus['name'] == basic_mock_corpus for corpus in response.data)
