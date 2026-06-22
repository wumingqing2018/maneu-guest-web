$(document).ready(function () {
    $('#update').click(function () {
        $.ajax({
            url: api_updata,
            method: 'GET',
            data: {
                remark: $("[name='remark']").val(),
                time: $("[name='time']").val(),
                name: $("[name='name']").val(),
                call: $("[name='call']").val(),
                age: $("[name='age']").val(),
                dfh: $("[name='dfh']").val(),
                sex: $("[name='sex']").val(),
                ot: $("[name='ot']").val(),
                em: $("[name='em']").val(),
                id: guest_id,
            },
            success: function (res) {
                if (res.status === true) {
                    alert('更新成功')
                    guest_detail(guest_id)
                } else {
                    alert('更新失败')
                }
            }
        })
    })

    function guest_detail(guest_id) {
        $.ajax({
            url: api_detail,
            method: 'GET',
            data: {
                id: guest_id
            },
            success: function (res) {
                if (res.status === true) {
                    $("[name='remark']").val(res.data.remark)
                    $("[name='time']").val(res.data.time)
                    $("[name='name']").val(res.data.name)
                    $("[name='call']").val(res.data.phone)
                    $("[name='age']").val(res.data.age)
                    $("[name='dfh']").val(res.data.dfh)
                    $("[name='sex']").val(res.data.sex)
                    $("[name='ot']").val(res.data.ot)
                    $("[name='em']").val(res.data.em)
                } else {
                    alert(res.message)
                }
            }
        })
    }

    guest_detail(guest_id)
})