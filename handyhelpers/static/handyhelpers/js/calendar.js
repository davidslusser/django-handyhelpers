document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
      header: {
        center: 'customButton',
        right: 'today, prev,next'
      },
      plugins: ['dayGrid', 'interaction'],
      allDay: false,
      editable: false,
      selectable: false,
      unselectAuto: false,
      displayEventTime: false,
      events: myEvents,

      eventClick: function(info) {
        htmx.ajax('GET', info.event.extendedProps.link, '#modal_wrapper').then(() => {
          var myModal = new bootstrap.Modal(document.getElementById('modal_wrapper'));
          myModal.show();
        });
      }

    });
 
    calendar.render();
    
  });
  