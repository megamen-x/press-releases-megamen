from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.core.cache import cache
from main.forms import *
from main.models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import os
import csv
import openpyxl
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
#model_path = os.path.join('credit_rating', 'ML', 'model.pt')


def predict_rating(text: str):
    # model = cache.get('model')
    # if model is None:
    #     model = Model(model_path)
    #     cache.set('model', model, None)
    return ('YEEEEEEEEEEES', 'nooooooooooo', ['first', 'second', 'hren znaet chto'])


def read_csv(file: str) -> list:
    with open(file, errors='ignore', mode='r') as f:
        # encoding='cp1251'
        reader = csv.reader(f)
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
                self.context['key_words'] = key_words
                for el in key_words:
                    rating.keywords_set.create(word=el)
                return render(request, 'main/mmtfilescreen.html', context=self.context)
            else:
                print(object.output_format)
                for i in range(len(list_address)):
                    ans_det, ans_sim, key_words = predict_rating(list_address[i])
                    rating = Rating.objects.create(user=request.user, answer_detalized=ans_det, answer_simplified=ans_sim, text=list_address[i])
                    list_address[i] = '; '.join([ans_det, ans_sim, *key_words]) + "\n"
                response = HttpResponse(
                list_address, content_type=f'application/{object.output_format}')
                response['Content-Disposition'] = f'attachment; filename="answer.{object.output_format}"'
                return response
        else:
            return render(request, 'main/404.html', context=self.context)


class RatingFileView(View):
    context = {'title': 'Работа с файлами (MMT)'}

    def get(self, request):
        form_file = RatingForm()
        self.context['form_file'] = form_file
        self.context['object'] = None
        return render(request, 'main/mmtfilescreen.html', context=self.context)

    @method_decorator(login_required)
    def post(self, request):
        form_file = RatingForm(request.POST, request.FILES)
        if form_file.is_valid():
            input_request = form_file.save(commit=False)
            input_request.user = request.user
            input_request.save()
            output_request = InputFile.objects.filter(
                user=request.user).latest('id')
            format_file = output_request.file.path[-3:]
            match format_file:
                case 'csv':
                    list_address = read_csv(output_request.file.path)
                case 'xls' | 'lsx':
                    list_address = read_excel(output_request.file.path)
                case _:
                    return render(request, 'main/404.html', context=self.context)
            for i in range(len(list_address)):
                list_address[i] = predict_rating(list_address[i])
            response = HttpResponse(
                list_address, content_type=f'application/{format_file}')
            response['Content-Disposition'] = f'attachment; filename="answer.{format_file}"'
            return response
        else:
            return render(request, 'main/404.html', context=self.context)
