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
    return ('YEEEEEEEEEEES', ['first', 'second', 'hren znaet chto'])


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


def slider(request):
    return render(request, 'main/mmtslider.html', context={'title': 'Справка (MMT)'})


def megamen(request):
    return render(request, 'main/mmtmegamen.html', context={'title': 'Наша команда (MMT)'})

def page404(request):
    return render(request, 'main/404.html')


class RatingView(View):
    context = {'title': 'Текстовый ввод (MMT)'}

    def get(self, request):
        form_text = RatingForm()
        self.context['form_text'] = form_text
        self.context['result'] = None
        return render(request, 'main/mmttextscreen.html', context=self.context)

    def post(self, request):
        form_text = RatingForm(request.POST)
        if form_text.is_valid():
            object = form_text.save(commit=False)
            if request.user.is_authenticated:
                object.user = request.user
            ans, key_words = predict_rating(object.text)
            object.answer = ans
            object.save()
            self.context['answer'] = ans
            self.context['key_words'] = key_words
            for el in key_words:
                object.keywords_set.create(word=el)
            print(self.context['answer'], self.context['key_words'])
            return render(request, 'main/mmttextscreen.html', context=self.context)
        else:
            return render(request, 'main/mmttextscreen.html', context=self.context)


class RatingFileView(View):
    context = {'title': 'Работа с файлами (MMT)'}

    def get(self, request):
        form_file = RatingFileForm()
        self.context['form_file'] = form_file
        self.context['object'] = None
        return render(request, 'main/mmtfilescreen.html', context=self.context)

    @method_decorator(login_required)
    def post(self, request):
        form_file = RatingFileForm(request.POST, request.FILES)
        if form_file.is_valid():
            input_request = form_file.save(commit=False)
            input_request.user = request.user
            input_request.save()
            output_request = RatingFile.objects.filter(
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
            with open('tmp.csv', errors='ignore', mode='w') as file:
                writer = csv.writer(file)
                writer.writerows(list_address)
                output_request.corrected_file = file
                output_request.save(update_fields=['corrected_file'])
            response = HttpResponse(
                list_address, content_type=f'application/{format_file}')
            response['Content-Disposition'] = f'attachment; filename="answer.{format_file}"'
            return response
        else:
            return render(request, 'main/404.html', context=self.context)
