$(document).ready(function() {

    /* ===== Stickyfill ===== */
    /* Ref: https://github.com/wilddeer/stickyfill */
    // Add browser support to position: sticky
    var elements = $('.sticky');
    Stickyfill.add(elements);


    /* Activate scrollspy menu */
    $('body').scrollspy({target: '#doc-menu', offset: 100});

    /* Smooth scrolling */
	$('a.scrollto').on('click', function(e){
        //store hash
        var target = this.hash;
        e.preventDefault();
		$('body').scrollTo(target, 800, {offset: 0, 'axis':'y'});

	});

    /* Bootstrap lightbox */
    /* Ref: http://ashleydw.github.io/lightbox/ */

    $(document).delegate('*[data-toggle="lightbox"]', 'click', function(e) {
        e.preventDefault();
        $(this).ekkoLightbox();
    });


});

function search_page() {
    let input = document.getElementById('search_text').value
    input=input.toLowerCase();
    let x = document.getElementsByClassName('body-blue');

    for (i = 0; i < x.length; i++) {
        if (!x[i].innerHTML.toLowerCase().includes(input)) {
            x[i].style.display="none";
        }
        else {
            x[i].style.display="list-item";
        }
    }
}
