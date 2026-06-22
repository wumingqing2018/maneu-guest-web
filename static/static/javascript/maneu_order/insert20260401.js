$(document).ready(function () {
    report_hide()
    guest_hide()
    $('#guest_hide').click(function () {
        guest_hide()
    })
    $('#guest_show').click(function () {
        guest_show()
    })
    $('#report_hide').click(function () {
        report_hide()
    })
    $('#report_show').click(function () {
        report_show()
    })

    function report_hide() {
        $("#report_hide").hide()
        $("#report_show").show()
        $("#OD_VA").hide()
        $("#OD_PR").hide()
        $("#OD_FR").hide()
        $("#OD_AL").hide()
        $("#OD_AK").hide()
        $("#OD_AD").hide()
        $("#OD_CCT").hide()
        $("#OD_LT").hide()
        $("#OD_VT").hide()
        $("#OD_BC").hide()
        $("#OS_VA").hide()
        $("#OS_PR").hide()
        $("#OS_FR").hide()
        $("#OS_AL").hide()
        $("#OS_AK").hide()
        $("#OS_AD").hide()
        $("#OS_CCT").hide()
        $("#OS_LT").hide()
        $("#OS_VT").hide()
        $("#OS_BC").hide()
    }

    function report_show() {
        $("#report_hide").show()
        $("#report_show").hide()
        $("#OD_VA").show()
        $("#OD_PR").show()
        $("#OD_FR").show()
        $("#OD_AL").show()
        $("#OD_AK").show()
        $("#OD_AD").show()
        $("#OD_CCT").show()
        $("#OD_LT").show()
        $("#OD_VT").show()
        $("#OD_BC").show()
        $("#OS_VA").show()
        $("#OS_PR").show()
        $("#OS_FR").show()
        $("#OS_AL").show()
        $("#OS_AK").show()
        $("#OS_AD").show()
        $("#OS_CCT").show()
        $("#OS_LT").show()
        $("#OS_VT").show()
        $("#OS_BC").show()
    }

    function guest_hide() {
        $("#guest_hide").hide()
        $("#guest_show").show()
        $("#guest_content").hide()
    }

    function guest_show() {
        $("#guest_hide").show()
        $("#guest_show").hide()
        $("#guest_content").show()
    }

    $('#insert').click(function () {
        store = []
        $(".store").each(function () {
            data = {
                arg10: $(this).find(".arg10").val(),
                arg11: $(this).find(".arg11").val(),
                arg12: $(this).find(".arg12").val(),
                arg13: $(this).find(".arg13").val(),
                arg14: $(this).find(".arg14").val(),
            };
            store.push(data)
        });
        $.ajax({
            url: order_insert_api,
            method: 'GET',
            data: {
                content: JSON.stringify(store),


                time: $("#time").val(),
                name: $("#name").val(),
                phone: $("#phone").val(),
                remark: $("#remark").val(),


                age: $("#age").val(),
                sex: $("#sex").val(),
                dfh: $("#dfh").val(),
                ot: $("#ot").val(),
                em: $("#em").val(),


                plan: $("#PLAN").val(),
                pd: $("#PD").val(),
                od_va: $("#OD_VA").val(),
                od_sph: $("#OD_SPH").val(),
                od_cyl: $("#OD_CYL").val(),
                od_ax: $("#OD_AX").val(),
                od_pr: $("#OD_PR").val(),
                od_fr: $("#OD_FR").val(),
                od_add: $("#OD_ADD").val(),
                od_al: $("#OD_AL").val(),
                od_ak: $("#OD_AK").val(),
                od_ad: $("#OD_AD").val(),
                od_cct: $("#OD_CCT").val(),
                od_lt: $("#OD_LT").val(),
                od_vt: $("#OD_VT").val(),
                od_bc: $("#OD_BC").val(),
                os_va: $("#OS_VA").val(),
                os_sph: $("#OS_SPH").val(),
                os_cyl: $("#OS_CYL").val(),
                os_ax: $("#OS_AX").val(),
                os_pr: $("#OS_PR").val(),
                os_fr: $("#OS_FR").val(),
                os_add: $("#OS_ADD").val(),
                os_al: $("#OS_AL").val(),
                os_ak: $("#OS_AK").val(),
                os_ad: $("#OS_AD").val(),
                os_cct: $("#OS_CCT").val(),
                os_lt: $("#OS_LT").val(),
                os_vt: $("#OS_VT").val(),
                os_bc: $("#OS_BC").val(),
            },
            success: function (res) {
                console.log(res)
                if (res.status === true) {
                    alert('更新成功')
                } else {
                    alert('更新失败')
                }
            },
            error: function (res) {
                console.log(res)
                alert('网络错误')
            }
        })
    });

});
