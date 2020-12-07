from django.contrib import messages
from django.shortcuts import render
from .models import *
from docxtpl import DocxTemplate
from django.db.models import Q
from .forms import *
from django.views import View
from petrovich.main import Petrovich
from petrovich.enums import Case, Gender
from num2words import num2words
from django.utils import dateformat
from django.utils import timezone
import re
import math
import os


def case_fio(case, gender, first_name=None, second_name=None, last_name=None, return_type=0):
    p = Petrovich()
    if first_name:
        first_name = p.firstname(first_name, case, gender)
    if second_name:
        second_name = p.middlename(second_name, case, gender)
    if last_name:
        last_name = p.lastname(last_name, case, gender)
    if return_type == 0:
        return first_name, second_name, last_name
    elif return_type == 1:
        return ' '.join(filter(None, (last_name, first_name, second_name)))


def make_non_breaking_spaces(string):
    splitted_strings = string.split(', ')
    non_breaking_strings = []
    for string in splitted_strings:
        non_breaking_strings.append(string.replace(' ', '&#160;', 1))
    return ', '.join(non_breaking_strings)


class PretensionsFormView(View):
    form = PretensionForm
    template_name = 'pretensions/pretensions_form.html'
    today = timezone.now().date()
    current_key_rate = KeyRate.objects.filter(Q(end_date__isnull=True) | Q(end_date__gte=today),
                                              Q(start_date__lte=today), Q(removed_at__isnull=True)).first()

    def get(self, request):
        return render(request, self.template_name, {'form': self.form(), 'current_key_rate': self.current_key_rate,
                                                    'today': self.today})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if (not self.current_key_rate and cleaned_data['is_without_peni']) or self.current_key_rate:

                # BUYER
                buyer_sex = Gender.MALE if cleaned_data['buyer_sex'] == 'M' else Gender.FEMALE
                pretension_to_who = case_fio(Case.DATIVE, buyer_sex, last_name=cleaned_data['buyer_last_name'])[2] + \
                                    ' ' + cleaned_data['buyer_first_name'][0] + \
                                    ('.' + cleaned_data['buyer_second_name'][0] + '.' if cleaned_data[
                                        'buyer_second_name'] else '')
                hello_prefix = 'ый' if buyer_sex == Gender.MALE else 'ая'
                contract_with_who = case_fio(Case.INSTRUMENTAL, buyer_sex, cleaned_data['buyer_first_name'],
                                             cleaned_data['buyer_second_name'], cleaned_data['buyer_last_name'],
                                             return_type=1)

                # STUDENT
                if cleaned_data['is_buyer_student_same']:
                    education_to_who = 'Вам'
                    education_who = 'Вы были отчислены'
                else:
                    student_sex = Gender.MALE if cleaned_data['student_sex'] == 'M' else Gender.FEMALE
                    education_to_who = case_fio(Case.DATIVE, student_sex, cleaned_data['student_first_name'],
                                                cleaned_data['student_second_name'], cleaned_data['student_last_name'],
                                                return_type=1)
                    education_who = ' '.join(filter(None, (cleaned_data['student_last_name'],
                                                           cleaned_data['student_first_name'],
                                                           cleaned_data['student_second_name']))) + \
                                    ' был отчислен' if student_sex == Gender.MALE else ' была отчислена'

                # OTCH REASON
                if cleaned_data['otch_reason'] == 'initiative':
                    otch_reason = 'по инициативе Обучающегося'
                elif cleaned_data['otch_reason'] == 'academic_debt':
                    otch_reason = 'за невыполнение обязанностей по добросовестному освоению образовательной ' \
                                  'программы и выполнению учебного плана'
                elif cleaned_data['otch_reason'] == 'money_debt':
                    otch_reason = 'за неисполнение условий п. 3.2 и п. 3.3 Договора'
                elif cleaned_data['otch_reason'] == 'vuz_change':
                    otch_reason = 'в связи с переводом для продолжения освоения образовательной программы в ' + \
                                  cleaned_data['another_vuz']
                elif cleaned_data['otch_reason'] == 'other':
                    otch_reason = 'в связи с ' + cleaned_data['other_text']
                else:
                    otch_reason = 'WRONG TOKEN SPECIFIED'

                # DEBT
                whole_debt = int(float(cleaned_data['debt_sum']))
                whole_debt_string = str(num2words(int(float(cleaned_data['debt_sum'])), lang='ru'))
                frac_debt = int("{:.2f}".format(cleaned_data['debt_sum']).split('.')[1])

                # DOCX FILLING
                doc = DocxTemplate(os.path.join(os.path.dirname(__file__),
                                                "docx_templates/Template_pretension_2020_12_07.docx"))
                context = {'name_to': pretension_to_who,
                           'address_first_line': make_non_breaking_spaces(cleaned_data['address_first_line']),
                           'address_second_line': make_non_breaking_spaces(cleaned_data['address_second_line']),
                           'postal_code': cleaned_data['postal_code'], 'hello_prefix': hello_prefix,
                           'buyer_io': ' '.join(filter(None, (cleaned_data['buyer_first_name'],
                                                              cleaned_data['buyer_second_name']))),
                           'contract_date': dateformat.format(cleaned_data['contract_date'], '«d» E Y года'),
                           'contract_with_who': contract_with_who, 'contract_number': cleaned_data['contract_number'],
                           'education_to_who': education_to_who, 'edu_name': cleaned_data['specialty'].spec_name,
                           'prikaz_date': cleaned_data['prikaz_date'].strftime('%d.%m.%Y'),
                           'prikaz_number': cleaned_data['prikaz_number'], 'otch_who': education_who,
                           'otch_date': cleaned_data['otch_date'].strftime('%d.%m.%Y'), 'otch_why': otch_reason,
                           'send_date': cleaned_data['send_date'].strftime('%d.%m.%Y'), 'whole_debt_sum': whole_debt,
                           'whole_debt_sum_string': whole_debt_string, 'frac_debt_sum': str(frac_debt).zfill(2)}

                # PENI
                if cleaned_data['is_without_peni']:
                    context.update({'with_peni': False})
                else:
                    debt_days = (cleaned_data['send_date'] - cleaned_data['debt_date']).days
                    penalties = math.floor(cleaned_data['debt_sum'] * self.current_key_rate.key_rate / 100 *
                                           self.current_key_rate.part_key_rate_to_float() * debt_days * 100) / 100.0
                    context.update({'with_peni': True, 'key_rate': "{:.2f}".format(self.current_key_rate.key_rate),
                                    'part_key_rate_string': self.current_key_rate.peni_part_key_rate,
                                    'debt_sum': "{:.2f}".format(cleaned_data['debt_sum']),
                                    'debt_date': cleaned_data['debt_date'].strftime('%d.%m.%Y'),
                                    'debt_days': debt_days, 'penalties': "{:.2f}".format(penalties),
                                    'debt_sum_with_penalties': "{:.2f}".format(cleaned_data['debt_sum'] + penalties),
                                    'whole_debt_sum_with_penalties': int(cleaned_data['debt_sum'] + penalties),
                                    'whole_debt_sum_with_penalties_string':
                                        str(num2words(int(cleaned_data['debt_sum'] + penalties), lang='ru')),
                                    'frac_debt_sum_with_penalties':
                                        int("{:.2f}".format(cleaned_data['debt_sum'] + penalties).split('.')[1])})

                # PERFORMER AND DIRECTOR SIGNATURE
                context.update({'performer_fio': cleaned_data['performer'].__str__(),
                                'performer_post': cleaned_data['performer'].position.lower(),
                                'performer_phone': re.sub(r'8(\d{3})(\d{3})(\d{2})(\d{2})', r'8 (\1) \2-\3-\4',
                                                          cleaned_data['performer'].phone_number),
                                'director_post': cleaned_data['director'].position,
                                'director_sign_fio': cleaned_data['director'].get_sign_name()})

                # DOC RENDER AND SAVE
                doc.render(context)
                doc_filename = cleaned_data['buyer_last_name'] + '_' + cleaned_data['buyer_first_name'][0] + \
                               (cleaned_data['buyer_second_name'][0] if cleaned_data['buyer_second_name'][0] else '')
                if not cleaned_data['is_buyer_student_same']:
                    doc_filename += cleaned_data['student_last_name'] + '_' + cleaned_data['student_first_name'][0] + \
                                    (cleaned_data['student_second_name'][0] if cleaned_data['student_second_name'][0]
                                     else '')
                doc_filename = "".join([x if x.isalnum() else "_"
                                        for x in doc_filename + '_' + cleaned_data['contract_number']]) + '.docx'
                full_doc_path = os.path.join(settings.MEDIA_ROOT, settings.PRETENSIONS_DIR, doc_filename)
                doc.save(full_doc_path)

                form.save(commit=False)
                form.creator = request.user.pk
                form.pretension_file = full_doc_path
                form.save()

                return render(request, self.template_name, {'form': form, 'current_key_rate': self.current_key_rate,
                                                            'today': self.today,
                                                            'filename': 'pretensions_docx/' + doc_filename})
            else:
                messages.error(request, "Значение ключевой ставки ЦБ РФ неактуально. "
                                        "Обратитесь к администратору системы.")
                return render(request, self.template_name, {'form': form})
        else:
            return render(request, self.template_name, {'form': form})
