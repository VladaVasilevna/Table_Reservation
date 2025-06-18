document.addEventListener('DOMContentLoaded', () => {
  const auth = document.body.dataset.auth === 'true';
  const dateIn = document.getElementById('id_date');
  const timeIn = document.getElementById('id_time');
  const guestIn = document.getElementById('id_guests');
  const hall = document.getElementById('hall-map');
  const authModal = document.getElementById('auth-modal');
  const bookModal = document.getElementById('booking-modal');

  function loadTables() {
    const d = dateIn.value, t = timeIn.value, g = guestIn.value;
    if (!d || !t) return;
    fetch(`/api/tables/?date=${d}&time=${t}&guests=${g}`)
      .then(r => r.json()).then(data => {
        hall.innerHTML = <img src="/static/reserv/images/hall.png">;
        data.tables.forEach(tb => {
          const btn = document.createElement('button');
          btn.className = table-btn ${tb.shape};
          btn.style.cssText = position:absolute;left:${tb.x}px;top:${tb.y}px;width:${tb.width}px;height:${tb.height}px;
          btn.innerText = tb.number;
          btn.title = Вместимость до ${tb.capacity} персон;
          btn.disabled = tb.reserved;
          btn.onclick = () => {
            if (!d || !t) return alert('Укажите дату и время');
            if (!auth) return authModal.style.display = 'block';
            document.getElementById('modal-table-id').value = tb.id;
            document.getElementById('modal-table-num').innerText = Столик №${tb.number};
            document.getElementById('id_date').value = d;
            document.getElementById('id_time').value = t;
            bookModal.style.display = 'block';
          };
          hall.appendChild(btn);
        });
      });
  }

  [dateIn, timeIn, guestIn].forEach(el => el.addEventListener('change', loadTables));
  document.querySelectorAll('.modal .close').forEach(x => x.onclick = () => x.closest('.modal').style.display = 'none');
});
