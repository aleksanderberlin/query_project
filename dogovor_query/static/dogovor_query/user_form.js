$(document).ready(function () {
    let span_user_status = $('#span_user_status')
    let div_card_people_before = $('#card_people_before')
    let div_card_welcome = $('#card_welcome')
    let div_card_cancel_request = $('#card_cancel_request')
    let div_card_new_request = $('#card_new_request')
    let attention_info = $('#attention_info')

    function update_request_status() {
        $.ajax({
            url: 'api/query/get',
            success: function (response) {
                let data = JSON.parse(response)

                if (data.current_status === 'created') {
                    span_user_status.text('Ожидание вызова')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-warning')
                    div_card_people_before.show()
                    div_card_welcome.hide()
                    div_card_cancel_request.show()
                    div_card_new_request.hide()
                    attention_info.show()
                } else if (data.current_status === 'activated') {
                    span_user_status.text('Вызов')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-success blob')
                    div_card_welcome.removeClass('bg-info d-none')
                    div_card_welcome.addClass('bg-success')
                    div_card_welcome.find('div:nth-child(1)').html('Ваша очередь подошла! Проходите в кабинет 214/2 к столу номер <span class="span_info" id="span_specialist_table_number"></span> к специалисту <span class="span_info" id="span_specialist_name"></span>')
                    div_card_welcome.show()
                    div_card_people_before.hide()
                    div_card_cancel_request.hide()
                    div_card_new_request.hide()
                    attention_info.hide()
                } else if (data.current_status === 'processing') {
                    span_user_status.text('Обработка')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-primary blob')
                    div_card_welcome.removeClass('bg-success')
                    div_card_welcome.addClass('bg-info')
                    div_card_welcome.find('div:nth-child(1)').html('С Вами работает специалист <span class="span_info" id="span_specialist_name"></span>')
                    div_card_welcome.show()
                    div_card_people_before.hide()
                    div_card_cancel_request.hide()
                    div_card_new_request.hide()
                    attention_info.hide()
                } else if (data.current_status === 'cancelled') {
                    span_user_status.text('Отменена')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-danger')
                    div_card_welcome.hide()
                    div_card_people_before.hide()
                    div_card_cancel_request.hide()
                    div_card_new_request.show()
                    attention_info.hide()
                } else if (data.current_status === 'closed') {
                    span_user_status.text('Обработана')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-dark')
                    div_card_welcome.hide()
                    div_card_people_before.hide()
                    div_card_cancel_request.hide()
                    div_card_new_request.show()
                    attention_info.hide()
                } else if (data.current_status === 'postponed') {
                    span_user_status.text('Отложена')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-secondary')
                    div_card_welcome.hide()
                    div_card_people_before.hide()
                    div_card_cancel_request.show()
                    div_card_new_request.hide()
                    attention_info.show()
                }

                $('#span_user_query_number').text(data.query_number)
                $('#span_user_fio').text(data.fio)
                $('#span_user_before_amount').text(data.people_before)
                $('#span_specialist_table_number').text(data.table_number)
                $('#span_specialist_name').text(data.specialist_name)
            }
        })
    }

    let status_auto_update = setInterval(function () {
        update_request_status();
    }, 10000);

    $('#cancel_request').on('click', function () {
        $.ajax({
            type: 'GET',
            url: '/api/request/cancel',
            statusCode: {
                403: function() {
                    alert('Редактирование невозможно, статус заявки некорректный.')
                }
            },
            success: function (response) {
                span_user_status.text('Отменена')
                span_user_status.removeClass()
                span_user_status.addClass('badge badge-danger')
                div_card_welcome.hide()
                div_card_people_before.hide()
                div_card_cancel_request.hide()
                div_card_new_request.show()
                attention_info.hide()
                clearInterval(status_auto_update);
            }
        })
    })
})