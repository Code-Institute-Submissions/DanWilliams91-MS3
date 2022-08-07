$(document).ready(function () {
    $(".dropdown-trigger").dropdown();
    $('.sidenav').sidenav();
    $('.modal').modal();
    $('select').formSelect();
    $('.tooltipped').tooltip({enterDelay: 300});
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
    };

    /** Scrolls to the top of the page when the user clicks on the button with an
     * ID of scroll-btn
     */
    // Code taken from https://www.w3schools.com/howto/howto_js_scroll_to_top.asp
    function topFunction() {
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    };


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


    function addIngredientRow() {
        let existingRows = $("[id^='ingredient-row']");
        $("#ingredients-table").append(
            `<tr>
            <td>
                <input id="ingredient-row-${existingRows.length}" name="ingredient-row-${existingRows.length}" minlength="3" maxlength="25"
                    type="text" class="validate" required>
                <label for="ingredient-row-${existingRows.length}" class="white-text">Enter ingredient here</label>
            </td>
            <td>
                <input id="quantity-row-${existingRows.length}" name="quantity-row-${existingRows.length}" minlength="1" maxlength="25"
                    type="text" class="validate" required>
                <label for="quantity-row-${existingRows.length}" class="white-text">Enter quantity here</label>
            </td>
            </tr>`
        )
    };


    function removeIngredientRows() {
        let ingredientRows = ($("[id^='ingredient-row']"));
        let quantityRows = ($("[id^='quantity-row']"));
        for (let i = 0; i < ingredientRows.length; i++) {
            if (!ingredientRows[i].classList.contains("valid") && !quantityRows[i].classList.contains("valid")) {
                ingredientRows[i].closest("tr").remove();
            }
        }
    }


    function updateIngredients() {
        let info = $("#ingredients-table input");
        console.log(info)



        
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
        topFunction()
    })


    $(".btn-cancel").on("click", function() {
        window.history.back()
    })


    /** */
    // $("#add-ingredient-row").on("click", function() {
    //     addIngredientRow()
    // })


    // /** */
    // $("#remove-ingredient-row").on("click", function() {
    //     removeIngredientRows()
    // })


    // /** */
    // $("#ingredients-submit").on("click", function() {
    //     updateIngredients()
    // })


    // /** */
    // $("#add-ingredients").on("click", function() {
    //     do {
    //         $("#page-content").css("display", " none")
    //         $("#recipe_name").attr("class", "hidden")
    //         $("#category_name").attr("class", "hidden")
    //         if (!$("#ingredients-modal").css("display", "block")) {
    //             break;
    //         }
    //     } while ($("#ingredients-modal").css("display", "block"))
    //     $("#recipe_name").attr("class", "validate")
    //     $("#category_name").attr("class", "validate")
    //     $("#page-content").css("display", " block")
    // })
    
//Event handlers end here