from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, permission_required
from formtools.wizard.views import SessionWizardView
from .forms import *
from .models import *
from specialist.models import Specialist
import datetime
from django.utils import timezone
import json
from django.contrib import messages
from django.db.models.functions import Concat
from django.db.models import Value as V, Count
from django.db.models import Prefetch
from constance import config
import re

FORMS = [
    ('user', RequestFormUser),
    ('university_subject', RequestFormSubjectUniversity),
    ('hostel_subject', RequestFormSubjectHostel),
]

TEMPLATES = {
    'user': 'dogovor_query/request_templates/user_form.html',
    'university_subject': 'dogovor_query/request_templates/university_form_subject.html',
    'hostel_subject': 'dogovor_query/request_templates/hostel_form_subject.html',
}


def split_fio(fio):
    splitted_fio = fio.split(' ')
    if len(splitted_fio) > 2:
        second_name = ' '.join(splitted_fio[2:])
    else:
        second_name = None
    return {'last_name': splitted_fio[0], 'first_name': splitted_fio[1], 'second_name': second_name}


def main_page(request):
    if (timezone.now().strftime('%A').lower() in config.EXCLUDE_WEEKDAYS) or \
            timezone.now().time() < config.TIME_OPENING or \
            timezone.now().time() > config.TIME_CLOSING:
        return render(request, 'dogovor_query/reseption_closed.html',
                      {'config': config, 'weekdays': [('ПН', 'monday'), ('ВТ', 'tuesday'), ('СР', 'wednesday'),
                                                      ('ЧТ', 'thursday'), ('ПТ', 'friday'), ('СБ', 'saturday'),
                                                      ('ВС', 'sunday')]})
    response = RequestWizard.as_view()(request)
    if 'user_uid' in request.COOKIES:
        try:
            user = User.objects.get(user_uid=request.COOKIES['user_uid'], removed_at__isnull=True)
        except Exception as e:
            print(e)
            response = redirect('main_page')
            response.delete_cookie('user_uid')
            return response
        user_request = Request.objects.filter(user=user, removed_at__isnull=True,
                                              created_at__date=timezone.now().date())
        if user_request:
            user_request = user_request.latest()
            user_request_status = user_request.requestlog_set
            if user_request_status:
                user_request_status = user_request_status.latest()
                if user_request_status.status in ['created', 'activated', 'processing', 'postponed']:
                    response = render(request, 'dogovor_query/user_waiting.html')
    return response


def api_query_position(request):
    response = {'user_uid': '', 'query_number': '', 'current_status': '', 'people_before': ''}
    if 'user_uid' in request.COOKIES:
        user = get_object_or_404(User, user_uid=request.COOKIES['user_uid'], removed_at__isnull=True)
        response['user_uid'] = request.COOKIES['user_uid']
        user_request = Request.objects.filter(user=user, removed_at__isnull=True,
                                              created_at__date=timezone.now().date())
        if user_request:
            user_request = user_request.latest()
            user_request_status = user_request.requestlog_set.latest()
            request_logs = RequestLog.objects.filter(removed_at__isnull=True, created_at__date=timezone.now().date()) \
                .order_by('request_id', '-created_at').distinct('request')

            people_before_amount = RequestLog.objects.filter(pk__in=request_logs,
                                                             status__in=['created', 'processing', 'activated'],
                                                             request__created_at__lte=user_request.created_at).count()
            response['fio'] = user.__str__()
            if user_request_status.specialist:
                response['room'] = user_request_status.specialist.room
                response['table_number'] = user_request_status.specialist.table_number
                response['specialist_name'] = user_request_status.specialist.get_full_name()
            response['query_number'] = user_request.get_query_number()
            response['current_status'] = user_request_status.status
            response['people_before'] = max(people_before_amount - 1, 0)
    return HttpResponse(json.dumps(response))


def user_cancel_request(request):
    response = {'user_uid': '', 'query_number': '', 'current_status': '', 'changed': False}
    status = 400
    if 'user_uid' in request.COOKIES:
        user = get_object_or_404(User, user_uid=request.COOKIES['user_uid'], removed_at__isnull=True)
        response['user_uid'] = request.COOKIES['user_uid']
        user_request = Request.objects.filter(user=user, removed_at__isnull=True,
                                              created_at__date=timezone.now().date())
        if user_request:
            user_request = user_request.latest()
            user_request_status = user_request.requestlog_set.latest()
            response['query_number'] = user_request.get_query_number()
            if user_request_status.status in ['created', 'postponed']:
                new_status = RequestLog(request=user_request, status='cancelled')
                new_status.save()
                response['changed'] = True
                status = 201
            else:
                status = 403
            response['current_status'] = user_request_status.status
    return HttpResponse(json.dumps(response), status=status)


