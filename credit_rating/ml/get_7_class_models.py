from transformers import (
    AutoTokenizer,
    BertForSequenceClassification,
)


def get_model_by_path(path):
    model = BertForSequenceClassification.from_pretrained(path)
    tokenizer = AutoTokenizer.from_pretrained(path, use_fast=True)

    return model, tokenizer
