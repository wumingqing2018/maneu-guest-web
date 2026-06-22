// ===== 1. 全局 Ajax 设置（自动添加 Authorization 头，跳过刷新接口） =====
$(document).ready(function() {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            // 自动添加 JWT Access Token
            const token = localStorage.getItem('access_token');
            if (token) {
                xhr.setRequestHeader('Authorization', 'Bearer ' + token);
            }
        }
    });
});

// ===== 2. 刷新 Token（返回 jQuery Deferred） =====
function refreshAccessToken() {
    var dfd = $.Deferred();
    var refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        dfd.reject('No refresh token');
        return dfd.promise();
    }
    $.ajax({
        url: '/refresh_token/',
        method: 'POST',
        data: { refresh_token: refreshToken }
    }).done(function(res) {
        if (res.status === true && res.access_token) {
            dfd.resolve(res);
        } else {
            dfd.reject('Invalid refresh response');
        }
    }).fail(function(xhr) {
        dfd.reject(xhr);
    });
    return dfd.promise();
}

// ===== 3. 401 拦截与自动刷新 =====
var isRefreshing = false;
var failedRequestsQueue = [];

$(document).ajaxError(function(event, xhr, settings) {
    if (xhr.status !== 401) return;

    // 刷新接口自身 401 直接跳转
    if (settings.url.indexOf('/refresh_token/') !== -1) {
        localStorage.clear();
        window.location.href = '/login/';
        return;
    }

    // 将失败请求的配置加入队列（稍后重放）
    failedRequestsQueue.push(function(newToken) {
        // 重新发起原始请求，全局 beforeSend 会使用 localStorage 中的新 token
        return $.ajax(settings);
    });

    // 如果尚未刷新，则开始刷新流程
    if (!isRefreshing) {
        isRefreshing = true;
        refreshAccessToken()
            .done(function(res) {
                // 更新 Token
                localStorage.setItem('access_token', res.access_token);
                if (res.refresh_token) {
                    localStorage.setItem('refresh_token', res.refresh_token);
                }
                // 重放所有积压的请求
                while (failedRequestsQueue.length) {
                    var retry = failedRequestsQueue.shift();
                    retry(res.access_token);
                }
            })
            .fail(function() {
                localStorage.clear();
                window.location.href = '/login/';
            })
            .always(function() {
                isRefreshing = false;
                failedRequestsQueue = []; // 清空队列（防止内存泄漏）
            });
    }
});

// ===== 5. 登出 =====
$(".logoutBtn").click(function() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/';
});