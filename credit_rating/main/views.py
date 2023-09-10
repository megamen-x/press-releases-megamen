from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.core.cache import cache
from main.forms import *
from main.models import *
from ML.main import seed_everything
from ML.preprocess import preprocess_names, pr_text_editing
from ML.get_7_class_models import get_model_by_path
from ML.predict import predict
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import os
import csv
import openpyxl
import numpy as np
import warnings
import torch
warnings.filterwarnings('ignore')

from transformers_interpret import MultiLabelClassificationExplainer


def predict_rating(text: str):
    labse = cache.get('labse')
    labse_tokenizer = cache.get('labse_token')
    if labse is None:
        seed_everything(seed=42)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        labse, labse_tokenizer = get_model_by_path('credit_rating\ML\labse_en_ru')
        # sbert, sbert_tokenizer = get_model_by_path('credit_rating\ML\checkpoint-548')
        cache.set('labse', labse, None)
        cache.set('labse_token', labse_tokenizer, None)
    # Чистка текста
    clear_text = pr_text_editing(text)
    clear_text = preprocess_names(clear_text)
    labse_label = predict(
        model=labse,
        tokenizer=labse_tokenizer,
        text_to_predict=clear_text
    )
    # sbert_label = predict(
    #     model=sbert,
    #     tokenizer=sbert_tokenizer,
    #     text_to_predict=text
    # )
    # cls_explainer = MultiLabelClassificationExplainer(labse, labse_tokenizer)
    # word_attributions = cls_explainer(
    #     "There were many aspects of the film I liked, but it was frightening and gross in parts. My parents hated it.")
    # cls_explainer.visualize("multilabel_viz.html")
    return ('sbert_label', labse_label, ['first', 'second', 'hren znaet chto'])


def read_csv(file: str) -> list:
    with open(file, errors='ignore', mode='r') as f:
        # encoding='cp1251'
        reader = csv.reader(f)
        next(reader)
        file_content = [''.join(row) for row in reader]
    return file_content

def read_excel(file: str) -> list:
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active
    file_content = [row for row in sheet.iter_rows(values_only=True)]
    return file_content

def read_txt(file: str) -> list:
    with open(file, errors='ignore', mode='r') as f:
        # encoding='cp1251'
        file = f.readlines()
    return file

def slider(request):
    return render(request, 'main/mmtslider.html', context={'title': 'Справка (MMT)'})

def megamen(request):
    return render(request, 'main/mmtmegamen.html', context={'title': 'Наша команда (MMT)'})

def page404(request):
    return render(request, 'main/404.html')

class RatingView(View):
    context = {'title': 'Ввод (MMT)'}

    def get(self, request):
        self.context['form'] = RatingForm()
        self.context['ans_detailed'] = None
        self.context['ans_simple'] = None
        self.context['key_words'] = None
        return render(request, 'main/mmtfilescreen.html', context=self.context)

    @method_decorator(login_required)
    def post(self, request):
        form_text = RatingForm(request.POST, request.FILES)
        if form_text.is_valid():
            object = form_text.save(commit=False)
            object.user = request.user
            object.save()
            object = InputFile.objects.filter(user=request.user).latest('id')
            match object.file.path[-4:]:
                case '.csv':
                    list_address = read_csv(object.file.path)
                case 'xlsx':
                    list_address = read_excel(object.file.path)
                case '.txt':
                    list_address = read_txt(object.file.path)
            if len(list_address) == 1:
                ans_det, ans_sim, key_words = predict_rating(list_address[0])
                rating = Rating.objects.create(user=request.user, answer_detalized=ans_det, answer_simplified=ans_sim, text=list_address[0])
                self.context['ans_detailed'] = ans_det
                self.context['ans_simple'] = ans_sim
                self.context['key_words'] = None
                for el in key_words:
                    rating.keywords_set.create(construction=el)
                return render(request, 'main/mmtfilescreen.html', context=self.context)
            else:
                for i in range(len(list_address)):
                    ans_det, ans_sim, key_words = predict_rating(list_address[i])
                    rating = Rating.objects.create(user=request.user, answer_detalized=ans_det, answer_simplified=ans_sim, text=list_address[i])
                    list_address[i] = '; '.join([ans_det, ans_sim]) + '; ' + str(key_words) + "\n"
                response = HttpResponse(
                list_address, content_type=f'application/{object.output_format}')
                response['Content-Disposition'] = f'attachment; filename="answer.{object.output_format}"'
                return response
        else:
            return render(request, 'main/404.html', context=self.context)
