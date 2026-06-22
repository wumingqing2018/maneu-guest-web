$(document).ready(function () {
    // 初始加载详情
    detail_store();
    guest_hide();

    // ---------- 客户信息展开/收起 ----------
    function guest_hide() {
        $("#guest_hide").hide();
        $("#guest_show").show();
        $("#guest_content").slideUp(200);
    }

    function guest_show() {
        $("#guest_hide").show();
        $("#guest_show").hide();
        $("#guest_content").slideDown(200);
    }

    $('#guest_hide').click(function () {
        guest_hide();
    });

    $('#guest_show').click(function () {
        guest_show();
    });

    // ---------- 加载详情数据 ----------
    function detail_store() {
        if (!index_id) {
            $('#loadStatus').text('缺少记录ID').removeClass('status-empty').addClass('status-badge bg-danger text-white');
            return;
        }

        $('#loadStatus').text('加载中...').removeClass('status-loaded').addClass('status-empty');

        $.ajax({
            url: store_detail,
            data: {
                'index_id': index_id,
            },
            success: function (res) {
                console.log('详情数据:', res);
                if (res.status === true) {
                    $('#loadStatus').text('已加载').removeClass('status-empty').addClass('status-loaded');

                    // 填充客户信息
                    var guest = res.content.guest;
                    if (guest && guest.status === true) {
                        var guestData = guest.content;
                        $('#guestRemark').val(guestData.remark || '');
                        $('#phone').val(guestData.phone || '');
                        $('#name').val(guestData.name || '');
                        $('#time').val(guestData.time || '');
                        $('#sex').val(guestData.sex || '');
                        $('#age').val(guestData.age || '');
                        $('#dfh').val(guestData.dfh || '');
                        $('#em').val(guestData.em || '');
                        $('#ot').val(guestData.ot || '');
                        $('#guestSection').addClass('fade-highlight');
                        setTimeout(() => $('#guestSection').removeClass('fade-highlight'), 1500);
                    }

                    // 填充产品订单
                    var store = res.content.store;
                    if (store && store.status === true && store.content && store.content.length > 0) {
                        $('#storeStatus').text('已加载').removeClass('status-empty').addClass('status-loaded');
                        var loopIndex = 0;
                        $.each(store.content[0], function (key, val) {
                            $('.store-key').eq(loopIndex).val(key || '');
                            $('.store-val').eq(loopIndex).val(val || '');
                            loopIndex++;
                        });
                        // 清空剩余未使用的输入框
                        for (var i = loopIndex; i < 10; i++) {
                            $('.store-key').eq(i).val('');
                            $('.store-val').eq(i).val('');
                        }
                        $('#storeSection').addClass('fade-highlight');
                        setTimeout(() => $('#storeSection').removeClass('fade-highlight'), 1500);
                    } else {
                        $('#storeStatus').text('无订单数据').removeClass('status-loaded').addClass('status-empty');
                    }
                } else {
                    $('#loadStatus').text('加载失败').removeClass('status-loaded').addClass('status-empty');
                    alert('加载详情失败：' + (res.message || '未知错误'));
                }
            },
            error: function (xhr) {
                console.log('加载错误:', xhr);
                $('#loadStatus').text('网络错误').removeClass('status-loaded').addClass('status-empty');
                alert('网络错误，请稍后重试');
            }
        });
    }

    // ---------- 更新客户信息 ----------
    $('#guestUpdate').click(function () {
        if (!index_id) {
            alert('缺少记录ID，无法更新');
            return;
        }

        var btn = $(this);
        btn.prop('disabled', true).html('<i class="bi bi-hourglass-split"></i> 更新中...');

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
                console.log('客户更新结果:', res);
                if (res.status === true) {
                    alert('客户信息更新成功');
                    $('#guestSection').addClass('fade-highlight');
                    setTimeout(() => $('#guestSection').removeClass('fade-highlight'), 1500);
                } else {
                    alert('更新失败：' + (res.message || '未知错误'));
                }
            },
            error: function (xhr) {
                console.log('更新错误:', xhr);
                alert('网络错误，请稍后重试');
            },
            complete: function () {
                btn.prop('disabled', false).html('<i class="bi bi-check-lg"></i> 更新客户信息');
            }
        });
    });

    // ---------- 更新产品订单 ----------
    $('#storeUpdate').click(function () {
        if (!index_id) {
            alert('缺少记录ID，无法更新');
            return;
        }

        var btn = $(this);
        btn.prop('disabled', true).html('<i class="bi bi-hourglass-split"></i> 更新中...');

        // 构建10组键值对数据
        var data = [{
            [$("#key10").val() || '']: $("#val10").val() || '',
            [$("#key20").val() || '']: $("#val20").val() || '',
            [$("#key30").val() || '']: $("#val30").val() || '',
            [$("#key40").val() || '']: $("#val40").val() || '',
            [$("#key50").val() || '']: $("#val50").val() || '',
            [$("#key60").val() || '']: $("#val60").val() || '',
            [$("#key70").val() || '']: $("#val70").val() || '',
            [$("#key80").val() || '']: $("#val80").val() || '',
            [$("#key90").val() || '']: $("#val90").val() || '',
            [$("#key00").val() || '']: $("#val00").val() || '',
        }];
        console.log('订单更新数据:', data);

        $.ajax({
            url: store_update,
            method: 'GET',
            data: {
                index_id: index_id,
                storeContent: JSON.stringify(data),
            },
            success: function (res) {
                console.log('订单更新结果:', res);
                if (res.status === true) {
                    alert('产品订单更新成功');
                    $('#storeStatus').text('已加载').removeClass('status-empty').addClass('status-loaded');
                    $('#storeSection').addClass('fade-highlight');
                    setTimeout(() => $('#storeSection').removeClass('fade-highlight'), 1500);
                } else {
                    alert('更新失败：' + (res.message || '未知错误'));
                }
            },
            error: function (xhr) {
                console.log('更新错误:', xhr);
                alert('网络错误，请稍后重试');
            },
            complete: function () {
                btn.prop('disabled', false).html('<i class="bi bi-check-lg"></i> 更新产品订单');
            }
        });
    });

    // ---------- 删除记录 ----------
    $('#delete').click(function () {
        if (!index_id) {
            alert('缺少记录ID，无法删除');
            return;
        }

        if (!confirm("确定要删除这条定制记录吗？\n此操作不可恢复，请谨慎操作。")) {
            return false;
        }

        var btn = $(this);
        btn.prop('disabled', true).html('<i class="bi bi-hourglass-split"></i> 删除中...');

        $.ajax({
            url: store_delete,
            data: {
                'index_id': index_id,
            },
            success: function (res) {
                console.log('删除结果:', res);
                if (res.status === true) {
                    alert('删除成功');
                    // 延迟跳转回列表页
                    setTimeout(function () {
                        window.location.href = "{% url 'maneu_store:index' %}";
                    }, 500);
                } else {
                    alert('删除失败：' + (res.message || '未知错误'));
                    btn.prop('disabled', false).html('<i class="bi bi-trash3"></i> 删除此记录');
                }
            },
            error: function (xhr) {
                console.log('删除错误:', xhr);
                alert('网络错误，请稍后重试');
                btn.prop('disabled', false).html('<i class="bi bi-trash3"></i> 删除此记录');
            }
        });
    });

    // ---------- 生成二维码 ----------
    $('#generate_qr_code').click(function () {
        if (!index_id) {
            alert('缺少记录ID，无法生成二维码');
            return;
        }

        var btn = $(this);
        btn.prop('disabled', true).html('<i class="bi bi-hourglass-split"></i> 生成中...');

        $.ajax({
            url: store_QRcode,
            data: {
                'index_id': index_id,
            },
            method: 'GET',
            xhrFields: {
                responseType: 'blob'
            },
            success: function (blob) {
                const blobUrl = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = blobUrl;
                link.download = 'qrcode_' + index_id + '.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(blobUrl);
                alert('二维码已下载');
            },
            error: function (xhr, status, error) {
                console.error('二维码下载失败:', error);
                alert('二维码生成失败，请稍后重试');
            },
            complete: function () {
                btn.prop('disabled', false).html('<i class="bi bi-qr-code"></i> 二维码');
            }
        });
    });

});