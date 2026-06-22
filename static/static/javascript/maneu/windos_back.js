// 返回上一页面, 功能相当于浏览器后退键
$(document).ready(function () {
    $('#btn-back').click(function () {
            window.history.back();
        }
    )
})