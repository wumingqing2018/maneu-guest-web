$(document).ready(function () {
    // 初始状态：验证码为空，显示禁用登录按钮，隐藏真实登录按钮
    function toggleLoginButton() {
        if ($("#code").val().trim() === '') {
            $("#login-hold").show();
            $("#login-btn").hide();
        } else {
            $("#login-hold").hide();
            $("#login-btn").show();
        }
    }

    // 页面加载时调用
    toggleLoginButton();

    // 监听验证码输入
    $("#code").on('input', toggleLoginButton);

    // 获取验证码
    $("#sendsms-btn").click(function () {
        const phone = $("#call").val().trim();
        if (!phone) {
            $("#msg").text("请输入手机号码").css("color", "#ff6b6b");
            return;
        }

        $.ajax({
            url: sendsms,
            method: 'POST',
            data: {call: phone},
            success: function (res) {
                if (res.status === true) {
                    // 切换按钮状态
                    $("#wait-btn").show();
                    $("#sendsms-btn").hide();
                    $("#msg").text("").css("color", "");

                    // 60秒后恢复
                    setTimeout(function () {
                        $("#wait-btn").hide();
                        $("#sendsms-btn").show();
                    }, 60000);
                } else {
                    $("#msg").text("发送失败：" + (res.message || "未知错误")).css("color", "#ff6b6b");
                }
            },
            error: function () {
                $("#msg").text("网络错误，请稍后重试").css("color", "#ff6b6b");
            }
        });
    });

    // 登录
    $("#login-btn").click(function () {
        const phone = $("#call").val().trim();
        const code = $("#code").val().trim();

        if (!phone || !code) {
            $("#msg").text("请填写完整信息").css("color", "#ff6b6b");
            return;
        }

        $.ajax({
            url: login_verify,
            method: 'POST',
            data: {call: phone, code: code},
            success: function (res) {
                console.log(res)
                if (res.status === true) {
                    window.location.href = maneu_index_index;
                } else {
                    $("#msg").text(res.message || "登录失败").css("color", "#ff6b6b");
                }
            },
            error: function () {
                $("#msg").text("登录请求失败，请检查网络").css("color", "#ff6b6b");
            }
        });
    });
});
