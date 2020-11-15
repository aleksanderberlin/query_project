$(document).ready(function () {

    let current_search_user_pk = $('#current_search_user_pk')

    let user_select = $('#id_user').select2({
        theme: 'bootstrap4',
        language: {
            errorLoading: function () {
                return 'Ошибка поиска.';
            },
            inputTooShort: function (args) {
                let remainingChars = args.minimum - args.input.length;
                return 'Пожалуйста, введите ' + remainingChars + ' или более символов';
            },
            noResults: function () {
                return 'Клиент не найден';
            },
            searching: function () {
                return 'Поиск…';
            }
        },
        ajax: {
            url: '/manager/api/user/select2',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term
                };
            },
        },
        placeholder: 'Начните вводить имя',
        minimumInputLength: 3,
    })

    if (current_search_user_pk.val().length !== 0) {
        $.ajax({
            url: '/manager/api/user/get',
            method: 'GET',
            data: {
                'pk': current_search_user_pk.val()
            },
            success: function (response) {
                let data = JSON.parse(response)
                user_select.append(new Option(data.fio, data.pk, true, true)).trigger('change');
                user_select.trigger({
                    type: 'select2:select',
                    params: {
                        data: data
                    }
                });
            }
        })
    }
})