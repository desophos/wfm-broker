'use strict';

// https://remarkablemark.org/blog/2019/11/29/javascript-sanitize-html/
function sanitizeHTML(text) {
    return $('<div>').text(text).html();
}

function remove(el) {
    $(el).parents('div.order').fadeOut();
}

function clip(el) {
    navigator.clipboard.writeText(
        $(el).parents('div.copy').siblings('div.text').find('span.whisper').text()
    ).then(function () {
        $(el).text("Copied to clipboard");
    });
}

//function sanitizeFields(data) {}

function orderHTML(data) {
    // TODO: sanitize data
    return $.parseHTML(
        `<div class="order" id=${data.id}>` +
        '<div class="done">' +
        '<button type="button" name="done" class="done" onclick="remove(this);">Done</button>' +
        '</div>' +
        '<div class="text">' +
        '<p>' +
        `<span class="whisper">/w ${data.user.ingame_name} Hi! I want to buy: ${data.item.en.item_name} for ${data.platinum} platinum. (warframe.market)</span>` +
        '<br>' +
        `(${data.quantity} for sale by ${data.user.ingame_name} at ${data.ratio.toFixed(1)} ducats/plat)` +
        '</p>' +
        '</div>' +
        '<div class="copy">' +
        '<button type="button" name="copy" class="copy" onclick="clip(this);">Whisper</button>' +
        '</div>' +
        '</div>'
    );
}

//$('button.done').click(function () {
    //var order = $(this).parents("div.order");
    //$.ajax({
    //    method: "POST",
    //    url: url_for("remove"),
    //    data: order.attr("id"),
    //}).done(order.fadeout);
//});