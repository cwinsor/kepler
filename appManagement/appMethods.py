import os
import json, pathlib
from flask import jsonify
from engine import engine as eng

class AppMethods:
    """
    Provides access to REST endpoints of the functionality which is present in the application object 'app'.
    These methods are designed to work with a session object to maintain state.
    - the loading, parsing and analysis of the datafiles
    - provides a method to produce recommendations
    - lists the configurations which have been uploaded

    Parameters
    ----------
    sessions : object
        An instance of a class which is reponsible for managing session state

    Attributes
    ----------

    Methods
    -------
    recommend

    Raises
    ------
    ValueError

    Notes and Examples
    ------------------
    """

    sessions = None
    uploadFolder = None

    def __init__(self, sessions, uploadFolder):
        self.sessions = sessions
        self.uploadFolder = uploadFolder

    # ----
    # Load the configuration file specified by filename parameter, into the session, and parse and analyze the data files.
    # ----
    def loadAndParseInSession(self, sessionId, filename):
        session = self.sessions[sessionId]
        session.setFilename(filename)
        filename = os.getcwd()+self.uploadFolder+'/'+ filename
        content, isParsed = session.getConfigMgr().LoadAndParse(filename) 

        if (isParsed is True):
            recEngine = eng.Engine(session.getConfigMgr())
            session.setRecEngine(recEngine)
            recEngine.Execute() 

        return content

    # ----
    # Produces recommendations for the specified session and prompt
    # ----
    def configRecommend(self, sessionId, prompt):
        session = self.sessions[sessionId]        
        result, isRecommendSuccess = session.getRecEngine().Recommendation(prompt)
        return result.to_json(orient="split")

    # ----
    # Returns a list of .cfg files that are uploaded to the recommendation system
    # ----
    def listUploadedConfigurations(self):
        updir = os.getcwd()+self.uploadFolder
        os.makedirs(updir, exist_ok=True)  
        files = os.listdir(updir)

        config_files = []
        for f in files:
            file_extension = pathlib.Path(f).suffix
            if (file_extension == '.cfg'):
                config_files.append(f)

        return config_files