@login_required(login_url='specialist_login')
def index(request):
    context = {}
    request_types = {request_type[0]: request_type[1] for request_type in Request.RequestTypes.choices}

    statuses = ['activated', 'processing']

    all_request_logs = RequestLog.objects.filter(removed_at__isnull=True, created_at__date=timezone.now().date(),
                                                 specialist=request.user). \
        order_by('request_id', '-created_at').distinct('request')
    current_request_log = RequestLog.objects.filter(pk__in=all_request_logs).filter(status__in=statuses). \
        select_related('request', 'request__user')

    if current_request_log:
        current_request_log = current_request_log[0]
        context['request_id'] = current_request_log.request_id
        context['query_number'] = current_request_log.request.get_query_number()
        context['status_created_at'] = current_request_log.created_at.strftime('%d.%m.%Y %H:%M:%S')
        context['status'] = current_request_log.status
        context['fio'] = current_request_log.request.user.__str__()
        context['birthday'] = current_request_log.request.user.birthday.strftime('%d.%m.%Y')
        context['phone_number'] = current_request_log.request.user.phone_number
        context['request_type'] = request_types[current_request_log.request.type]
        context['request_question'] = current_request_log.request.question
        context['notes'] = ';'.join([note.text for note in current_request_log.request.note_set.all()])
    return render(request, 'dogovor_query/manager_query_list.html', context)


@login_required(login_url='specialist_login')
def add_note(request):
    response = {'request_id': '', 'specialist_id': '', 'note_text': '', 'created_at': ''}
    status = 400
    if 'request_id' in request.GET and 'note_text' in request.GET:
        response['request_id'] = request.GET['request_id']
        response['note_text'] = request.GET['note_text']
        response['specialist_id'] = request.user.pk
        try:
            user_request = Request.objects.get(pk=request.GET['request_id'])
        except Request.DoesNotExist:
            return HttpResponse(json.dumps(response), content_type='application/json', status=status)
        new_note = Note(request=user_request, specialist=request.user, text=request.GET['note_text'])
        new_note.save()
        response['created_at'] = new_note.created_at.strftime('%d.%m.%Y %H:%M:%S')
        status = 200
    return HttpResponse(json.dumps(response), content_type='application/json', status=status)


@login_required(login_url='specialist_login')
@permission_required('dogovor_query.view_query', raise_exception=True)
def get_requests(request):
    request_types = {request_type[0]: request_type[1] for request_type in Request.RequestTypes.choices}
    if 'response_type' in request.GET:
        response_type = request.GET['response_type']
    else:
        response_type = 'clean'
    if 'status' in request.GET:
        statuses = request.GET['status'].split('_')
    else:
        statuses = RequestLog.RequestStatus.values

    if 'start_date' in request.GET:
        start_date = generate_start_end_date(request.GET['start_date'], 'start')
        if start_date is None:
            return HttpResponseBadRequest()
    else:
        start_date = datetime.date.min

    if 'end_date' in request.GET:
        end_date = generate_start_end_date(request.GET['end_date'], 'end')
        if end_date is None:
            return HttpResponseBadRequest()
    else:
        end_date = timezone.now().date()

    all_request_logs = RequestLog.objects.filter(removed_at__isnull=True,
                                                 created_at__range=(start_date, end_date +
                                                                    datetime.timedelta(days=1))). \
        order_by('request_id', '-created_at').distinct('request')
    postponed_amount = RequestLog.objects.filter(pk__in=all_request_logs, status='postponed').count()
    request_logs = RequestLog.objects.filter(pk__in=all_request_logs).filter(status__in=statuses). \
        order_by('created_at').select_related('request', 'request__user')

    if response_type == 'clean':
        response = {'data': [{'pk': log.request.pk, 'number': log.request.get_query_number(),
                              'fio': log.request.user.__str__(),
                              'birthday': log.request.user.birthday.strftime('%d.%m.%Y'),
                              'phone_number': log.request.user.phone_number, 'type': request_types[log.request.type],
                              'question': log.request.question, 'status': log.status,
                              'created_at': log.request.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                              'notes': ';'.join([text[0] for text in log.request.note_set.all().values_list('text')])}
                             for log in request_logs],
                    'info': {
                        'postponed_amount': postponed_amount,
                    }}
    elif response_type == 'datatable':
        response = {'data': [[log.request.pk, log.request.get_query_number(), log.request.user.__str__(),
                              log.request.user.birthday.strftime('%d.%m.%Y'), log.request.user.phone_number,
                              request_types[log.request.type], log.request.question,
                              log.request.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                              ';'.join([text[0] for text in log.request.note_set.all().values_list('text')])]
                             for log in request_logs]}
    else:
        response = []
    json_dump = json.dumps(response)
    return HttpResponse(json_dump, content_type='application/json')


