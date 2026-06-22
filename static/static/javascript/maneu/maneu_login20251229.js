$(document).ready(function () {
    $("#sendsms-btn").click(function () {
        $.ajax({
            url: sendsms,
            method: 'GET',
            data: {
                call: $("#call").val(),
            },
            success: function (res) {
                if (res.status === true) {
                    $("#wait-btn").show();
                    $("#sendsms-btn").hide();
                    setTimeout(function () {
                        $("#wait-btn").hide();
                        $("#sendsms-btn").show();
                    }, 60000);
                } else {
                    $("#msg").text("发送短信失败" + res.message)
                }
            }
        })
    })
    $("#login-btn").click(function () {
        $.ajax({
            url: login_verify,
            method: 'GET',
            data: {
                call: $("#call").val(),
                code: $("#code").val()
            },
            success: function (res) {
                if (res.status === true) {
                    window.location.href = maneu_order_index
                } else {
                    $("#msg").text(res.message)
                }
            },
        })
    })
    $("#code").keyup(function () {
        if ($("#code").val() === '') {
            $("#login-hold").show()
            $("#login-btn").hide()
        } else {
            $("#login-hold").hide()
            $("#login-btn").show()
        }
    })
})