function showForm(form_id) {
    let summary_col = $("#summary_col")[0]
    let form_col = $("#form_col")
    if (summary_col.classList.contains("col")) {
        summary_col.classList.remove("col")
        summary_col.classList.add("col-md-8")
    }
    if (form_col[0].style.display === "none") {
        form_col[0].style.display = "block"
    }
    form_col.children(".form").each(function () {
        this.style.display = "none"
    })
    $(form_id)[0].style.display = "block"
}

function hideForm(form_id, is_submit) {
    let form = $(form_id)
    if (!is_submit || form.valid()) {
        form[0].style.display = "none"
        $("#form_col")[0].style.display = "none"
        let summary_col = $("#summary_col")[0]
        summary_col.classList.remove("col-md-8")
        summary_col.classList.add("col")
    }
}