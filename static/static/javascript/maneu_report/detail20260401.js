$(document).ready(function () {
    detail_report()
    report_hide()
    guest_hide()


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


    function detail_report() {
        $.ajax({
            url: report_detail,
            data: {
                index_id: index_id,
            },
            success: function (res) {
                console.log(res)
                if (res.status === true) {

                    guest = res.content.guest
                    if (guest.status === true) {
                        $('#guestRemark').val(guest.content.remark)
                        $('#name').val(guest.content.name)
                        $('#phone').val(guest.content.phone)
                        $('#sex').val(guest.content.sex)
                        $('#age').val(guest.content.age)
                        $('#dfh').val(guest.content.dfh)
                        $('#em').val(guest.content.em)
                        $('#ot').val(guest.content.ot)
                    }

                    report = res.content.report
                    if (report.status === true) {
                        $('#time').val(report.content.time)
                        $('#reportRemark').val(report.content.remark)
                        $('#PD').val(report.content.pd)
                        $('#PLAN').val(report.content.plan)

                        $('#OS_AX').val(report.content.os_ax)
                        $('#OS_AD').val(report.content.os_ad)
                        $('#OS_ADD').val(report.content.os_add)
                        $('#OS_AK').val(report.content.os_ak)
                        $('#OS_AL').val(report.content.os_al)
                        $('#OS_BC').val(report.content.os_bc)
                        $('#OS_CCT').val(report.content.os_cct)
                        $('#OS_CYL').val(report.content.os_cyl)
                        $('#OS_FR').val(report.content.os_fr)
                        $('#OS_LT').val(report.content.os_lt)
                        $('#OS_PR').val(report.content.os_pr)
                        $('#OS_SPH').val(report.content.os_sph)
                        $('#OS_VA').val(report.content.os_va)
                        $('#OS_VT').val(report.content.os_vt)

                        $('#OD_AX').val(report.content.od_ax)
                        $('#OD_AD').val(report.content.od_ad)
                        $('#OD_ADD').val(report.content.od_add)
                        $('#OD_AK').val(report.content.od_ak)
                        $('#OD_AL').val(report.content.od_al)
                        $('#OD_BC').val(report.content.od_bc)
                        $('#OD_CCT').val(report.content.od_cct)
                        $('#OD_CYL').val(report.content.od_cyl)
                        $('#OD_FR').val(report.content.od_fr)
                        $('#OD_LT').val(report.content.od_lt)
                        $('#OD_PR').val(report.content.od_pr)
                        $('#OD_SPH').val(report.content.od_sph)
                        $('#OD_VA').val(report.content.od_va)
                        $('#OD_VT').val(report.content.od_vt)
                    }
                }
            }
        })
    }


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


    $('#delete').click(function () {
        if (confirm("确定要删除记录吗？")) {
            $.ajax({
                url: report_delete,
                data: {
                    index_id: index_id,
                },
                success: function (res) {
                    console.log(res)
                    if (res.status === true) {
                        alert('删除成功')
                    } else {
                        alert('删除失败')
                    }
                },
                error: function (res) {
                    console.log(res)
                    alert('网络错误')
                }
            })
        } else {
            return false;
        }
    })


    $('#reportUpdate').click(function update_report() {
        $.ajax({
            url: report_update,
            method: "GET",
            data: {
                index_id: index_id,
                plan: $("#PLAN").val(),
                pd: $("#PD").val(),
                od_va: $("#OD_VA").val(),
                os_va: $("#OS_VA").val(),
                od_sph: $("#OD_SPH").val(),
                os_sph: $("#OS_SPH").val(),
                od_cyl: $("#OD_CYL").val(),
                os_cyl: $("#OS_CYL").val(),
                od_ax: $("#OD_AX").val(),
                os_ax: $("#OS_AX").val(),
                od_pr: $("#OD_PR").val(),
                os_pr: $("#OS_PR").val(),
                od_fr: $("#OD_FR").val(),
                os_fr: $("#OS_FR").val(),
                od_add: $("#OD_ADD").val(),
                os_add: $("#OS_ADD").val(),
                od_al: $("#OD_AL").val(),
                os_al: $("#OS_AL").val(),
                od_ak: $("#OD_AK").val(),
                os_ak: $("#OS_AK").val(),
                od_ad: $("#OD_AD").val(),
                os_ad: $("#OS_AD").val(),
                od_cct: $("#OD_CCT").val(),
                os_cct: $("#OS_CCT").val(),
                od_lt: $("#OD_LT").val(),
                os_lt: $("#OS_LT").val(),
                od_vt: $("#OD_VT").val(),
                os_vt: $("#OS_VT").val(),
                od_bc: $("#OD_BC").val(),
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
    })


    $('#guestUpdate').click(function update_guest() {
        $.ajax({
            url: guest_update,
            method: 'GET',
            data: {
                index_id: index_id,
                guestRemark: $("#guestRemark").val(),
                phone: $("#phone").val(),
                time: $("#time").val(),
                name: $("#name").val(),
                age: $("#age").val(),
                sex: $("#sex").val(),
                dfh: $("#dfh").val(),
                ot: $("#ot").val(),
                em: $("#em").val(),
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
    })
});
