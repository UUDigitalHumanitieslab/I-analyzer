import os

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

here = os.path.dirname(os.path.abspath(__file__))


def test_csv_upload(admin_client, json_mock_corpus):
    fp = os.path.join(here, 'files', 'example.csv')

    # Test file upload
    with open(fp, 'rb') as f:
        data = {'corpus': json_mock_corpus.pk, 'is_sample': True, 'file': f}
        res = admin_client.post('/api/corpus/datafiles/', data)
    assert res.status_code == HTTP_201_CREATED
    file_pk = res.data.get('id')

    # Test file info
    info_res = admin_client.get(f'/api/corpus/datafiles/{file_pk}/info/')
    assert info_res.status_code == HTTP_200_OK
    assert info_res.data == {
        'character': 'text',
        'line': 'text',
        'date-column': 'date',
        'FLOAT COLUMN': 'float',
        'int_column': 'integer',
        'bool column': 'boolean'
    }
