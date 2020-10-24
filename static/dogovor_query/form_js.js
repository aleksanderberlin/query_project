$('input[type=radio][name$=_subject-question]').change(function () {
    let other_input = $('input[id$=_subject-other_text]')
    if (this.value === 'Другое') {
        other_input.prop('readonly', false);
        other_input.prop('required', true);
    } else {
        other_input.val('')
        other_input.prop('readonly', true);
        other_input.prop('required', false);
    }
});
