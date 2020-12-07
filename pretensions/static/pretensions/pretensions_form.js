$(document).ready(function () {
    let checkbox_is_buyer_student_same = $('#id_is_buyer_student_same')
    let checkbox_is_without_peni = $('#id_is_without_peni')
    let select_otch_reason = $('#id_otch_reason')

    $('#id_specialty').select2({
        theme: 'bootstrap4',
    });
    $('#id_performer').select2({
        theme: 'bootstrap4',
    });
    $('#id_director').select2({
        theme: 'bootstrap4',
    });
    $('#id_buyer_sex').select2({
        theme: 'bootstrap4',
    });
    $('#id_student_sex').select2({
        theme: 'bootstrap4',
    });

    select_otch_reason.select2({
        theme: 'bootstrap4',
    }).on('select2:select', function (e) {
        var data = e.params.data;
        if (data.id === 'vuz_change') {
            $('#id_another_vuz').show();
            $('#id_other_text').hide();
        } else if (data.id === 'other') {
            $('#id_another_vuz').hide();
            $('#id_other_text').show();
        } else {
            $('#id_another_vuz').hide();
            $('#id_other_text').hide();
        }
    });

    if (select_otch_reason.val() === 'vuz_change') {
        $('#id_another_vuz').show();
        $('#id_other_text').hide();
    } else if (select_otch_reason.val() === 'other') {
        $('#id_another_vuz').hide();
        $('#id_other_text').show();
    }

    if (checkbox_is_buyer_student_same.is(':checked')) {
        $('#student_fio').hide();
    }

    checkbox_is_buyer_student_same.change(function () {
        if (this.checked) {
            $('#student_fio').hide();
        } else {
            $('#student_fio').show();
        }
    });

    if (checkbox_is_without_peni.is(':checked')) {
        $('#key_rate_info').hide();
        $('#create_pretension').removeAttr("disabled");
    }

    checkbox_is_without_peni.change(function () {
        if (this.checked) {
            $('#key_rate_info').hide();
            $('#create_pretension').attr("disabled", true);
        } else {
            $('#key_rate_info').show();
            $('#create_pretension').removeAttr("disabled");
        }
    });

    // ADDRESS SUGGESTIONS
    function join(arr /*, separator */) {
        var separator = arguments.length > 1 ? arguments[1] : ", ";
        return arr.filter(function (n) {
            return n
        }).join(separator);
    }

    function dotify(address) {
        var shortTypes = ['аобл', 'респ', 'вл', 'г', 'д', 'двлд', 'днп', 'дор', 'дп', 'жт', 'им', 'к', 'кв', 'км', 'комн', 'кп', 'лпх', 'м', 'мкр', 'наб', 'нп', 'обл', 'оф', 'п', 'пгт', 'пер', 'пл', 'платф', 'рзд', 'рп', 'с', 'сл', 'снт', 'ст', 'стр', 'тер', 'туп', 'ул', 'х', 'ш'];
        var words = address.split(" ");
        var dottedWords = words.map(function (word) {
            if (shortTypes.indexOf(word) !== -1) {
                return word + '.';
            } else {
                return word;
            }
        });
        return dottedWords.join(" ");
    }

    var defaultFormatResult = $.Suggestions.prototype.formatResult;

    function formatResult(value, currentValue, suggestion, options) {
        value = dotify(value);
        suggestion.value = value;
        return defaultFormatResult.call(this, value, currentValue, suggestion, options);
    }

    function makeAddressString(address) {
        let address_first_line = join([
            join([address.street_type, address.street], " "),
            join([address.house_type, address.house,
                address.block_type, address.block], " "),
            join([address.flat_type, address.flat], " ")
        ]);
        let address_second_line = join([
            join([address.settlement_type, address.settlement], " "),
            (address.city !== address.region && join([address.city_type, address.city], " ") || ""),
            join([address.area_type, address.area], " "),
            join([address.region_type, address.region], " ")
        ]);

        return [join([address_first_line, address_second_line]), address_first_line, address_second_line];
    }

    function formatSelected(suggestion) {
        let address_strings = makeAddressString(suggestion.data)
        for (let i = 0; i < address_strings.length; i++) {
            address_strings[i] = dotify(address_strings[i])
        }
        $("#id_address_first_line").val(address_strings[1]);
        $("#id_address_second_line").val(address_strings[2]);

        if (suggestion.data.postal_code) {
            $("#id_postal_code").val(suggestion.data.postal_code);
            return dotify(suggestion.data.postal_code + ', ' + suggestion.value);
        } else {
            return dotify(suggestion.value);
        }
    }

    $("#id_address").suggestions({
        token: "fd8b91ff4de0829baf7ff4bb9a5df7483aaa4487",
        type: "ADDRESS",
        formatSelected: formatSelected,
        formatResult: formatResult,
    });
});