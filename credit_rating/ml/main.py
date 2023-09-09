import torch
import numpy as np
import pandas as pd
import random
import os
import pickle

from catboost import CatBoostClassifier

from regex import *
from get_features import make_features_transformers


def string_from_sasha():
    return 'hello'


def seed_everything(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


if __name__ == '__main__':
    seed_everything(seed=42)

    models = [
        ('sberbank-ai/sbert_large_nlu_ru', 512),
        ('sberbank-ai/sbert_large_mt_nlu_ru', 512),
        ('cointegrated/rubert-tiny2', 2048),
        ('cointegrated/LaBSE-en-ru', 512),
    ]

    user_input = string_from_sasha()
    user_input = pr_text_editing(user_input)
    user_input = preprocess_names(user_input)

    embeddings = pd.DataFrame()

    for m in models:
        embeddings = embeddings.join(make_features_transformers(m[0], m[1], user_input))

    with (open("features_name", "rb")) as openfile:
        feature_names = pickle.load(openfile)


    model = CatBoostClassifier()
    model.load_model('catboost_classifier')
    pred = model.predict(embeddings)


