import numpy as np

from wordmodels.utils import transform_query, term_to_vector, index_to_term

def cosine_similarity_vectors(array1, array2):
    dot = np.inner(array1, array2)
    vec1_norm = np.linalg.norm(array1)
    vec2_norm = np.linalg.norm(array2)
    return dot / (vec1_norm * vec2_norm)

def cosine_similarity_matrix_vector(vector, matrix):
    dot = vector.dot(matrix)
    matrix_norms = np.linalg.norm(matrix, axis=0)
    vector_norm = np.linalg.norm(vector)
    matrix_vector_norms = np.multiply(matrix_norms, vector_norm)
    return dot / matrix_vector_norms

def term_similarity(wm, wm_type, term1, term2):
    matrix = wm[wm_type]

    if wm_type == 'svd_ppmi':
        transformer = wm['transformer']
        vocab = transformer.get_feature_names_out()
        vec1 = term_vector(matrix, vocab, term1)
        vec2 = term_vector(matrix, vocab, term2)

        if type(vec1) != type(None) and type(vec2) != type(None):
            return float(cosine_similarity_vectors(vec1, vec2))

    elif wm_type == 'word2vec':
        similarity = matrix.similarity(term1, term2)
        return str(similarity)

def term_vector(matrix, vocab, term):
    index = next(
        (i for i, a in enumerate(vocab)
         if a == term), None)
    if not(index):
        return None
    vec = matrix[:, index]
    return vec

def find_n_most_similar(wm, wm_type, query_term, n):
    """given a matrix of svd_ppmi or word2vec values
    and the transformer (i.e., sklearn CountVectorizer),
    determine which n terms match the given query term best
    """
    analyzer = wm['analyzer']
    vocab = wm['vocab']
    transformed_query = transform_query(query_term, analyzer)
    matrix = wm[wm_type]
    if wm_type == 'svd_ppmi':
        vec = term_to_vector(query_term, wm['transformer'], matrix)

        if type(vec) == type(None):
            return None

        similarities = cosine_similarity_matrix_vector(vec, matrix)
        sorted_sim = np.sort(similarities)
        most_similar_indices = np.where(similarities >= sorted_sim[-n])
        output_terms = [{
            'key': index_to_term(index, vocab),
            'similarity': similarities[index]
            } for index in most_similar_indices[0] if
            index_to_term(index, vocab)!=transformed_query
        ]
    elif wm_type == 'word2vec':
        try:
            results = matrix.most_similar(transformed_query, topn=n)
        except:
            return None
        output_terms = [{
            'key': result[0],
            'similarity': result[1]
        } for result in results]
    else:
        return None
    return output_terms


def similarity_with_top_terms(matrix, transformer, query_term, word_data, wm_type):
    """given a matrix of svd_ppmi values,
    the transformer (i.e., sklearn CountVectorizer), and a word list
    of the terms matching the query term best over the whole corpus,
    determine the similarity for each time interval
    """
    if wm_type == 'svd_ppmi':
        query_vec = term_to_vector(query_term, transformer, matrix)
        for item in word_data:
            item_vec = term_to_vector(item['label'], transformer, matrix)
            if type(item_vec) == type(None):
                value = 0
            else:
                value = cosine_similarity_vectors(item_vec, query_vec)
            item['data'].append(value)
    elif wm_type == 'word2vec':
        for item in word_data:
            value = matrix.similarity(query_term, item['label'])
            item['data'].append(value)
    return word_data