@login_required(login_url='specialist_login')
@permission_required(['dogovor_query.view_query', 'dogovor_query.work_requests'], raise_exception=True)
def get_update_status(request, action, request_pk):
    response = {'request_pk': '', 'status': '', 'changed_at': '', 'changed': False, 'info': ''}
    status = 400
    if action == 'get':
        return HttpResponse('0')
    elif action == 'update':
        if 'status' in request.GET:
            if request.GET['status'] in RequestLog.RequestStatus.values:
                current_request_log = RequestLog.objects.filter(request_id=request_pk)
                if current_request_log:
                    current_request_log = current_request_log[0]
                    response['request_pk'] = current_request_log.request_id
                    if current_request_log.status == 'closed':
                        response['status'] = current_request_log.status
                        response['changed_at'] = current_request_log.created_at.strftime('%d.%m.%Y %H:%M:%S')
                        response['info'] = 'Request is already closed'
                        status = 403
                    else:
                        if current_request_log.status == request.GET['status']:
                            response['status'] = current_request_log.status
                            response['changed_at'] = current_request_log.created_at.strftime('%d.%m.%Y %H:%M:%S')
                            response['info'] = 'Status is already ' + current_request_log.status
                            status = 409
                        else:
                            new_request_log = RequestLog(request_id=request_pk, specialist=request.user,
                                                         status=request.GET['status'])
                            new_request_log.save()
                            response['status'] = new_request_log.status
                            response['changed_at'] = new_request_log.created_at.strftime('%d.%m.%Y %H:%M:%S')
                            response['changed'] = True
                            status = 201
    else:
        status = 405
    return HttpResponse(json.dumps(response), content_type='application/json', status=status)


@login_required(login_url='specialist_login')
@permission_required('dogovor_query.view_query', raise_exception=True)
def search_user(request):
    if request.method == 'POST':
        search_form = SearchUser(request.POST)
        if search_form.is_valid():
            user = User.objects.get(pk=search_form.cleaned_data['user_id'], removed_at__isnull=True)
            user_requests = Request.objects.filter(user=user, removed_at__isnull=True). \
                prefetch_related('requestlog_set', 'requestlog_set__specialist', 'note_set', 'note_set__specialist')
            user_data_edit_form = UserForm(request.POST)
            if user_data_edit_form.is_valid():
                user_data_edit_form = UserForm(request.POST, instance=user)
                user = user_data_edit_form.save()
            else:
                user_data_edit_form = UserForm(instance=user)
            return render(request, 'dogovor_query/manager_search_requests.html',
                          {'search_form': search_form, 'user_data_edit_form': user_data_edit_form,
                           'requests': user_requests, 'client': user})

    else:
        search_form = SearchUser()
        return render(request, 'dogovor_query/manager_search_requests.html', {'search_form': search_form})


@login_required(login_url='specialist_login')
@permission_required('dogovor_query.view_query', raise_exception=True)
def manage_user(request, action):
    if action == 'get':
        if 'fio' in request.GET:
            users = User.objects.annotate(fio=Concat('last_name', V(' '), 'first_name', V(' '), 'second_name')). \
                filter(fio__icontains=request.GET['fio'], removed_at__isnull=True)
            response = [{'pk': user.pk, 'last_name': user.last_name, 'first_name': user.first_name,
                         'second_name': user.second_name, 'fio': user.__str__(),
                         'birthday': user.birthday.strftime('%d.%m.%Y'), 'phone_number': user.phone_number}
                        for user in users]
            return HttpResponse(json.dumps(response))
        elif 'pk' in request.GET:
            user = get_object_or_404(User, pk=request.GET['pk'], removed_at__isnull=True)
            response = {'pk': user.pk, 'last_name': user.last_name, 'first_name': user.first_name,
                        'second_name': user.second_name, 'fio': user.__str__(),
                        'birthday': user.birthday.strftime('%d.%m.%Y'), 'phone_number': user.phone_number}
            return HttpResponse(json.dumps(response))
    elif action == 'select2':
        if 'q' in request.GET:
            users = User.objects.annotate(fio=Concat('last_name', V(' '), 'first_name', V(' '), 'second_name')). \
                filter(fio__icontains=request.GET['q'], removed_at__isnull=True)
            response = [{'id': user.pk, 'text': user.__str__(), 'birthday': user.birthday.strftime('%d.%m.%Y'),
                         'last_name': user.last_name, 'first_name': user.first_name, 'second_name': user.second_name,
                         'phone_number': user.phone_number}
                        for user in users]
            return HttpResponse(json.dumps({'results': response}))


