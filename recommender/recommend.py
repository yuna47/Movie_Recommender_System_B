from process_data import prepare_data, load_data


def prepare():
    try:
        tfidf_matrix, cosine_sim, indices, dataframe = load_data()
    except FileNotFoundError:
        print("Preparing data...")
        tfidf_matrix, cosine_sim, indices, dataframe = prepare_data('../movie_crawl/output/movie.csv')
    return cosine_sim, indices, dataframe


def recommend_list(movies):
    cosine_sim, indices, dataframe = prepare()
    recomm = set()

    for movie in movies:
        idx = indices[movie]

        # Get similarity scores for the selected movie
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]  # Exclude the movie itself from recommendations

        # Get indices of recommended movies
        movie_indices = [i[0] for i in sim_scores]

        # Add recommended movie indices to the set
        recomm.update(movie_indices)

        # Convert set to list and get the first 10 movies
    recomm = list(recomm)[:10]

    print('< 추천 영화 >')
    for i, idx in enumerate(recomm):
        print(f'{i + 1} : {dataframe["title"][idx]}')


def recommend(title):
    cosine_sim, indices, dataframe = prepare()
    recomm = []
    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:11]

    movie_indices = [i[0] for i in sim_scores]

    for i in range(10):
        recomm.append(dataframe['title'][movie_indices[i]])

    print('< 추천 영화 >')
    for i in range(10):
        print(str(i + 1) + ' : ' + recomm[i])


if __name__ == "__main__":
    # recommend('곤지암')
    recommend_list(['소름', '말아톤', '은교'])
    # recommend_list(['곤지암', '공작', '감기'])
    # recommend_list(['여고괴담 5', '부산행', '기생충'])
