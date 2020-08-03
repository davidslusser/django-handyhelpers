$( document ).ready(function() {
    $("div.zoom-card").hover(function () {
        $(this).toggleClass('scale-up').siblings().toggleClass('scale-down')
    });

    $("a.zoom-card").hover(function () {
        $(this).toggleClass('scale-up').siblings().toggleClass('scale-down')
    });
});
