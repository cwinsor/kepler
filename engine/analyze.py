import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from appManagement import analyzeInstructions as ai
from appManagement import configMgr 

class Analyze:
    """
    Provides the engine with data analysis capability, specifically:
    - vectorization of column data
    - combining vectorization output
    - processing similarity

    Parameters
    ----------
    configMgr : object
        An instance of a class which is reponsible for identifying the configuration 
        to use for recommendations
    workingDataFile: object
        An instance of the data file from which ETL has already been performed

    Attributes
    ----------

    Methods
    -------
    TransformDataFile
    MergeDataFiles

    Raises
    ------

    Notes and Examples
    ------------------
    """

    # ---
    # Performs the analysis of the supplied data.
    # ---
    def VectorizeAndSimilarity(self, configMgr, workingDatafile):
        
        matrixlist = []
        for vec in configMgr.analyze.vectorizers:

            if vec.vectorizerName == 'count':
                vec.vectorizer = CountVectorizer(stop_words=vec.stopWords)
                vec.matrix = vec.vectorizer.fit_transform(workingDatafile.data[vec.column])
                matrixlist.append(vec.matrix)
                pass

            if vec.vectorizerName == 'tfidf':
                vec.vectorizer = TfidfVectorizer(stop_words=vec.stopWords)
                vec.matrix = vec.vectorizer.fit_transform(workingDatafile.data[vec.column])
                matrixlist.append(vec.matrix)
                pass

            # otherwise- issue an error, unknown vectorizer

        #stack sparse matrix
        if configMgr.analyze.sparseStack[0].stackType == "hstack":
            sparse = sp.hstack(matrixlist, format=configMgr.analyze.sparseStack[0].stackFormat)

        #similarity
        #TODO: this similarity function should be identified by the configuration... it's hardwired and shouldn't be
        self.similarity = cosine_similarity(sparse, sparse)

        return self.similarity

    # ---
    # Given a request, returns the associate recommendation or empty set.
    # ---
    def Recommend(self, configMgr, workingData, columnName, request):

        indices = pd.Series(workingData.index, index = workingData[columnName])
        try:
            index = indices[request]
        except Exception as ex:
            return pd.DataFrame([]), False

        sim_scores = list(enumerate(self.similarity[index]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:configMgr.recommend.responseCount+1]
        
        movie_indices = [i[0] for i in sim_scores]

        responseColumns = []
        response = {}
        for column in configMgr.recommend.responseColumns:
            response[column.sourceColumn] = workingData[column.sourceColumn].iloc[movie_indices]
            responseColumns.append(column.outputColumn)

        recommendation_data = pd.DataFrame(columns=responseColumns)

        for column in configMgr.recommend.responseColumns:
            recommendation_data[column.outputColumn] = response[column.sourceColumn]

        return recommendation_data, True        
