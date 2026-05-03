// XSS 防护函数
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function (m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

$(document).ready(function () {
    var $card = $('#verify-card');

    // 如果没有提供 index_id，显示提示信息
    if (!index_id || index_id.trim() === "") {
        $card.html('<div class="info-placeholder"> 未提供订单号，请使用正确的链接访问</div>');
        return;
    }

    // 显示加载状态
    $card.html('<div class="loading-placeholder"><span class="spinner"></span> 正在验证授权信息...</div>');

    $.ajax({
        url: verify_order_url,
        method: "GET",
        data: {index_id: index_id},
        dataType: "json",
        timeout: 10000,
        success: function (res) {
            console.log(res);
            renderVerifyResult(res);
        },
        error: function (xhr, status, error) {
            console.error("AJAX Error:", status, error);
            $card.html(`
                    <div class="status-badge fail">请求失败</div>
                    <div class="fail-message">网络错误或服务器无响应，请刷新页面后重试。</div>
                `);
        }
    });

    // 渲染验证结果（适配后端数据结构：res.content.time / res.content.data）
    function renderVerifyResult(data) {
        $card.empty(); // 清空卡片

        // 判断状态（兼容布尔值或字符串 'true'）
        var isSuccess = (data.status === true || data.status === 'true');
        var content = data.content || {};
        var timeStr = content.time || '';
        var productList = content.data || [];

        if (isSuccess && productList.length > 0) {
            // 成功状态
            $card.append('<div class="status-badge success"> 正品验证通过</div>');
            if (timeStr) {
                $card.append(`<div class="time-section">购买时间 <strong>${escapeHtml(timeStr)}</strong></div>`);
            }

            // 遍历每个产品
            $.each(productList, function (index, item) {
                // 过滤掉键为空或值为空的属性，同时排除空字符串键
                var entries = Object.entries(item).filter(function (entry) {
                    var key = entry[0];
                    var val = entry[1];
                    return key && key.trim() !== "" && val && val.trim() !== "";
                });
                if (entries.length === 0) return;

                var $product = $('<div class="product-item"></div>');
                var firstEntry = entries[0];

                // 第一个属性作为主标题特殊展示
                if (firstEntry) {
                    $product.append(`
                            <div class="first-property">
                                <span class="first-key">${escapeHtml(firstEntry[0])}</span>
                                <span class="divider">—</span>
                                <span class="first-val">${escapeHtml(firstEntry[1])}</span>
                            </div>
                        `);
                }

                // 其余属性采用网格排列
                if (entries.length > 1) {
                    var $grid = $('<div class="props-grid"></div>');
                    for (var i = 1; i < entries.length; i++) {
                        $grid.append(`
                                <div class="prop-item">
                                    <span class="prop-key">${escapeHtml(entries[i][0])}</span>
                                    <span class="prop-val">${escapeHtml(entries[i][1])}</span>
                                </div>
                            `);
                    }
                    $product.append($grid);
                }

                $card.append($product);
            });
        } else {
            // 失败状态
            $card.append('<div class="status-badge fail"> 验证失败</div>');
            var message = (data && data.message) ? escapeHtml(data.message) : '未查询到授权信息，请核对购买渠道。';
            $card.append(`<div class="fail-message">${message}</div>`);
        }
    }
});