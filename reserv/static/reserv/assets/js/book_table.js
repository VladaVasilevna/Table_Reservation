const container = document.querySelector('.container[data-auth]');
const isAuthenticated = container?.dataset.auth === 'true';
const tableButtons = document.querySelectorAll('.table-button');

const dateInput = document.querySelector('#booking-choose-form [name="date"]');
const timeInput = document.querySelector('#booking-choose-form [name="time"]');

// Обновление доступности столов при изменении даты/времени
function fetchTablesStatus() {
  const date = dateInput.value;
  const time = timeInput.value;

  if (!date || !time) return;

  fetch(`/api/tables/?date=${date}&time=${time}`)
    .then(response => response.json())
    .then(data => {
      const tables = data.tables;

      tableButtons.forEach(button => {
        const tableId = parseInt(button.textContent.trim());
        const tableData = tables.find(t => t.number === tableId);

        if (tableData?.reserved) {
          button.disabled = true;
          button.style.opacity = '0.5';
          button.style.cursor = 'not-allowed';
          button.title = `Стол забронирован`;
        } else {
          button.disabled = false;
          button.style.opacity = '';
          button.style.cursor = '';
          button.title = `Вместимость ${tableData.capacity} персон`;
        }
      });
    });
}

// Обработка клика по кнопке стола
tableButtons.forEach(button => {
  button.addEventListener('click', () => {
    const tableId = button.textContent.trim();

    // Проверка авторизации (всегда первая)
    if (!isAuthenticated) {
      document.getElementById('auth-modal').style.display = 'block';
      return;
    }

    // Далее — только для авторизованных
    const date = dateInput.value;
    const time = timeInput.value;

    if (!date || !time) {
      alert('Пожалуйста, выберите дату и время бронирования.');
      return;
    }

    const now = new Date();
    const selectedDateTime = new Date(`${date}T${time}`);
    if (selectedDateTime < now) {
      alert('Выбранная дата и время уже прошли. Пожалуйста, выберите другую дату и время.');
      return;
    }

    const [hours, minutes] = time.split(':').map(Number);
    const selectedMinutes = hours * 60 + minutes;
    const openMinutes = 11 * 60;   // 11:00
    const closeMinutes = 22 * 60;  // 22:00

    if (selectedMinutes < openMinutes) {
      alert('Ресторан открывается в 11:00. Пожалуйста, выберите другое время.');
      return;
    } else if (selectedMinutes > closeMinutes) {
      alert('Кухня принимает заказы до 22:00. Пожалуйста, выберите другое время.');
      return;
    }

    // Всё в порядке — открываем модалку бронирования
    document.getElementById('booking-modal').style.display = 'flex';
    document.getElementById('modal-table-id').value = tableId;
    const modalTitle = document.getElementById('modal-table-num');
    modalTitle.textContent = `Бронирование столика №${tableId}`;
    modalTitle.style.textAlign = 'center';
  });
});

// Обновляем доступность столов при изменении даты или времени
[dateInput, timeInput].forEach(input => {
  input.addEventListener('change', fetchTablesStatus);
});

// Закрытие модалок по крестику
document.querySelectorAll('.modal .close').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.closest('.modal').style.display = 'none';
  });
});

// Закрытие модалок по клику вне
window.addEventListener('click', (event) => {
  document.querySelectorAll('.modal').forEach(modal => {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  });
});

// Подготовка карты столов для бронирования (если понадобится)
let numberToIdMap = {};

function updateTableIdMap() {
  const date = dateInput.value;
  const time = timeInput.value;

  if (!date || !time) return;

  fetch(`/api/tables/?date=${date}&time=${time}`)
    .then(response => response.json())
    .then(data => {
      const tables = data.tables;
      numberToIdMap = {};

      tableButtons.forEach(button => {
        const tableNumber = parseInt(button.textContent.trim());
        const tableData = tables.find(t => t.number === tableNumber);

        if (tableData) {
          numberToIdMap[tableNumber] = tableData.id;
          // Можно использовать map при отправке брони
        }
      });
    });
}

// Вызываем при изменении даты и времени
[dateInput, timeInput].forEach(input => {
  input.addEventListener('change', updateTableIdMap);
});
