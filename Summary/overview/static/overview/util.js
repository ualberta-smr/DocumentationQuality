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
    // form_col.children(".form_row").children(".form").each(function () {
    //     this.style.display = "none"
    // })
    // $(form_id)[0].style.display = "block"
}

function hideForm(form_id, is_submit) {
    let form = $(form_id)
    if (!is_submit || form.valid()) {
        // form[0].style.display = "none"
        $("#form_col")[0].style.display = "none"
        let summary_col = $("#summary_col")[0]
        summary_col.classList.remove("col-md-8")
        summary_col.classList.add("col")
    }
}

function checkOption(select_id) {
    let select = $(select_id)
    let custom_where = $(".custom_where")[0]
    if (select[0].value === "other") {
        custom_where.disabled = false;
        custom_where.style.display = "block";
    } else {
        custom_where.disabled = true;
        custom_where.style.display = "none";
    }
}

function changeWhereSee(where_see_id) {
    let where_see_select = $(where_see_id)[0]
    let where_see_input = $(".custom_where")[0]
    let in_choices = 0;
    for (let i = 0; i < where_see_select.length; i++) {
        if (where_see_input.value === where_see_select[i].value) {
            where_see_select[i].selected = "selected"
            in_choices = 1
        }
    }
    if (!in_choices) {
        where_see_input.disabled = false;
        where_see_input.style.display = "block";
        for (let i = 0; i < where_see_select.length; i++) {
            if (where_see_select[i].value === "other") {
                where_see_select[i].selected = "selected"
            }
        }
    }
    if (in_choices) {
        where_see_input.value = "";
    }
}

function refreshPage() {
    location.reload()
    clearTimeout(refreshInterval)
}

function httpGetAsync() {
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            refreshPage(xmlHttp.responseText);
    }
    let library_url = location.href;
    xmlHttp.open("GET", library_url.split("/").slice(0, -1).join("/") + "/check/" + library_url.split("/").slice(-1), true);
    xmlHttp.send(null);
}