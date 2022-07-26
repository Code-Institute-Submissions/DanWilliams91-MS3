$(document).ready(function () {
    $(".dropdown-trigger").dropdown();
    $('.sidenav').sidenav();
    $('.modal').modal();
    checkScreenSize();
    });

// Functions begin here

    /** Shows the button with an ID of scroll-btn when the window is scrolled down
     * by over 20px from the top of the document 
     */
    // Code adapted from https://www.w3schools.com/howto/howto_js_scroll_to_top.asp
    function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        $("#scroll-btn").css("display", "block")
    } else {
        $("#scroll-btn").css("display", "none")
    }
    }

    /** Scrolls to the top of the page when the user clicks on the button with an
     * ID of scroll-btn
     */
    // Code taken from https://www.w3schools.com/howto/howto_js_scroll_to_top.asp
    function topFunction() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    }


    /** Checks the width of the window and applies or removes the "valign-wrapper"
     *  class based on whether the window width is categorised as small or not. 
     */
    function checkScreenSize() {
        if ($(window).width() <= 600) {
            $(".valign-workaround").removeClass("valign-wrapper");
        } else {
            $(".valign-workaround").addClass("valign-wrapper");
        }
    };

// Functions end here

// Event handlers begin here

    /** Calls the checkScreenSize function when the window is resized */
    $(window).on("resize", function() {
        checkScreenSize();
    });


    /** Calls the scrollFunction function when the window is scrolled */
    $(window).on("scroll", function() {
        scrollFunction();
    });


    /** Calls the topFunction function when the "Go to top" button is clicked */
    $("#scroll-btn").on("click", function() {
        topFunction()
    })

//Event handlers end here