import torch
import numpy as np
import random
import os

from preprocess import preprocess_names, pr_text_editing
from get_7_class_models import get_model_by_path
from predict import predict

from transformers_interpret import MultiLabelClassificationExplainer

def get_text():
    """
    Имитирует получение строки от Саши
    :return:  something
    """
    return "random string"


def seed_everything(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


if __name__ == '__main__':
    seed_everything(seed=42)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Чистка текста
    text = get_text()
    clear_text = pr_text_editing(text)
    clear_text = preprocess_names(clear_text)


    # ТОЛЬКО МОДЕЛИ НА 7 КЛАССОВ
    # sbert, sbert_tokenizer = get_model_by_path('sbert_nlu_7_class/checkpoint-548')
    labse, labse_tokenizer = get_model_by_path('labse_en_ru')

    """sbert_label = predict(
        model=sbert,
        tokenizer=sbert_tokenizer,
        text_to_predict=text
    )"""

    labse_label = predict(
        model=labse,
        tokenizer=labse_tokenizer,
        text_to_predict=text
    )

    # print(sbert_label, labse_label)
    """print('here 1')
    cls_explainer = MultiLabelClassificationExplainer(labse, labse_tokenizer)
    print('here 2')
    word_attributions = cls_explainer(
        "There were many aspects of the film I liked, but it was frightening and gross in parts. My parents hated it.")
    print('here 3')
    print(word_attributions)
    cls_explainer.visualize("multilabel_viz.html")"""
    print(labse_label)




