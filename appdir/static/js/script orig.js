// Functions begin here

    /**
     * Initializes the Materialize components and their workarounds.
     * Also calls the checkScreenSize function once the page loads.
     */
    $(document).ready(function () {
        $(".dropdown-trigger").dropdown();
        $(".sidenav").sidenav();
        $(".modal").modal();
        $("select").formSelect();
        $(".tooltipped").tooltip({enterDelay: 300});
        $("select[required]").css({display: "block", height: 0, padding: 0, width: 0, position: "absolute"});
        /* Workaround for Materialize setting readonly="true" on disabled dropdowns */
        $(".select-dropdown.dropdown-trigger").removeAttr("readonly").prop("readonly", true);
        checkScreenSize();
        confirmExit();
        });

    /**
     * Displays a confirmation dialog when the user attempts to leave either the Add Recipe, Edit Recipe,
     * Add Category or Edit Category page.
     */
    function confirmExit() {
        if ($("#ingredients").length > 0 || $("#category_img").length > 0) {
            $(window).on('beforeunload', function () {
                var c = confirm("Navigating from this page will result in all changes being lost. Are you sure you want to leave this page?");
                if (c) {
                    return true;
                } else
                    return false;
            })
        }
    }    


    /** 
     * Shows the button with an ID of scroll-btn when the window is scrolled down
     * by over 20px from the top of the document 
     */
    // Code adapted from https://www.w3schools.com/howto/howto_js_scroll_to_top.asp
    function scrollFunction() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            $("#scroll-btn").css("display", "block");
        } else {
            $("#scroll-btn").css("display", "none");
        }
    }

    /** 
     * Scrolls to the top of the page when the user clicks on the button with an
     * ID of scroll-btn
     */
    // Code taken from https://www.w3schools.com/howto/howto_js_scroll_to_top.asp
    function topFunction() {
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    }


    /** 
     * Checks the width of the window and applies or removes the "valign-wrapper"
     *  class based on whether the window width is categorised as small. 
     */
    function checkScreenSize() {
        if ($(window).width() <= 600) {
            $(".valign-workaround").removeClass("valign-wrapper");
        } else {
            $(".valign-workaround").addClass("valign-wrapper");
        }
    }

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
        topFunction();
    });
    

    /** Redirects the user to the previous webpage when any ".btn-cancel" button is clicked */
    $(".btn-cancel").on("click", function() {
        window.history.back();
    });
    
//Event handlers end here