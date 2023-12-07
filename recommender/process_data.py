import re
import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

okt = Okt()


def sub_special(text):
    return re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣0-9a-zA-Z]', ' ', text)


def normalize(text):
    tokens = okt.morphs(text)
    return ' '.join(tokens)


def process_dataframe(dataframe):
    dataframe["actor"] = dataframe["actor"].fillna('')
    dataframe["genre"] = dataframe["genre"].apply(sub_special)
    dataframe["director"] = dataframe["director"].apply(sub_special)
    dataframe["actor"] = dataframe["actor"].apply(sub_special)
    dataframe["synopsis"] = dataframe["synopsis"].apply(sub_special)

    dataframe["synopsis"] = dataframe["synopsis"].apply(normalize)

    dataframe["text"] = dataframe["title"] + " " + dataframe["genre"] + " " + dataframe["director"] + " " + 2 * dataframe["synopsis"]

    return dataframe


def generate_tfidf_matrix(dataframe):
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(dataframe["text"])
    return tfidf_matrix, tfidf


def generate_cosine_sim(tfidf_matrix):
    return linear_kernel(tfidf_matrix, tfidf_matrix)


def generate_indices(dataframe):
    return pd.Series(dataframe.index, index=dataframe['title']).drop_duplicates()


def prepare_data(file_path):
    dataframe = process_dataframe(pd.read_csv(file_path))
    tfidf_matrix, tfidf = generate_tfidf_matrix(dataframe)
    cosine_sim = generate_cosine_sim(tfidf_matrix)
    indices = generate_indices(dataframe)

    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
    cosine_sim_df = pd.DataFrame(cosine_sim, index=dataframe.index, columns=dataframe.index)

    tfidf_df.to_pickle('tfidf_matrix.pkl')
    cosine_sim_df.to_pickle('cosine_sim.pkl')
    indices.to_pickle('indices.pkl')
    dataframe.to_pickle('dataframe.pkl')

    return tfidf_matrix, cosine_sim, indices, dataframe


def load_data():
    tfidf_matrix = pd.read_pickle('tfidf_matrix.pkl')
    cosine_sim = pd.read_pickle('cosine_sim.pkl')
    indices = pd.read_pickle('indices.pkl')
    dataframe = pd.read_pickle('dataframe.pkl')

    return tfidf_matrix, cosine_sim, indices, dataframe
