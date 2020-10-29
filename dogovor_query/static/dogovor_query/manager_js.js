$(document).ready(function () {
    let request_id = $('#request_id')
    let request_status = $('#request_current_status')
    let current_query_number = $('#current_query_number')
    let current_client_fio = $('#current_client_fio')
    let current_client_birthday = $('#current_client_birthday')
    let current_client_phone_number = $('#current_client_phone_number')
    let current_client_request_type = $('#current_client_request_type')
    let current_client_request_question = $('#current_client_request_question')
    let span_status_text = $('#span_status_text')
    let request_current_status_created_at = $('#request_current_status_created_at')
    let span_timer = $('#current_client_status_time')
    let timer = new easytimer.Timer()
    let request_id_note = $('#request_id_note')
    let request_text_note = $('#request_text_note')
    let add_note_modal = $('#add_note_modal')
    let requests_count = 0
    let is_first_ajax_call = 1

    let requests_table = $('#requests_table').DataTable({
        "paging": false,
        "fnInitComplete": function () {
            var myCustomScrollbar = document.querySelector('#requests_table_wrapper .dataTables_scrollBody');
            var ps = new PerfectScrollbar(myCustomScrollbar);
        },
        "scrollY": 450,
        "ajax": {
            url: 'api/requests/get?status=created',
            dataSrc: function (data) {
                $('#postponed_amount').text(data.info.postponed_amount)
                $('#created_amount').text(data.info.created_amount)
                return data.data
            },
            "complete": function (data) {
                let requests = data['responseJSON'].data
                if (requests_table.ajax.url().endsWith('created')) {
                    if (requests_count < requests.length && is_first_ajax_call === 0) {
                        let audioElement = document.createElement('audio');
                        audioElement.setAttribute('src', 'https://proxy.notificationsounds.com/notification-sounds/just-maybe-577/download/file-sounds-1124-just-maybe.mp3');
                        let promise = audioElement.play()
                    } else if (is_first_ajax_call === 1) {
                        is_first_ajax_call = 0
                    }
                    requests_count = requests.length
                }
            }
        },
        "ordering": false,
        "searching": false,
        rowId: 'pk',
        deferRender: true,
        language: {
            "processing": "Подождите...",
            "search": "Поиск:",
            "lengthMenu": "Показать _MENU_ заявок",
            "info": "Заявки с _START_ до _END_ из _TOTAL_ заявок",
            "infoEmpty": "Заявки с 0 до 0 из 0 заявок",
            "infoFiltered": "(отфильтровано из _MAX_ заявок)",
            "infoPostFix": "",
            "loadingRecords": "Загрузка заявок...",
            "zeroRecords": "Заявки отсутствуют.",
            "emptyTable": "В настоящее время новых заявок нет",
            "paginate": {
                "first": "Первая",
                "previous": "Предыдущая",
                "next": "Следующая",
                "last": "Последняя"
            },
            "aria": {
                "sortAscending": ": активировать для сортировки столбца по возрастанию",
                "sortDescending": ": активировать для сортировки столбца по убыванию"
            },
            "select": {
                "rows": {
                    "_": "Выбрано заявок: %d",
                    "0": "Кликните по заявке для выбора",
                    "1": "Выбрана одна заявка"
                }
            }
        },
        columns: [
            {data: 'pk'},
            {data: 'number', width: '7%'},
            {data: 'fio', width: '20%'},
            {data: 'birthday', width: '13%'},
            {data: 'phone_number', width: '15%'},
            {data: 'type', width: '15%'},
            {data: 'question', width: '30%'},
            {data: 'created_at'},
            {data: 'status'},
        ],
        "columnDefs": [
            {
                "targets": [0, 7, 8],
                "visible": false,
                "searchable": false
            }
        ],
        dom: 'Bfrtip',
        select: {
            style: 'single'
        },
        buttons: [
            {
                text: 'Вызвать',
                className: 'btn-warning',
                init: function (dt, node, config) {
                    $(node).removeClass('btn-secondary')
                    this.disable()
                },
                action: function (e, dt, node, config) {
                    let data = dt.rows('.selected').data()
                    $.ajax({
                        type: 'GET',
                        url: '/manager/api/status/update/' + data[0]['pk'],
                        data: {
                            'status': 'activated'
                        },
                        statusCode: {
                            400: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Произошла ошибка запроса. Обратитесь к администратору.',
                                    delay: 5000,
                                });
                            },
                            403: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже закрыта. Обновите страницу.',
                                    delay: 5000,
                                });
                            },
                            409: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже активирована, возможно, другим специалистом.',
                                    delay: 5000,
                                });
                                dt.rows('.selected').remove().draw(false);
                            }
                        },
                        success: function (response) {
                            $.toast({
                                type: 'success',
                                title: 'Статус заявки изменен',
                                content: 'Заявка успешно активирована, человек приглашен в кабинет.',
                                delay: 5000,
                            });
                            request_id.val(data[0]['pk'])
                            request_status.val('activated')
                            request_current_status_created_at.val(data[0]['created_at'])
                            span_status_text.removeClass()
                            span_status_text.addClass('badge badge-warning')
                            span_status_text.text('Вызван')
                            current_query_number.text(data[0]['number'])
                            current_client_fio.text(data[0]['fio'])
                            current_client_birthday.text(data[0]['birthday'])
                            current_client_phone_number.text(data[0]['phone_number'])
                            current_client_request_type.text(data[0]['type'])
                            current_client_request_question.text(data[0]['question'])
                            timer_change_state('start', response.changed_at)
                            dt.rows('.selected').remove().draw(false);
                            dt.buttons([0, 4]).disable()
                            dt.buttons([1, 2, 3, 5]).enable()
                        }
                    })
                }
            },
            {
                text: 'Начать работу',
                className: 'btn-success',
                init: function (dt, node, config) {
                    $(node).removeClass('btn-secondary')
                    if (request_status.val() !== 'activated') {
                        this.disable()
                    }
                },
                action: function (e, dt, node, config) {
                    $.ajax({
                        type: 'GET',
                        url: '/manager/api/status/update/' + request_id.val(),
                        data: {
                            'status': 'processing'
                        },
                        statusCode: {
                            400: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Произошла ошибка запроса. Обратитесь к администратору.',
                                    delay: 5000,
                                });
                            },
                            403: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже закрыта. Обновите страницу.',
                                    delay: 5000,
                                });
                            },
                            409: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже в работе. Обновите страницу.',
                                    delay: 5000,
                                });
                            }
                        },
                        success: function (response) {
                            $.toast({
                                type: 'success',
                                title: 'Статус заявки изменен',
                                content: 'Работа по заявке успешно начата.',
                                delay: 5000,
                            });
                            request_status.val('processing')
                            request_current_status_created_at.val(response.changed_at)
                            span_status_text.removeClass()
                            span_status_text.addClass('badge badge-success')
                            span_status_text.text('В работе')
                            timer_change_state('reset')
                            timer_change_state('stop')
                            timer_change_state('start', response.changed_at)
                            dt.buttons([0, 1, 2]).disable()
                            dt.buttons([3, 4, 5]).enable()
                        }
                    })
                }
            },
            {
                text: 'Отменить заявку',
                className: 'btn-danger',
                init: function (api, node, config) {
                    $(node).removeClass('btn-secondary')
                    if (request_status.val() !== 'activated') {
                        this.disable()
                    }
                },
                action: function (e, dt, node, config) {
                    let request_pk = request_id.val()
                    if (request_id.val().length === 0) {
                        request_pk = dt.rows('.selected').data()[0]['pk']
                    }
                    $.ajax({
                        type: 'GET',
                        url: '/manager/api/status/update/' + request_pk,
                        data: {
                            'status': 'cancelled'
                        },
                        statusCode: {
                            400: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Произошла ошибка запроса. Обратитесь к администратору.',
                                    delay: 5000,
                                });
                            },
                            403: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже закрыта. Обновите страницу.',
                                    delay: 5000,
                                });
                            },
                            409: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже отменена. Обновите страницу.',
                                    delay: 5000,
                                });
                            }
                        },
                        success: function (response) {
                            $.toast({
                                type: 'success',
                                title: 'Статус заявки изменен',
                                content: 'Заявка успешно отменена.',
                                delay: 5000,
                            });
                            if (request_id.val().length === 0) {
                                dt.rows('.selected').remove().draw(false);
                            }
                            request_id.val('')
                            request_status.val('')
                            request_current_status_created_at.val('')
                            span_status_text.removeClass()
                            span_status_text.text('')
                            current_client_fio.text('')
                            current_client_birthday.text('')
                            current_client_phone_number.text('')
                            current_client_request_type.text('')
                            current_client_request_question.text('')
                            current_query_number.text('')
                            timer_change_state('reset')
                            timer_change_state('stop')
                            timer_change_state('start', moment().format("DD.MM.YYYY HH:mm:ss"))
                            timer_change_state('stop')
                            dt.buttons([0, 1, 2, 3, 4, 5]).disable()
                        }
                    })
                }
            },
            {
                text: 'Отложить заявку',
                className: 'btn-dark',
                init: function (dt, node, config) {
                    $(node).removeClass('btn-secondary')
                    if (request_status.val().length === 0 || request_id.val().length === 0) {
                        this.disable()
                    }
                },
                action: function (e, dt, node, config) {
                    $.ajax({
                        type: 'GET',
                        url: '/manager/api/status/update/' + request_id.val(),
                        data: {
                            'status': 'postponed'
                        },
                        statusCode: {
                            400: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Произошла ошибка запроса. Обратитесь к администратору.',
                                    delay: 5000,
                                });
                            },
                            403: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже закрыта. Обновите страницу.',
                                    delay: 5000,
                                });
                            },
                            409: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже отложена. Обновите страницу.',
                                    delay: 5000,
                                });
                            }
                        },
                        success: function (response) {
                            $.toast({
                                type: 'success',
                                title: 'Статус заявки изменен',
                                content: 'Заявка успешно перемещена в отложенные. Для повторного вызова нажмите кнопку "Показать отложенные заявки"',
                                delay: 5000,
                            });
                            request_id.val('')
                            request_status.val('')
                            request_current_status_created_at.val('')
                            span_status_text.removeClass()
                            span_status_text.text('')
                            current_client_fio.text('')
                            current_client_birthday.text('')
                            current_client_phone_number.text('')
                            current_client_request_type.text('')
                            current_client_request_question.text('')
                            current_query_number.text('')
                            timer_change_state('reset')
                            timer_change_state('stop')
                            timer_change_state('start', moment().format("DD.MM.YYYY HH:mm:ss"))
                            timer_change_state('stop')
                            dt.buttons([0, 1, 2, 3, 4, 5]).disable()
                        }
                    })
                }
            },
            {
                text: 'Завершить работу',
                className: 'btn-primary',
                init: function (api, node, config) {
                    $(node).removeClass('btn-secondary')
                    if (request_status.val() !== 'processing' || request_id.val().length === 0) {
                        this.disable()
                    }
                },
                action: function (e, dt, node, config) {
                    $.ajax({
                        type: 'GET',
                        url: '/manager/api/status/update/' + request_id.val(),
                        data: {
                            'status': 'closed'
                        },
                        statusCode: {
                            400: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Произошла ошибка запроса. Обратитесь к администратору.',
                                    delay: 5000,
                                });
                            },
                            403: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже закрыта. Обновите страницу.',
                                    delay: 5000,
                                });
                            },
                            409: function () {
                                $.toast({
                                    type: 'error',
                                    title: 'Ошибка',
                                    content: 'Заявка уже завершена. Обновите страницу.',
                                    delay: 5000,
                                });
                            }
                        },
                        success: function (response) {
                            $.toast({
                                type: 'success',
                                title: 'Статус заявки изменен',
                                content: 'Заявка успешно обработана и закрыта.',
                                delay: 5000,
                            });
                            request_id.val('')
                            request_status.val('')
                            request_current_status_created_at.val('')
                            span_status_text.removeClass()
                            span_status_text.text('')
                            current_client_fio.text('')
                            current_client_birthday.text('')
                            current_client_phone_number.text('')
                            current_client_request_type.text('')
                            current_client_request_question.text('')
                            current_query_number.text('')
                            timer_change_state('reset')
                            timer_change_state('stop')
                            timer_change_state('start', moment().format("DD.MM.YYYY HH:mm:ss"))
                            timer_change_state('stop')
                            dt.buttons([0, 1, 2, 3, 4, 5]).disable()
                        }
                    })
                }
            },
            {
                text: 'Добавить примечание',
                className: 'btn-secondary',
                init: function (api, node, config) {
                    if (request_id.val().length === 0) {
                        this.disable()
                    }
                },
                action: function (e, dt, node, config) {
                    if (request_id.val().length !== 0) {
                        add_note_modal.modal('show')
                    } else {
                        $.toast({
                            type: 'error',
                            title: 'Ошибка',
                            content: 'Попробуйте обновить страницу.',
                            delay: 5000,
                        });
                    }
                }
            },
            {
                text: 'Показать отложенные заявки',
                className: 'btn-info btn-block',
                init: function (api, node, config) {
                    $(node).removeClass('btn-secondary')
                    $(node).text(' Показать отложенные заявки')
                    $(node).prepend("<span id=\"postponed_amount\" class=\"badge badge-light\"></span>")
                },
                action: function (e, dt, node, config) {
                    if (dt.ajax.url().endsWith('created')) {
                        current_request_type = 'postponed'
                        dt.ajax.url('api/requests/get?status=postponed').load()
                        $(node).text('Вернуться к активным заявкам')
                    } else if (dt.ajax.url().endsWith('postponed')) {
                        current_request_type = 'created'
                        dt.ajax.url('api/requests/get?status=created').load()
                        $(node).text(' Показать отложенные заявки')
                        $(node).prepend("<span id=\"postponed_amount\" class=\"badge badge-light\"></span>")
                    }
                }
            },
        ],
    }).on('select', function (e, dt, type, indexes) {
        if (type === 'row') {
            if (request_id.val().length === 0) {
                dt.buttons([0, 2]).enable()
            }
        }
    }).on('deselect', function (e, dt, type, indexes) {
        if (type === 'row') {
            if (request_id.val().length === 0) {
                dt.buttons([0, 2]).disable()
            }
        }
    });

    setInterval(function () {
        requests_table.ajax.reload();
    }, 5000);

    function timer_change_state(new_state, timestamp = '') {
        if (new_state === 'stop') {
            timer.stop()
        } else if (new_state === 'reset') {
            timer.reset()
        } else if (new_state === 'start') {
            if (timestamp === '') {
                timestamp = request_current_status_created_at.val()
            }
            if (timestamp.length !== 0) {
                let seconds_passed = moment().diff(moment(timestamp, "DD.MM.YYYY HH:mm:ss"), 'seconds')
                timer.start({precision: 'seconds', startValues: {seconds: seconds_passed}});
            }
        }
    }

    timer_change_state('start');

    timer.addEventListener('secondsUpdated', function (e) {
        span_timer.text(timer.getTimeValues().toString());
    });

    timer.addEventListener('started', function (e) {
        span_timer.text(timer.getTimeValues().toString());
    });

    timer.addEventListener('reset', function (e) {
        span_timer.text(timer.getTimeValues().toString());
    });
    //
    // function sound_notification_on_requests() {
    //     if (requests_table.ajax.url().endsWith('created')) {
    //         if (requests_count < requests.length && is_first_ajax_call === 0) {
    //             let audioElement = document.createElement('audio');
    //             audioElement.setAttribute('src', 'https://proxy.notificationsounds.com/notification-sounds/just-maybe-577/download/file-sounds-1124-just-maybe.mp3');
    //             let promise = audioElement.play()
    //         } else if (is_first_ajax_call === 1) {
    //             is_first_ajax_call = 0
    //         }
    //         requests_count = requests.length
    //     }
    // }

    $('#add_note').on('click', function () {
        if (request_id.val().length !== 0 && request_text_note.val().length !== 0) {
            $.ajax({
                type: 'GET',
                url: '/manager/api/note/add',
                data: {
                    'request_id': request_id.val(),
                    'note_text': request_text_note.val()
                },
                statusCode: {
                    400: function () {
                        $.toast({
                            type: 'error',
                            title: 'Ошибка',
                            content: 'Произошла ошибка запроса. Обратитесь к администратору.',
                            delay: 5000,
                        });
                    }
                },
                success: function (response) {
                    $.toast({
                        type: 'success',
                        title: 'Успешно',
                        content: 'Примечание успешно добавлено.',
                        delay: 5000,
                    });
                    let request_notes = $('#request_notes')
                    if (request_notes.text().length > 0) {
                        request_notes.text(request_notes.text() + ";" + response.note_text)
                    } else {
                        request_notes.text(response.note_text)
                    }
                    request_text_note.val('')
                    add_note_modal.modal('hide')
                }
            })
        } else {
            $.toast({
                type: 'error',
                title: 'Ошибка',
                content: 'Попробуйте обновить страницу.',
                delay: 5000,
            });
        }
    })
});