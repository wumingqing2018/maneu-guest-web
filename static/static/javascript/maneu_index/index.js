$(function () {
    var start = moment().subtract(29, 'days');
    var end = moment();
    var myChart = echarts.init(document.getElementById('main1'), 'maneu');

    function cb(start, end) {
        $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        $('#body').empty();
        $.ajax({
                url: api_index,
                type: 'GET',
                data: {
                    start_day: start.format('YYYY-MM-DD'),
                    end_day: end.format('YYYY-MM-DD'),
                    start: start.format('YYYY-MM-DD 00:00:00'),
                    end: end.format('YYYY-MM-DD 23:59:59'),
                },
                success: function (res) {
                    console.log(res)
                    // 使用刚指定的配置项和数据显示图表。
                    var option = {
                        title: {
                            show: true, //显示策略，默认值true,可选为：true（显示） | false（隐藏）
                            // text: '零售数据：'+ res.count +'单\n\n新增客户：'+ res.count1 +'位' , //主标题文本，'\n'指定换行
                            link: '', //主标题文本超链接,默认值true
                            target: null, //指定窗口打开主标题超链接，支持'self' | 'blank'，不指定等同为'blank'（新窗口）
                            x: 'left', //水平安放位置，默认为'left'，可选为：'center' | 'left' | 'right' | {number}（x坐标，单位px）
                            y: 'top', //垂直安放位置，默认为top，可选为：'top' | 'bottom' | 'center' | {number}（y坐标，单位px）
                            textAlign: null,//水平对齐方式，默认根据x设置自动调整，可选为： left' | 'right' | 'center
                            backgroundColor: 'rgba(0,0,0,0)', //标题背景颜色，默认'rgba(0,0,0,0)'透明
                            borderColor: '#ccc', //标题边框颜色,默认'#ccc'
                            borderWidth: 0, //标题边框线宽，单位px，默认为0（无边框）
                            padding: 0, //标题内边距，单位px，默认各方向内边距为5，接受数组分别设定上右下左边距
                            itemGap: 10, //主副标题纵向间隔，单位px，默认为10
                            textStyle: { //主标题文本样式{"fontSize": 18,"fontWeight": "bolder","color": "#333"}
                                fontSize: 20,
                                fontStyle: 'normal',
                                fontWeight: 'normal',
                            },
                        },
                        tooltip: {},
                        legend: {
                            data: ['零售数据', '客户数据']
                        },
                        xAxis: {
                            data: res.time_list
                        },
                        yAxis: {},
                        series: [{
                            name: '零售数据',
                            type: 'line',
                            data: res.time_newList,
                        }, {
                            name: '客户数据',
                            type: 'line',
                            data: res.time_newList1,
                        }]
                    };
                    myChart.setOption(option);
                }
            }
        );
    }

    $('#reportrange').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
            // 'Today': [moment(), moment()],
            // 'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            '今天': [moment(), moment()],
            '昨天': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            '七天内': [moment().subtract(6, 'days'), moment()],
            '三十天内': [moment().subtract(29, 'days'), moment()],
            '本月': [moment().startOf('month'), moment().endOf('month')],
            '上月': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }, cb);
    cb(start, end);
});

function deleteBtn(obj) {
    if (confirm("您确定要删除吗？")) {
        $.ajax({
            url: api_delete,
            type: 'GET',
            data: {
                index_id: obj.dataset.index_id,
            },
            success: function (res) {
                console.log(res)
                if (res.status === true) {
                    obj.parentElement.parentElement.parentElement.parentElement.parentElement.remove()
                } else {
                    alert(res.message)
                }
            },
        })

    } else {
        return false;
    }
}


$(document).ready(function () {
    $.ajax({
        url: search_time,
        method: 'GET',
        data: {
            timeE: $("#timeE").val(),
            timeS: $("#timeS").val(),
        },
        success: function (res) {
            console.log(res)
            forList(res.content)
        }
    })

    $('#search_time').click(function () {
        $.ajax({
            url: search_time,
            method: 'GET',
            data: {
                timeE: $("#timeE").val(),
                timeS: $("#timeS").val(),
            },
            success: function (res) {
                console.log(res)
                forList(res.content)
            }
        })
    })

    $('#search_data').click(function () {
        $.ajax({
            url: search_data,
            method: 'GET',
            data: {
                value: $("#value").val(),
            },
            success: function (res) {
                console.log(res)
                forList(res.content)
            }
        })
    })

    function forList(res) {
        $('#body').empty();
        for (i in res) {
            $('#body').append(
                "<div>\n" +
                "    <div class='col-12 row'>\n" +
                "        <div class='col-2'>\n" +
                "            <p>" + res[i]['time'] + "</p>\n" +
                "        </div>\n" +
                "        <div class='col-1'>\n" +
                "            <p>" + res[i]['name'] + "</p>\n" +
                "        </div>\n" +
                "        <div class='col-1'>\n" +
                "            <p>" + res[i]['phone'] + "</p>\n" +
                "        </div>\n" +
                "        <div class='col-7'>\n" +
                "            <p>" + res[i]['remark'] + "</p>\n" +
                "        </div>\n" +
                "        <div class='col-1'>\n" +
                "            <form method='GET' action='" + api_detail + "'>\n" +
                "                <input type='hidden' name='index_id' value=" + res[i]['id'] + ">\n" +
                "                <div class='input-group input-group-sm'>\n" +
                "                    <input type='submit' class='col-12 btn btn-primary' value='查看'>\n" +
                "                </div>\n" +
                "            </form>\n" +
                "        </div>\n" +
                "    </div>\n" +
                "    <hr style='color: white'>\n" +
                "</div>\n"
            )
        }
    }
})