(function($) {

  $(document).ready(function(){

    $('button#add-question').click(function(e) {

      e.preventDefault();

      var size = $('table#question-list tr').length - 1;

      $('table#question-list').append('<tr>' +
        '<td><input type="text" name="question-title-'+ size +'" placeholder="Question Title" required/></td>' +
        '<td><input type="text" name="question-choice-1-'+ size +'" placeholder="Choice 1" required/></td>' +
        '<td><input type="text" name="question-choice-3-'+ size +'" placeholder="Choice 3" required/></td>' +
        '<td><input type="text" name="question-choice-2-'+ size +'" placeholder="Choice 2" required/></td>' +
        '<td><input type="text" name="question-choice-4-'+ size +'" placeholder="Choice 4" required/></td>' +
        '<td>' +
        '  <select name="question-answer-'+ size +'">' +
        '    <option value="0">1</option>' +
        '    <option value="1">2</option>' +
        '    <option value="2">3</option>' +
        '    <option value="3">4</option>' +
        '  </select>' +
        '</td>' +
        '<td><a href="#" class="remove">X</a></td>' +
      '</tr>')
    });

    $(document).on("click", ".remove", function(e){

      e.preventDefault();

      var size = $('table#question-list tr').length - 1;
      console.log($(this));
      if (size > 1) {

        $(this).parent().parent().remove();

      } else {

        alert("Cannot delete the first row");
      }
    });
  })
})(jQuery)