@login_required(login_url='specialist_login')
@permission_required('dogovor_query.view_dashboard', raise_exception=True)
def manager_dashboard(request):
    return render(request, 'dogovor_query/manager_dashboard.html')


@login_required(login_url='specialist_login')
@permission_required('dogovor_query.view_dashboard', raise_exception=True)
def api_get_specialists_requests(request):
    today_request_statuses = RequestLog.objects.filter(removed_at__isnull=True,
                                                       created_at__date=timezone.now().date()). \
        order_by('request_id', '-created_at').distinct('request')

    specialists = Specialist.objects.all().order_by('room', 'last_name').prefetch_related(
        Prefetch('requestlog_set', queryset=RequestLog.objects.filter(pk__in=today_request_statuses,
                                                                      status__in=['activated', 'processing'])),
        Prefetch('requestlog_set__request', queryset=Request.objects.filter(removed_at__isnull=True)),
        Prefetch('requestlog_set__request__user', queryset=User.objects.filter(removed_at__isnull=True)))

    response = [{'specialist_fio': specialist.get_full_name(), 'specialist_room': specialist.room,
                 'specialist_table': specialist.table_number,
                 'requests': [
                     {'request_pk': user_request_log.request.pk,
                      'client_fio': user_request_log.request.user.__str__(),
                      'request_number': user_request_log.request.get_query_number(),
                      'request_type': user_request_log.request.get_type_verbose(),
                      'request_created_at': user_request_log.request.created_at.strftime('%H:%M:%S'),
                      'request_question': user_request_log.request.question,
                      'request_status': user_request_log.get_status_verbose(),
                      'request_status_created_at': user_request_log.created_at.strftime('%H:%M:%S')
                      } for user_request_log in specialist.requestlog_set.all()
                 ]} for specialist in specialists]
    return HttpResponse(json.dumps(response))


@login_required(login_url='specialist_login')
@permission_required('dogovor_query.view_dashboard', raise_exception=True)
def get_pivot_requests(request):
    if 'start_date' in request.GET:
        start_date = generate_start_end_date(request.GET['start_date'], 'start')
        if start_date is None:
            return HttpResponseBadRequest()
    else:
        start_date = datetime.date.min

    if 'end_date' in request.GET:
        end_date = generate_start_end_date(request.GET['end_date'], 'end')
        if end_date is None:
            return HttpResponseBadRequest()
    else:
        end_date = timezone.now().date()

    today_request_statuses = RequestLog.objects.filter(
        removed_at__isnull=True, created_at__range=(start_date, end_date + datetime.timedelta(days=1))). \
        order_by('request_id', '-created_at').distinct('request')
    totals = {item['status']: item['status__count'] for item in
              RequestLog.objects.filter(pk__in=today_request_statuses).values('status').annotate(Count('status'))}
    response = {'today': timezone.now().strftime('%d.%m.%Y %H:%M'), 'start_date': start_date.strftime('%d.%m.%Y'),
                'end_date': end_date.strftime('%d.%m.%Y'), 'query': today_request_statuses.query.__str__(),
                'totals': totals.items()}
    for status in RequestLog.RequestStatus.values:
        if status in totals:
            response[status] = totals[status]
        else:
            response[status] = 0
    return HttpResponse(json.dumps(response))


def is_hostel_request(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('user') or {}
    if 'type' in cleaned_data:
        if cleaned_data['type'] == 'hostel':
            return True
        else:
            return False


def is_university_request(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('user') or {}
    if 'type' in cleaned_data:
        if cleaned_data['type'] == 'university':
            return True
        else:
            return False


def generate_start_end_date(input_date, type):
    if isinstance(input_date, str):
        date_regex = re.compile(r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))"
                                r"(?:(?:1[6-9]|[2-9]\d)\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)(?:0[48]|[2468]"
                                r"[048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])"
                                r"(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)\d{2})$")
        reg_match = date_regex.match(input_date)
        if reg_match:
            splitted_date = list(map(int, [input_date[0:2], input_date[3:5], input_date[6:10]]))
            date_object = datetime.date(day=splitted_date[0], month=splitted_date[1], year=splitted_date[2])
        else:
            return None
    elif isinstance(input_date, datetime.date):
        date_object = input_date
    elif input_date is None:
        if type == 'start':
            date_object = datetime.datetime.min
        elif type == 'end':
            date_object = timezone.now().date()
        else:
            return None
    else:
        return None
    if type == 'end':
        if date_object > timezone.now().date():
            date_object = timezone.now().date()
    return date_object


