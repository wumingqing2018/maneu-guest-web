        // ==================== 工具函数 ====================
        // XSS 防护：转义 HTML 特殊字符
        function escapeHtml(str) {
            if (!str) return '';
            return String(str).replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
        }

        // 获取 CSRF Token（Django 默认在 Cookie 中）
        function getCSRFToken() {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, 10) === 'csrftoken=') {
                        cookieValue = decodeURIComponent(cookie.substring(10));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // 格式化时间显示（移动端短格式，可选）
        function formatTimeShort(timeStr) {
            if (!timeStr) return '';
            const parts = timeStr.split(' ');
            if (parts.length >= 1) return parts[0];
            return timeStr.substring(0, 10);
        }

        // ---------- API 端点 ----------
        const REPORT = {
            web_detail: "{% url 'maneu_report:detail' %}",
            api_delete: "{% url 'maneu_report:api_delete' %}",
            api_searchText: "{% url 'maneu_report:api_search_data' %}",
            api_searchTime: "{% url 'maneu_report:api_search_time' %}"
        };

        // ---------- DOM 缓存 ----------
        const $listContainer = $('#listContainer');
        const $timeStart = $('#timeStart');
        const $timeEnd = $('#timeEnd');
        const $keyword = $('#keywordInput');
        const $searchByTextBtn = $('#searchByText');
        const $searchByTimeBtn = $('#searchByTime');

        // 请求取消控制器
        let currentRequest = null;

        // ---------- UI 状态函数 ----------
        function showLoading() {
            $listContainer.html(`
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status"></div>
                </div>
            `);
        }

        function showEmptyState() {
            $listContainer.html(`
                <div class="empty-state">
                    <i class="bi bi-inbox"></i>
                    <p>暂无定制记录</p>
                    <small>尝试调整筛选条件或新增一条记录</small>
                </div>
            `);
        }

        function showErrorState() {
            $listContainer.html(`
                <div class="empty-state">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>加载失败，请稍后重试</p>
                </div>
            `);
        }

        // 清除关键词输入框的验证样式
        function clearKeywordInvalid() {
            $keyword.removeClass('is-invalid');
            $keyword.closest('.filter-group').find('.invalid-feedback').hide();
        }

        function showKeywordInvalid() {
            $keyword.addClass('is-invalid');
            $keyword.closest('.filter-group').find('.invalid-feedback').show();
        }

        // ---------- 生成列表项 HTML（XSS 防护）----------
        function createItemHTML(item) {
            const timeRaw = item.time || '';
            const name = escapeHtml(item.name) || '-';
            const phone = escapeHtml(item.phone) || '-';
            const remarkRaw = item.remark || '-';
            const remark = escapeHtml(remarkRaw);
            const escapedRemarkAttr = remarkRaw.replace(/"/g, '&quot;');
            const id = escapeHtml(item.id);

            // 移动端在 col-time 内显示时间（不再使用伪元素）
            return `
                <div class="store-list-item">
                    <div class="col-time">
                        <i class="bi bi-clock me-2 d-md-none"></i>
                        ${escapeHtml(timeRaw) || '-'}
                    </div>
                    <div class="col-name">
                        <i class="bi bi-person me-2 d-md-none"></i>
                        ${name}
                    </div>
                    <div class="col-phone">
                        <i class="bi bi-phone me-2 d-md-none"></i>
                        ${phone}
                    </div>
                    <div class="col-remark" title="${escapedRemarkAttr}">
                        <i class="bi bi-chat-left-text me-2 d-md-none"></i>
                        ${remark}
                    </div>
                    <div class="col-actions">
                        <button class="btn-action detail-btn" data-index-id="${id}" title="查看详情">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn-action delete-btn" data-index-id="${id}" title="删除记录">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </div>
                </div>
            `;
        }

        // 渲染列表（使用 Fragment 提高性能）
        function renderList(items) {
            $listContainer.empty();
            if (!Array.isArray(items) || items.length === 0) {
                showEmptyState();
                return;
            }
            const fragment = $(document.createDocumentFragment());
            items.forEach(item => {
                fragment.append(createItemHTML(item));
            });
            $listContainer.append(fragment);
        }

        // ---------- 业务操作：详情跳转 ----------
        function handleDetail(btn) {
            const indexId = btn.getAttribute('data-index-id');
            window.location.href = REPORT.web_detail + '?index_id=' + indexId;
        }

        // 删除记录（改用 DELETE 方法 + CSRF token）
        function deleteRecord(btn) {
            if (!confirm("确定要删除这条记录吗？此操作不可恢复。")) return;

            const indexId = btn.getAttribute('data-index-id');
            $.ajax({
                url: REPORT.api_delete,
                method: 'GET',
                data: { index_id: indexId },
                success(res) {
                    if (res.status === true) {
                        const $item = $(btn).closest('.store-list-item');
                        if ($item.length) {
                            $item.css({
                                transition: 'all 0.3s ease',
                                opacity: 0,
                                transform: 'translateX(20px)'
                            });
                            setTimeout(() => {
                                $item.remove();
                                if (!$listContainer.find('.store-list-item').length) {
                                    showEmptyState();
                                }
                            }, 300);
                        }
                    } else {
                        alert(res.message || '删除失败，请稍后重试');
                    }
                },
                error(xhr) {
                    if (xhr.status === 403) {
                        alert('CSRF 验证失败，请刷新页面后重试');
                    } else {
                        alert('网络错误，请稍后重试');
                    }
                }
            });
        }

        // ---------- 数据加载（支持 abort 前一个请求）----------
        function fetchAndRender(url, params) {
            if (currentRequest && currentRequest.readyState !== 4) {
                currentRequest.abort();
            }
            showLoading();
            currentRequest = $.get(url, params)
                .done(res => {
                    const data = Array.isArray(res) ? res : (res.content || []);
                    renderList(data);
                })
                .fail(xhr => {
                    if (xhr.statusText === 'abort') return;
                    showErrorState();
                });
        }

        // 时间范围搜索
        function searchByTime() {
            clearKeywordInvalid();
            fetchAndRender(REPORT.api_searchTime, {
                timeS: $timeStart.val(),
                timeE: $timeEnd.val()
            });
        }

        // 关键词搜索
        function searchByText() {
            const keyword = $keyword.val().trim();
            if (!keyword) {
                showKeywordInvalid();
                return;
            }
            clearKeywordInvalid();
            fetchAndRender(REPORT.api_searchText, { value: keyword });
        }

        // ---------- 初始化事件绑定 ----------
        $(function () {
            // 如果后端未传递 default_time_start，前端设置默认起始时间为30天前
            if (!$timeStart.val()) {
                const thirtyDaysAgo = new Date();
                thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
                $timeStart.val(thirtyDaysAgo.toISOString().slice(0, 16));
            }
            // 默认加载时间范围内的数据
            searchByTime();

            // 按钮事件
            $searchByTimeBtn.on('click', searchByTime);
            $searchByTextBtn.on('click', searchByText);

            // 回车搜索
            $keyword.on('keypress', function (e) {
                if (e.which === 13) {
                    e.preventDefault();
                    searchByText();
                }
            });

            // 事件委托：查看详情
            $listContainer.on('click', '.detail-btn', function () {
                handleDetail(this);
            });

            // 事件委托：删除记录
            $listContainer.on('click', '.delete-btn', function () {
                deleteRecord(this);
            });
        });