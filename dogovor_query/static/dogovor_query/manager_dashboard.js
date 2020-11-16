let cards_container = $('#cards_container')
let blink_dot_status = $('#blink_dot_status')

$(document).ready(function () {
    function update_specialists_dashboard() {
        $.ajax({
            url: '/manager/api/requests/specialists/get',
            method: 'GET',
            success: function (response) {
                let data = JSON.parse(response)
                let request_cards_html = ''
                data.forEach(function (specialist, i, obj) {
                    request_cards_html += "<div class=\"col mb-4\"><div class=\"card border-info\">" +
                        "<div class=\"card-header\"><h5>" + specialist.specialist_fio + "</h5></div>" +
                        "<div class=\"card-body\">" +
                        "<ul class=\"list-group list-group-horizontal-sm mb-3\">" +
                        "<li class=\"list-group-item\">Кабинет: " + specialist.specialist_room + "</li>" +
                        "<li class=\"list-group-item\">Стол: " + specialist.specialist_table + "</li>" +
                        "</ul>" +
                        "<div class=\"card\">" +
                        "<div class=\"card-header\">Текущий клиент</div>" +
                        "<div class=\"card-body\">"
                    if (specialist.requests.length > 0) {
                        request_cards_html += "<ul class=\"list-group list-group-flush\">" +
                            "<li class=\"list-group-item\">ФИО: " + specialist.requests[0].client_fio + "</li>" +
                            "<li class=\"list-group-item\">Номер: " + specialist.requests[0].request_number + "</li>" +
                            "<li class=\"list-group-item\">Тип: " + specialist.requests[0].request_type + "</li>" +
                            "<li class=\"list-group-item\">Тема: " + specialist.requests[0].request_question + "</li>"
                        if (specialist.requests[0].request_status === 'Активирована') {
                            request_cards_html += "<li class=\"list-group-item\">Статус: <span class='badge badge-success'>Клиент вызван</span></li>"
                        } else if (specialist.requests[0].request_status === 'Обрабатывается') {
                            request_cards_html += "<li class=\"list-group-item\">Статус: <span class='badge badge-primary'>Обрабатывется</span></li>"
                        }
                        request_cards_html += "</ul>"
                    } else {
                        request_cards_html += "<span class=\"badge badge-secondary\">Ожидание</span>"
                    }
                    request_cards_html += "</div></div></div></div></div>"
                })
                cards_container.html(request_cards_html);
                if (blink_dot_status.html().includes("red") || blink_dot_status.html().length === 0) {
                    blink_dot_status.html("<svg height=\"25\" width=\"25\" class=\"blinking\">" +
                    "<circle cx=\"15\" cy=\"10\" r=\"5\" fill=\"green\" /></svg>")
                }
            },
            error: function(jqXHR, exception) {
                if (blink_dot_status.html().includes("green") || blink_dot_status.html().length === 0) {
                    blink_dot_status.html("<svg height=\"25\" width=\"25\" class=\"blinking\">" +
                    "<circle cx=\"15\" cy=\"10\" r=\"5\" fill=\"red\" /></svg>")
                }
            }
        })
    }

    function update_pivot_dashboard() {
        $.ajax({
            url: '/manager/api/requests/pivot/get',
            method: 'GET',
            success: function (response) {
                let data = JSON.parse(response)
                $('#requests_all_count').text(data['created'] + data['activated'] + data['processing'] + data['closed'] + data['cancelled'] + data['postponed'])
                $('#requests_waiting_count').text(data['created'] + data['postponed'])
                $('#requests_processing_count').text(data['activated'] + data['processing'])
                $('#requests_closed_count').text(data['closed'])
                $('#requests_cancelled_count').text(data['cancelled'])
                $('#today_date').text(data['today'])
                if (blink_dot_status.html().includes("red") || blink_dot_status.html().length === 0) {
                    blink_dot_status.html("<svg height=\"25\" width=\"25\" class=\"blinking\">" +
                    "<circle cx=\"15\" cy=\"10\" r=\"5\" fill=\"green\" /></svg>")
                }
            },
            error: function(jqXHR, exception) {
                if (blink_dot_status.html().includes("green") || blink_dot_status.html().length === 0) {
                    blink_dot_status.html("<svg height=\"25\" width=\"25\" class=\"blinking\">" +
                    "<circle cx=\"15\" cy=\"10\" r=\"5\" fill=\"red\" /></svg>")
                }
            }
        })
    }

    update_specialists_dashboard();
    update_pivot_dashboard();
    setInterval(function () {
        update_specialists_dashboard();
        update_pivot_dashboard()
    }, 6000);
})