import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0].detach().cpu()
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def make_features_transformers(model_name, max_len, sentences):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).cuda()
    df_model = model_name.split('/')[1]
    text_features = []
    for sentence in sentences:
        encoded_input = tokenizer([sentence], padding='max_length', truncation=True, max_length=max_len,
                                  return_tensors='pt')
        with torch.no_grad():
            model_output = model(input_ids=encoded_input['input_ids'].cuda())
        sentence_embeddings = list(mean_pooling(model_output, encoded_input['attention_mask']).numpy())
        text_features.extend(sentence_embeddings)
    text_features_df = pd.DataFrame(text_features,
                                    columns=[f'{df_model}_pr_txt_parsed_feature_{i}' for i in range(len(text_features[0]))])
    return text_features_df
