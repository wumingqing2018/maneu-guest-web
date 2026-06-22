$(document).ready(function () {
    // 客户信息折叠
    $('#toggleGuest').click(function () {
        $('#guestExtra').slideToggle(200);
        $(this).find('i').toggleClass('bi-chevron-down bi-chevron-up');
    });

    // 产品信息折叠
    $('#toggleProduct').click(function () {
        $('#productExtra').slideToggle(200);
        $(this).find('i').toggleClass('bi-chevron-down bi-chevron-up');
    });

    // 提交逻辑（增加参数名唯一性校验）
    $('#insert').click(function () {
        // 收集所有非空的参数名
        const enteredKeys = [];
        for (let i = 1; i <= 12; i++) {
            const keyVal = $(`#key${i}`).val().trim();
            if (keyVal !== '') enteredKeys.push(keyVal);
        }

        // 检查是否有重复参数名
        if (new Set(enteredKeys).size !== enteredKeys.length) {
            alert('产品参数名不能重复，请检查并修改重复的参数名。');
            return;
        }

        // 构建键值对对象
        const customObj = {};
        for (let i = 1; i <= 12; i++) {
            const k = $(`#key${i}`).val().trim();
            const v = $(`#val${i}`).val().trim();
            if (k !== '') {
                customObj[k] = v;
            }
        }
        const data = [customObj];

        $.ajax({
            url: store_insert_api,
            method: 'GET',
            data: {
                time: $('#time').val(),
                name: $('#name').val(),
                phone: $('#phone').val(),
                age: $('#age').val(),
                sex: $('#sex').val(),
                dfh: $('#dfh').val(),
                ot: $('#ot').val(),
                em: $('#em').val(),
                remark: $('#remark').val(),
                storeContent: JSON.stringify(data)
            },
            success: function (res) {
                if (res.status === true) {
                    alert('记录提交成功');
                } else {
                    alert('提交失败：' + (res.message || '未知错误'));
                }
            },
            error: function () {
                alert('网络错误，请稍后重试');
            }
        });
    });
});
