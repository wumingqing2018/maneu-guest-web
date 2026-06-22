$(document).ready(function () {
    // 折叠客户高级字段
    $('#toggleGuest').click(function () {
        $('#guestExtra').slideToggle(200);
        $(this).find('i').toggleClass('bi-chevron-down bi-chevron-up');
        $(this).html($(this).find('i')[0].outerHTML + ' ' + ($('#guestExtra').is(':visible') ? '详细参数' : '详细参数'));
    });

    // 折叠验光报告高级参数
    $('#toggleReport').click(function () {
        $('#reportExtra').slideToggle(200);
        $(this).find('i').toggleClass('bi-chevron-down bi-chevron-up');
        $(this).html($(this).find('i')[0].outerHTML + ' ' + ($('#reportExtra').is(':visible') ? '详细参数' : '详细参数'));
    });

    // 提交订单
    $('#insert').click(function () {
        const store = [];
        $('.product-row').each(function () {
            store.push({
                arg10: $(this).find('.arg10').val(),
                arg11: $(this).find('.arg11').val(),
                arg12: $(this).find('.arg12').val(),
                arg13: $(this).find('.arg13').val(),
                arg14: $(this).find('.arg14').val()
            });
        });

        $.ajax({
            url: order_insert_api,
            method: 'GET',
            data: {
                content: JSON.stringify(store),
                time: $('#time').val(),
                name: $('#name').val(),
                phone: $('#phone').val(),
                remark: $('#remark').val(),
                age: $('#age').val(),
                sex: $('#sex').val(),
                dfh: $('#dfh').val(),
                ot: $('#ot').val(),
                em: $('#em').val(),
                plan: $('#PLAN').val(),
                pd: $('#PD').val(),
                od_va: $('#OD_VA').val(),
                od_sph: $('#OD_SPH').val(),
                od_cyl: $('#OD_CYL').val(),
                od_ax: $('#OD_AX').val(),
                od_pr: $('#OD_PR').val(),
                od_fr: $('#OD_FR').val(),
                od_add: $('#OD_ADD').val(),
                od_al: $('#OD_AL').val(),
                od_ak: $('#OD_AK').val(),
                od_ad: $('#OD_AD').val(),
                od_cct: $('#OD_CCT').val(),
                od_lt: $('#OD_LT').val(),
                od_vt: $('#OD_VT').val(),
                od_bc: $('#OD_BC').val(),
                os_va: $('#OS_VA').val(),
                os_sph: $('#OS_SPH').val(),
                os_cyl: $('#OS_CYL').val(),
                os_ax: $('#OS_AX').val(),
                os_pr: $('#OS_PR').val(),
                os_fr: $('#OS_FR').val(),
                os_add: $('#OS_ADD').val(),
                os_al: $('#OS_AL').val(),
                os_ak: $('#OS_AK').val(),
                os_ad: $('#OS_AD').val(),
                os_cct: $('#OS_CCT').val(),
                os_lt: $('#OS_LT').val(),
                os_vt: $('#OS_VT').val(),
                os_bc: $('#OS_BC').val()
            },
            success: function (res) {
                if (res.status === true) {
                    alert('订单提交成功');
                } else {
                    alert(res.message || '提交失败，请稍后重试');
                }
            },
            error: function () {
                alert('提交失败，网络错误，请稍后重试');
            }
        });
    });
});
