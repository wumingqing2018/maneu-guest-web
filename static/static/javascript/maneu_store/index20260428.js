// 删除确认及请求
function deleteRecord(btn) {
    if (!confirm("确定要删除这条记录吗？此操作不可恢复。")) return;

    const indexId = btn.dataset.index_id;
    $.ajax({
        url: api_delete,
        type: 'GET',
        data: {index_id: indexId},
        success: function (res) {
            if (res.status === true) {
                const item = btn.closest('.store-list-item');
                if (item) {
                    item.style.transition = 'all 0.3s ease';
                    item.style.opacity = '0';
                    item.style.transform = 'translateX(20px)';
                    setTimeout(() => item.remove(), 300);
                }
                // 如果列表空了，显示空状态
                if ($('#body .store-list-item').length === 0) {
                    showEmptyState();
                }
            } else {
                alert(res.message || '删除失败，请稍后重试');
            }
        },
        error: function () {
            alert('网络错误，请稍后重试');
        }
    });
}

// 构建列表HTML
function renderList(dataArray) {
    const container = $('#body');
    container.empty();

    if (!dataArray || dataArray.length === 0) {
        showEmptyState();
        return;
    }

    dataArray.forEach(item => {
        const remarkText = item.remark || '-';
        const rowHtml = `
                <div class="store-list-item" data-mobile-label="${item.time || ''}">
                    <div class="col-time"><i class="bi bi-clock me-2 d-md-none"></i>${item.time || '-'}</div>
                    <div class="col-name"><i class="bi bi-person me-2 d-md-none"></i>${item.name || '-'}</div>
                    <div class="col-phone"><i class="bi bi-phone me-2 d-md-none"></i>${item.phone || '-'}</div>
                    <div class="col-remark" title="${remarkText.replace(/"/g, '&quot;')}">
                        <i class="bi bi-chat-left-text me-2 d-md-none"></i>${remarkText}
                    </div>
                    <div class="col-actions">
                        <a href="${api_detail}?index_id=${item.id}" class="btn-action" title="查看详情">
                            <i class="bi bi-eye"></i>
                        </a>
                        <button class="btn-action delete-btn" data-index_id="${item.id}" onclick="deleteRecord(this)" title="删除记录">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </div>
                </div>
            `;
        container.append(rowHtml);
    });
}

function showEmptyState() {
    $('#body').html(`
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <p>暂无定制记录</p>
                <small>尝试调整筛选条件或新增一条记录</small>
            </div>
        `);
}

// 通用加载函数
function fetchAndRender(url, params) {
    const body = $('#body');
    body.html(`<div class="loading-spinner"><div class="spinner-border text-primary" role="status"></div></div>`);

    $.ajax({
        url: url,
        method: 'GET',
        data: params,
        success: function (res) {
            renderList(res.content || []);
        },
        error: function () {
            body.html(`<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>加载失败，请稍后重试</p></div>`);
        }
    });
}

$(document).ready(function () {
    // 初始加载：使用默认时间范围
    const timeS = $("#timeS").val();
    const timeE = $("#timeE").val();
    fetchAndRender(search_time_url, {timeS: timeS, timeE: timeE});

    // 时间筛选按钮
    $('#search_time').click(function () {
        fetchAndRender(search_time_url, {
            timeS: $("#timeS").val(),
            timeE: $("#timeE").val()
        });
    });

    // 关键词搜索按钮
    $('#search_data').click(function () {
        const keyword = $("#value").val().trim();
        if (!keyword) {
            alert('请输入搜索关键词');
            return;
        }
        fetchAndRender(search_data_url, {value: keyword});
    });

    // 回车搜索
    $('#value').keypress(function (e) {
        if (e.which === 13) {
            $('#search_data').click();
        }
    });
});