def get_postponed_requests_id(start_date=None, end_date=None):
    start_date = generate_start_end_date(start_date, type='start')
    end_date = generate_start_end_date(end_date, type='end')
    return set(RequestLog.objects.filter(removed_at__isnull=True,
                                         created_at__range=(start_date, end_date + datetime.timedelta(days=1)),
                                         status='postponed').values_list('request', flat=True))


class RequestWizard(SessionWizardView):
    condition_dict = {
        'university_subject': is_university_request,
        'hostel_subject': is_hostel_request,
    }

    initial_dict = {
        'user': {
            'user_checked': False
        },
    }

    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_initial(self, step):
        initial = self.initial_dict.get(step, {})
        if step == 'user':
            if 'user_uid' in self.request.COOKIES:
                if self.initial_dict['user']['user_checked'] is False:
                    try:
                        user = User.objects.get(user_uid=self.request.COOKIES['user_uid'], removed_at__isnull=True)
                    except Exception as e:
                        print(e)
                        initial.update({'last_name': '', 'first_name': '', 'second_name': '', 'phone_number': '',
                                        'birthday': '', 'user_checked': True})
                        return initial

                    initial.update({'last_name': user.last_name, 'first_name': user.first_name,
                                    'second_name': user.second_name, 'phone_number': user.phone_number,
                                    'birthday': user.birthday, 'user_checked': True})
            else:
                initial.update({'last_name': '', 'first_name': '', 'second_name': '', 'phone_number': '',
                                'birthday': '', 'user_checked': False})
        return initial

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        data['first_name'] = ' '.join([word[0].upper() + word[1:] for word in data['first_name'].split(' ')])
        data['second_name'] = ' '.join([word[0].upper() + word[1:] for word in data['second_name'].split(' ')])
        data['last_name'] = ' '.join([word[0].upper() + word[1:] for word in data['last_name'].split(' ')])

        try:
            user, created = User.objects.get_or_create(first_name=data['first_name'], second_name=data['second_name'],
                                                       last_name=data['last_name'], birthday=data['birthday'])
        except User.MultipleObjectsReturned:
            user = User.objects.filter(first_name=data['first_name'], second_name=data['second_name'],
                                       last_name=data['last_name'], birthday=data['birthday'])[0]
            created = False

        if created is True:
            user.phone_number = data['phone_number']
            user.save()
        else:
            if user.phone_number != data['phone_number']:
                user.phone_number = data['phone_number']
                user.save()
            today_requests = Request.objects.filter(removed_at__isnull=True, created_at__date=timezone.now().date(),
                                                    user=user)
            today_requests_statuses = RequestLog.objects.filter(removed_at__isnull=True, request__in=today_requests). \
                order_by('request_id', '-created_at').distinct('request')
            active_today_requests = RequestLog.objects.filter(pk__in=today_requests_statuses,
                                                              status__in=['created', 'activated', 'processing',
                                                                          'postponed'])
            if active_today_requests:
                response = redirect('main_page')
                response.set_cookie('user_uid', user.user_uid, expires=(datetime.datetime.now() +
                                                                        datetime.timedelta(days=3650)))
                messages.error(self.request, 'У Вас уже есть активная заявка. Отмените ее или ожидайте ее закрытия.')
                return response

        if data['question'] == 'Другое':
            data['question'] = data['other_text']

        if data['type'] == 'hostel':
            if data['hostel_privileges']:
                data['question'] += ';Есть льготы '

        extra_prop = ['last_name', 'first_name', 'second_name', 'phone_number', 'user_uid', 'temporary_move',
                      'birthday', 'other_text', 'hostel', 'hostel_privileges']
        for prop in extra_prop:
            if prop in data:
                data.pop(prop)

        last_requests = Request.objects.filter(type=data['type'], created_at__date=timezone.now().date())
        if last_requests:
            new_number = last_requests.order_by('-number')[0].number + 1
        else:
            new_number = 0

        new_request = Request(user=user, number=new_number, **data)
        new_request.save()
        request_log = RequestLog(request=new_request, status=RequestLog.RequestStatus.CREATED)
        request_log.save()
        response = redirect('main_page')
        response.set_cookie('user_uid', user.user_uid, expires=(datetime.datetime.now() +
                                                                datetime.timedelta(days=3650)))
        self.initial_dict['user']['user_checked'] = False
        return response
