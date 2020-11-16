function getKeyByValue(object, value) {
    return Object.keys(object).find(key => object[key] === value);
}

$(document).ready(function () {
    let span_user_status = $('#span_user_status')
    let div_user_status = $('#div_user_status')
    let div_card_pretty_status_info = $('#card_pretty_status_info')
    let div_card_cancel_request = $('#card_cancel_request')
    let div_card_new_request = $('#card_new_request')
    let attention_info = $('#attention_info')
    const statuses = {
        'created': 'Ожидание вызова',
        'activated': 'Вызов',
        'processing': 'Обработка',
        'cancelled': 'Отменена',
        'closed': 'Обработана',
        'postponed': 'Отложена'
    }

    function update_request_status() {
        $.ajax({
            url: '/api/query/get',
            success: function (response) {
                let data = JSON.parse(response)
                if (data.current_status !== getKeyByValue(statuses, span_user_status.text())) {
                    if (data.current_status === 'created') {
                        div_user_status.html("<span id=\"span_user_status\">"+statuses[data.current_status]+"</span>")
                        div_user_status.prepend("<span class=\"spinner-border spinner-border-sm\" aria-hidden=\"true\" role=\"status\"></span> ")
                        div_user_status.removeClass().addClass('badge badge-warning')
                        div_card_pretty_status_info.removeClass().addClass('card bg-light mt-2 mb-2')
                        if (data.people_before !== 0) {
                            div_card_pretty_status_info.find('div:nth-child(1)').html('Перед Вами Перед вами <span class="span_info" id="span_user_before_amount">' + data.people_before + '</span> чел.')
                        } else {
                            div_card_pretty_status_info.find('div:nth-child(1)').html('Перед Вами нет людей в очереди. Совсем скоро специалист пригласит Вас в кабинет! Ожидайте, пожалуйста.')
                        }
                        div_card_pretty_status_info.show()
                        div_card_cancel_request.show()
                        div_card_new_request.hide()
                        attention_info.show()
                    } else if (data.current_status === 'activated') {
                        div_user_status.html("<span id=\"span_user_status\">"+statuses[data.current_status]+"</span>")
                        div_user_status.removeClass().addClass('badge badge-success blob')
                        div_card_pretty_status_info.removeClass().addClass('card mt-2 mb-2 bg-success text-white')
                        div_card_pretty_status_info.find('div:nth-child(1)').html('Специалист готов Вас принять! Проходите в кабинет <span class="span_info" id="span_specialist_room">' + data.room + '</span> к столу номер <span class="span_info" id="span_specialist_table_number">' + data.table_number + '</span> к специалисту <span class="span_info" id="span_specialist_name">' + data.specialist_name + '</span>')
                        div_card_pretty_status_info.show()
                        div_card_cancel_request.hide()
                        div_card_new_request.hide()
                        attention_info.hide()
                    } else if (data.current_status === 'processing') {
                        div_user_status.html("<span id=\"span_user_status\">"+statuses[data.current_status]+"</span>")
                        div_user_status.removeClass().addClass('badge badge-primary blob')
                        div_card_pretty_status_info.removeClass().addClass('card mt-2 mb-2 bg-info text-white')
                        div_card_pretty_status_info.find('div:nth-child(1)').html('С Вами работает специалист <span class="span_info" id="span_specialist_name">' + data.specialist_name + '</span>')
                        div_card_pretty_status_info.show()
                        div_card_cancel_request.hide()
                        div_card_new_request.hide()
                        attention_info.hide()
                    } else if (data.current_status === 'cancelled') {
                        div_user_status.html("<span id=\"span_user_status\">"+statuses[data.current_status]+"</span>")
                        div_user_status.removeClass().addClass('badge badge-danger')
                        div_card_pretty_status_info.hide()
                        div_card_cancel_request.hide()
                        div_card_new_request.show()
                        attention_info.hide()
                    } else if (data.current_status === 'closed') {
                        div_user_status.html("<span id=\"span_user_status\">"+statuses[data.current_status]+"</span>")
                        div_user_status.removeClass().addClass('badge badge-dark')
                        div_card_pretty_status_info.hide()
                        div_card_cancel_request.hide()
                        div_card_new_request.show()
                        attention_info.hide()
                    } else if (data.current_status === 'postponed') {
                        div_user_status.html("<span id=\"span_user_status\">"+statuses[data.current_status]+"</span>")
                        div_user_status.removeClass().addClass('badge badge-secondary')
                        div_card_pretty_status_info.hide()
                        div_card_cancel_request.show()
                        div_card_new_request.hide()
                        attention_info.show()
                    }
                    $('#span_user_query_number').text(data.query_number)
                    $('#span_user_fio').text(data.fio)
                } else if (data.current_status === 'created') {
                    $('#span_user_before_amount').text(data.people_before)
                }
            }
        })
    }

    update_request_status();
    let status_auto_update = setInterval(function () {
        update_request_status();
    }, 5000);

    $('#cancel_request').on('click', function () {
        $.ajax({
            type: 'GET',
            url: '/api/request/cancel',
            statusCode: {
                403: function () {
                    alert('Редактирование невозможно, статус заявки некорректный.')
                }
            },
            success: function (response) {
                div_user_status.html("<span id=\"span_user_status\">Отменена</span>")
                div_user_status.removeClass().addClass('badge badge-danger')
                div_card_pretty_status_info.hide()
                div_card_cancel_request.hide()
                div_card_new_request.show()
                attention_info.hide()
                clearInterval(status_auto_update);
            }
        })
    })
})