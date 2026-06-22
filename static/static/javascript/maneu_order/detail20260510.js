$(document).ready(function () {
    // ========== 折叠交互 ==========

    // 验光报告高级参数
    $('#toggleReport').click(function () {
        $('#reportExtra').slideToggle(200);
        const icon = $(this).find('i');
        icon.toggleClass('bi-chevron-down bi-chevron-up');
    });

    // 客户信息详细参数
    $('#toggleGuest').click(function () {
        $('#guestExtra').slideToggle(200);
        const icon = $(this).find('i');
        icon.toggleClass('bi-chevron-down bi-chevron-up');
    });

    // ========== 通用更新函数 ==========
    function collectProductData() {
        const products = [];
        $('.product-row').each(function () {
            products.push({
                arg10: $(this).find('.arg10').val(),
                arg11: $(this).find('.arg11').val(),
                arg12: $(this).find('.arg12').val(),
                arg13: $(this).find('.arg13').val(),
                arg14: $(this).find('.arg14').val()
            });
        });
        return products;
    }

    function ajaxUpdate(url, data, successMsg) {
        $.ajax({
            url: url,
            method: 'GET',
            data: data,
            success: function (res) {
                alert(res.status === true ? successMsg : '更新失败：' + (res.message || ''));
            },
            error: function () {
                alert('网络错误');
            }
        });
    }

    // 更新订单（时间、订单备注、产品）共用一个函数
    function updateOrder() {
        const data = {
            index_id: index_id,
            time: $('#time').val(),
            orderRemark: $('#remark').val(),
            content: JSON.stringify(collectProductData())
        };
        ajaxUpdate(order_update, data, '订单信息更新成功');
    }

    // ========== 按钮事件绑定 ==========
    $('#timeUpdate').click(updateOrder);
    $('#remarkUpdate').click(updateOrder);
    $('#orderUpdate').click(updateOrder);

    $('#guestUpdate').click(function () {
        ajaxUpdate(guest_update, {
            index_id: index_id,
            time: $('#time').val(),
            name: $('#name').val(),
            phone: $('#phone').val(),
            age: $('#age').val(),
            sex: $('#sex').val(),
            dfh: $('#dfh').val(),
            ot: $('#ot').val(),
            em: $('#em').val(),
            guestRemark: $('#remark').val()
        }, '客户信息更新成功');
    });

    $('#reportUpdate').click(function () {
        ajaxUpdate(report_update, {
            index_id: index_id,
            plan: $('#PLAN').val(),
            pd: $('#PD').val(),
            od_sph: $('#OD_SPH').val(), os_sph: $('#OS_SPH').val(),
            od_cyl: $('#OD_CYL').val(), os_cyl: $('#OS_CYL').val(),
            od_ax: $('#OD_AX').val(), os_ax: $('#OS_AX').val(),
            od_va: $('#OD_VA').val(), os_va: $('#OS_VA').val(),
            od_bc: $('#OD_BC').val(), os_bc: $('#OS_BC').val(),
            od_add: $('#OD_ADD').val(), os_add: $('#OS_ADD').val(),
            od_pr: $('#OD_PR').val(), os_pr: $('#OS_PR').val(),
            od_fr: $('#OD_FR').val(), os_fr: $('#OS_FR').val(),
            od_al: $('#OD_AL').val(), os_al: $('#OS_AL').val(),
            od_ak: $('#OD_AK').val(), os_ak: $('#OS_AK').val(),
            od_ad: $('#OD_AD').val(), os_ad: $('#OS_AD').val(),
            od_cct: $('#OD_CCT').val(), os_cct: $('#OS_CCT').val(),
            od_lt: $('#OD_LT').val(), os_lt: $('#OS_LT').val(),
            od_vt: $('#OD_VT').val(), os_vt: $('#OS_VT').val()
        }, '验光报告更新成功');
    });

    // 删除订单
    $('#delete').click(function () {
        if (!confirm('确定要删除这条订单吗？此操作不可恢复。')) return;
        $.ajax({
            url: order_delete,
            data: {index_id: index_id},
            success: function (res) {
                if (res.status) {
                    alert('删除成功');
                    window.location.href = "{% url 'maneu_order:index' %}";
                } else {
                    alert('删除失败：' + (res.message || ''));
                }
            },
            error: function () {
                alert('网络错误');
            }
        });
    });

    // 生成二维码
    $('#generate_qr_code').click(function () {
        $.ajax({
            url: order_QRcode,
            data: {index_id: index_id},
            method: 'GET',
            xhrFields: {responseType: 'blob'},
            success: function (blob) {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = index_id + '.png';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            },
            error: function () {
                alert('二维码生成失败');
            }
        });
    });

    // ========== 加载详情 ==========
    function loadDetail() {
        $.ajax({
            url: order_detail,
            data: {index_id: index_id},
            success: function (res) {
                if (res.status === true) {
                    const {guest, report, order} = res.content;
                    // 填充客户
                    if (guest && guest.status === true) {
                        const g = guest.content;
                        $('#time').val(g.time);
                        $('#name').val(g.name);
                        $('#phone').val(g.phone);
                        $('#sex').val(g.sex);
                        $('#age').val(g.age);
                        $('#dfh').val(g.dfh);
                        $('#em').val(g.em);
                        $('#ot').val(g.ot);
                        $('#guestRemark').val(g.remark);
                        $('#remark').val(g.remark); // 订单备注默认同步
                        $('#guestLoadStatus').removeClass('status-empty').addClass('status-loaded').text('加载成功');
                    } else {
                        $('#guestLoadStatus').removeClass('status-empty').addClass('status-warning').text('加载失败');
                    }
                    // 填充验光报告
                    if (report && report.status === true) {
                        const r = report.content;
                        $('#PLAN').val(r.plan);
                        $('#PD').val(r.pd);
                        $('#reportRemark').val(r.remark);
                        ['OD', 'OS'].forEach(eye => {
                            ['SPH', 'CYL', 'AX', 'VA', 'BC', 'ADD'].forEach(f => {
                                $(`#${eye}_${f}`).val(r[`${eye.toLowerCase()}_${f.toLowerCase()}`] || '');
                            });
                        });
                        ['OD', 'OS'].forEach(eye => {
                            ['PR', 'FR', 'AL', 'AK', 'AD', 'CCT', 'LT', 'VT'].forEach(f => {
                                $(`#${eye}_${f}`).val(r[`${eye.toLowerCase()}_${f.toLowerCase()}`] || '');
                            });
                        });
                        $('#reportLoadStatus').removeClass('status-empty').addClass('status-loaded').text('加载成功');
                    } else {
                        $('#reportLoadStatus').removeClass('status-empty').addClass('status-warning').text('加载失败');
                    }
                    // 填充产品
                    if (order && order.status === true) {
                        const products = order.content; // 数组
                        if (Array.isArray(products)) {
                            $('.product-row').each(function (i) {
                                if (i < products.length) {
                                    const p = products[i];
                                    $(this).find('.arg10').val(p.arg10);
                                    $(this).find('.arg11').val(p.arg11);
                                    $(this).find('.arg12').val(p.arg12);
                                    $(this).find('.arg13').val(p.arg13);
                                    $(this).find('.arg14').val(p.arg14);
                                }
                            });
                        }
                        $('#storeLoadStatus').removeClass('status-empty').addClass('status-loaded').text('加载成功');
                    } else {
                        $('#storeLoadStatus').removeClass('status-empty').addClass('status-warning').text('加载失败');
                    }
                } else {
                    alert('加载详情失败');
                }
            },
            error: function () {
                alert('网络错误，无法加载订单详情');
            }
        });
    }

    loadDetail();
});
