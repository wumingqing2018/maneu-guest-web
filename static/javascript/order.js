$(document).ready(function () {
    var $card = $('#verify-card');

    // 如果没有提供 index_id，显示提示信息
    if (!index_id || index_id.trim() === "") {
        $card.html('<div class="info-placeholder">🔍 未提供订单号，请使用正确的链接访问</div>');
        return;
    }

    // 显示加载状态
    $card.html('<div class="loading-placeholder"><span class="spinner"></span> 正在验证授权信息...</div>');

    // 发起 AJAX 请求
    $.ajax({
        url: verify_order_url,
        method: "GET",
        data: {index_id: index_id},
        dataType: "json",
        timeout: 10000,
        success: function (res) {
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

    // 渲染验证结果 (XSS 安全)
    function renderVerifyResult(data) {
        $card.empty(); // 清空卡片

        // 判断状态（兼容字符串和布尔）
        var isSuccess = (data.status === true || data.status === "true");

        if (isSuccess) {
            // 成功状态
            $card.append('<div class="status-badge success">正品验证通过</div>');
            var timeStr = data.content && data.content.time ? escapeHtml(data.content.time) : '';
            if (timeStr) {
                $card.append(`<div class="time-section">购买时间: <strong>${timeStr}</strong></div>`);
            }

            var productList = (data.content && data.content.data) ? data.content.data : [];
            var hasValidProduct = false;

            $.each(productList, function (idx, item) {
                // 检查是否有有效内容（非空且不是占位符“无”）
                var isValid = (item.arg10 && item.arg10 !== '无') ||
                    (item.arg11 && item.arg11 !== '无') ||
                    (item.arg12 && item.arg12 !== '无') ||
                    (item.arg13 && item.arg13 !== '无') ||
                    (item.arg14 && item.arg14 !== '无');
                if (!isValid) return;

                hasValidProduct = true;
                var $product = $('<div class="product-item"></div>');
                var productName = (item.arg10 && item.arg10 !== '无') ? escapeHtml(item.arg10) : '未命名商品';

                // 标题行
                $product.append(`
                        <div class="product-title-row">
                            <span class="product-name">${productName}</span>
                            <span class="product-qty">×1</span>
                        </div>
                    `);

                // 详情列表 (arg11~arg14)
                var details = [];
                if (item.arg11 && item.arg11 !== '无') details.push(escapeHtml(item.arg11));
                if (item.arg12 && item.arg12 !== '无') details.push(escapeHtml(item.arg12));
                if (item.arg13 && item.arg13 !== '无') details.push(escapeHtml(item.arg13));
                if (item.arg14 && item.arg14 !== '无') details.push(escapeHtml(item.arg14));

                if (details.length > 0) {
                    var $detail = $('<div class="product-detail"></div>');
                    $.each(details, function (i, text) {
                        $detail.append(`<p>${text}</p>`);
                    });
                    $product.append($detail);
                }

                $card.append($product);
            });

            if (!hasValidProduct) {
                $card.append('<div class="info-placeholder">暂无详细产品信息</div>');
            }
        } else {
            // 失败状态
            $card.append('<div class="status-badge fail">验证失败</div>');
            var errMsg = data.message ? escapeHtml(data.message) : '未查询到授权信息，请核对购买渠道。';
            $card.append(`<div class="fail-message">${errMsg}</div>`);
        }
    }

    // 简单的 XSS 防护函数
    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>]/g, function (m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }
});
