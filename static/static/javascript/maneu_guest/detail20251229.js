$(document).ready(function () {
    detail_guest(function (data) {
        console.log(data)
    })


    $('#delete').click(function () {
        if (confirm("确定要删除记录吗？")) {
            $.ajax({
                url: guest_delete,
                data: {
                    'index_id': index_id
                },
                success: function (res) {
                    if (data === true) {
                        alert('删除成功')
                        window.location.href = guest_index
                    } else {
                        alert(data.message)
                    }
                },
                error: function () {
                    alert('order,网络出错')
                }
            })
        } else {
            return false;
        }
    })
    $('#update').click(function () {
        if (confirm("确定要修改记录吗？")) {
            update_guest(function (data) {
                if (data.status === true) {
                    alert('修改成功')
                } else {
                    alert(data.message)
                }
            })
        } else {
            return false;
        }
    })


    function detail_guest(callback) {
        $.ajax({
            url: guest_detail,
            data: {
                'index_id': index_id
            },
            success: function (res) {
                content = res.content
                $('#time').val(content.time)
                $('#name').val(content.name)
                $('#phone').val(content.phone)
                $('#sex').val(content.sex)
                $('#age').val(content.age)
                $('#DFH').val(content.dfh)
                $('#EM').val(content.em)
                $('#OT').val(content.ot)
                callback(res); // 第一个参数为null表示没有错误，第二个参数为请求的数据
            },
            error: function (res) {
                callback(false); // 第一个参数为null表示没有错误，第二个参数为请求的数据
            }
        })
    }

    function delete_guest(callback) {
        $.ajax({
            url: guest_delete,
            data: {
                'index_id': index_id
            },
            success: function (res) {
                callback(res)
            },
            error: function () {
                callback({"status": false, 'message': 'order,网络出错'})
            }
        })
    }

    function update_guest(callback) {
        $.ajax({
            url: guest_update,
            method: 'GET',
            data: {
                'index_id': index_id,
                'remark': $("#remark").val(),
                'time': $("#time").val(),
                'name': $("#name").val(),
                'call': $("#call").val(),
                'age': $("#age").val(),
                'sex': $("#sex").val(),
                'DFH': $("#DFH").val(),
                'OT': $("#OT").val(),
                'EM': $("#EM").val(),
            },
            success: function (res) {
                callback(res)
            },
            error: function () {
                callback({"status": false, 'message': 'guest,网络出错'})
            }
        })
    }
});
