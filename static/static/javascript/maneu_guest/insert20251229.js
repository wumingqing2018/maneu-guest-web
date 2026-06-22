$(document).ready(function () {
    $("#insert").click(function () {
        $.ajax({
            url: guest_api,
            method: 'GET',
            data: {
                remark: $("[name='remark']").val(),
                time: $("[name='time']").val(),
                name: $("[name='name']").val(),
                phone: $("[name='phone']").val(),
                age: $("[name='age']").val(),
                sex: $("[name='sex']").val(),
                DFH: $("[name='DFH']").val(),
                OT: $("[name='OT']").val(),
                EM: $("[name='EM']").val(),
            },
            success: function (res) {
                if (res.status === true) {
                    alert('提交成功,返回上一页')
                    window.location.href = guest_index
                } else {
                    alert("提交失败" + res.message)
                }
            }
        })
    })
})