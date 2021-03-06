from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import f1_score
from sklearn.model_selection import ParameterGrid
from tqdm import tqdm

import pickle
import os
import json

class MLModel:
    def __init__(self, X, y, model_name):
        self.X = X
        self.y = y
        self.model_name = model_name
        self.parameters = None
        self.load_model()
        self.vectorize()
        os.makedirs(f'results/{model_name}', exist_ok=True)

    def vectorize(self):
        if os.path.isfile('vectorizer.h5'):
            with open('vectorizer.h5', 'rb') as f:
                self.vectorizer = pickle.load(f)
            self.X = self.vectorizer.transform(self.X)
            return

        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(self.X)        
        filename = 'vectorizer.h5'
        with open(filename, 'wb') as f:
            pickle.dump(self.vectorizer, f)

    def save_best_params(self):
        filename = f'results/{self.model_name}/{self.model_name}_best_params.json'
        with open(filename, 'w') as f:
            json.dump(self.best_params, f)

    def load_best_params(self):
        filename = f'results/{self.model_name}/{self.model_name}_best_params.json'
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                self.best_params = json.load(f)

    def save_model(self):
        filename = f'results/{self.model_name}/{self.model_name}.h5'
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f)

    def load_model(self):
        filename = f'results/{self.model_name}/{self.model_name}.h5'

        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                self.model = pickle.load(f)

    def save_cv_results(self):
        filename = f'results/{self.model_name}/{self.model_name}_cv_results.json'
        with open(filename, 'w') as f:
            json.dump({'results':self.cv_results.tolist()}, f)
        
    def GridSearch(self):
        best_model, best_score = None, 0

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        for train_index, test_index in skf.split(self.X, self.y):
            break

        grid_search = ParameterGrid(self.parameters)
        for params in tqdm(grid_search):
            model = self.model.set_params(**params)
            model.fit(self.X[train_index], self.y[train_index])
            score = f1_score(self.y[test_index], model.predict(self.X[test_index]), average='macro')
            if score > best_score:
                best_model = model
                best_score = score

        self.model = best_model

    def train(self):
        self.GridSearch()
        self.save_model()

        self.cv_results = cross_val_score(self.model, self.X, self.y, cv=10, scoring='f1_macro', n_jobs=-1, verbose=4)
        self.save_cv_results()