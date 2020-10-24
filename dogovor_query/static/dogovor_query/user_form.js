$(document).ready(function () {
    let span_user_status = $('#span_user_status')
    let div_card_people_before = $('#card_people_before')
    let div_card_welcome = $('#card_welcome')
    // блоки
    // 1) ФИО Клиента - всегда показывать
    // 2) Номер талончика - всегда показывать
    // 3) Текущий статус - всегда показывать
    // 4) Сколько человек перед Вами - показывать ТОЛЬКО если заявка еще не вызвана
    // 5) Карточка приглашения или статуса в работе - показывать ВО ВСЕХ случаях кроме когда карточка вызвана
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
                } else if (data.current_status === 'activated') {
                    span_user_status.text('Вызов')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-success blob')
                    div_card_welcome.removeClass('bg-info d-none')
                    div_card_welcome.addClass('bg-success')
                    div_card_welcome.find('div:nth-child(1)').html('Ваша очередь подошла! Проходите в кабинет 214/2 к столу номер <span class="span_info" id="span_specialist_table_number"></span> к специалисту <span class="span_info" id="span_specialist_name"></span>')
                    div_card_welcome.show()
                    div_card_people_before.hide()
                } else if (data.current_status === 'processing') {
                    span_user_status.text('Обработка')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-primary blob')
                    div_card_welcome.removeClass('bg-success')
                    div_card_welcome.addClass('bg-info')
                    div_card_welcome.find('div:nth-child(1)').html('С Вами работает специалист <span class="span_info" id="span_specialist_name"></span>')
                    div_card_welcome.show()
                    div_card_people_before.hide()
                } else if (data.current_status === 'cancelled') {
                    span_user_status.text('Отменена')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-danger')
                    div_card_welcome.hide()
                    div_card_people_before.hide()
                } else if (data.current_status === 'closed') {
                    span_user_status.text('Обработана')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-dark')
                    div_card_welcome.hide()
                    div_card_people_before.hide()
                } else if (data.current_status === 'postponed') {
                    span_user_status.text('Отложена')
                    span_user_status.removeClass()
                    span_user_status.addClass('badge badge-secondary')
                    div_card_welcome.hide()
                    div_card_people_before.hide()
                }

                $('#span_user_query_number').text(data.query_number)
                $('#span_user_fio').text(data.fio)
                $('#span_user_before_amount').text(data.people_before)
                $('#span_specialist_table_number').text(data.table_number)
                $('#span_specialist_name').text(data.specialist_name)
            }
        })
    }

    setInterval(function () {
        update_request_status();
    }, 10000);
})