$(document).on('submit', '#updateTicketForm', function(e) {
  e.preventDefault();
  $.post($(this).attr('action'), $(this).serialize(), function() {
    // Actualizar badge de estado dinámicamente
    const newStatus = $('select[name="status"]').val();
    $('#ticketStatus').text(newStatus);
  });
});


$(document).on('submit', '#commentForm', function(e) {
  e.preventDefault();
  $.post($(this).attr('action'), $(this).serialize(), function() {
    const commentText = $('textarea[name="comment"]').val();
    $('#commentsList').append(
      `<li class="list-group-item"><strong>You</strong><small>Just now</small><p class="mb-0">${commentText}</p></li>`
    );
    $('textarea[name="comment"]').val('');
  });
});

$(function() {
  $("form[action*='comments']").on("submit", function(e) {
    e.preventDefault();
    const form = $(this);
    $.post(form.attr("action"), form.serialize(), function() {
      location.reload(); // o actualizar dinámicamente la lista
    });
  });
});