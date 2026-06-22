function remove(e) {
    e.parentElement.parentElement.remove()
}

$(document).ready(function () {
    // $("#AddMoreTextBox").click(function (e) {
    //     var POLEN = $(".Product_Orders").length + 1;
    //     $("#Product_Orders_TABLE").append(
    //         '<form class="col-9 row vertical2 Product_Orders">\n' +
    //         '    <div class="input-group input-group-sm">\n' +
    //         '        <input autocomplete="off" type="text" name="arg' + POLEN + '0" class="form-control" style="width: 11%" placeholder="类别">\n' +
    //         '        <input autocomplete="off" type="text" name="arg' + POLEN + '1" class="form-control" style="width: 11%" placeholder="品牌">\n' +
    //         '        <input autocomplete="off" type="text" name="arg' + POLEN + '2" class="form-control" style="width: 11%" placeholder="型号">\n' +
    //         '        <input autocomplete="off" type="text" name="arg' + POLEN + '3" class="form-control" style="width: 51%" placeholder="参数">\n' +
    //         '        <input autocomplete="off" type="text" name="arg' + POLEN + '4" class="form-control price" style="width: 11%" placeholder="价格">\n' +
    //         '        <input class="form-control" onclick="remove(this)"  type="button" style="width: 5%" value="删除">\n' +
    //         '    </div>\n' +
    //         '</form>\n'
    //     );
    // });
    //

    $('#insert').click(function () {
        Product_Orders_json = $('.Product_Orders').serializeJsonStr();
        $('#Product_Orders_json').val(Product_Orders_json);
        Vision_Solutions_json = $('#VisionSolutions').serializeJsonStr();
        $('#VisionSolutions_json').val(Vision_Solutions_json);
        order_json = $('#order').serializeJsonStr();
        $('#order_json').val(order_json);
    });


    // $('#VisionSolutionsShowButton').click(function () {
    //     $('#VisionSolutionsShowButton').attr('style', 'display: none')
    //     $('#VisionSolutionsHideButton').attr('style', 'display: block')
    //     $('#VisionHistory').attr('style', 'display: block')
    //     $("#VisionSolutions").attr('style', 'display: block')
    // });
    // $('#VisionSolutionsHideButton').click(function () {
    //     $('#VisionSolutionsHideButton').attr('style', 'display: none');
    //     $('#VisionSolutionsShowButton').attr('style', 'display: block');
    //     $('#VisionHistory').attr('style', 'display: none')
    //     $("#VisionSolutions").attr('style', 'display: none');
    //     $("#VisionSolutions")[0].reset();
    // });
    //
    //
    // $('#VisionHistory').click(function () {
    //     $.ajax({})
    // })
});
