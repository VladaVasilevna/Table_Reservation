document.addEventListener('DOMContentLoaded', function () {
	const container = document.querySelector('.container[data-auth]');
	const isAuthenticated = container?.dataset.auth === 'true';
	const tableButtons = document.querySelectorAll('.table-button');
	const dateInput = document.querySelector('#booking-choose-form [name="date"]');
	const timeInput = document.querySelector('#booking-choose-form [name="time"]');

	// Настройки системы (будут загружены с сервера)
	let systemSettings = {
		booking_duration_hours: 2,
		restaurant_open_time: '11:00',
		restaurant_close_time: '23:00',
		last_booking_time: '22:00'
	};

	// Загружаем настройки с сервера
	async function loadSettings() {
		try {
			const response = await fetch('/api/settings/');
			const data = await response.json();
			systemSettings = data;
		} catch (error) {
			console.log('Не удалось загрузить настройки, используем значения по умолчанию');
		}
	}

	// Инициализация настроек
	loadSettings();

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
						button.classList.add('reserved');
						button.title = `Стол забронирован`;
					} else {
						button.disabled = false;
						button.classList.remove('reserved');
						button.title = `Вместимость ${tableData.capacity} персон`;
					}
				});
			});
	}

	// Обновляем статус столов при загрузке страницы, если дата и время уже выбраны
	if (dateInput.value && timeInput.value) {
		fetchTablesStatus();
	}

	// Обработка клика по кнопке стола
	tableButtons.forEach(button => {
		button.addEventListener('click', () => {
			const tableId = button.textContent.trim();

			// Проверка авторизации
			if (!isAuthenticated) {
				document.getElementById('auth-modal').style.display = 'flex';
				return;
			}

			// Проверка выбора даты и времени
			const date = dateInput.value;
			const time = timeInput.value;

			if (!date || !time) {
				alert('Пожалуйста, выберите дату и время бронирования.');
				return;
			}

			// Проверка, что выбранная дата не в прошлом
			const now = new Date();
			const selectedDateTime = new Date(`${date}T${time}`);
			if (selectedDateTime < now) {
				alert('Выбранная дата и время уже прошли. Пожалуйста, выберите другую дату и время.');
				return;
			}

			// Проверка времени работы ресторана из настроек
			const [hours, minutes] = time.split(':').map(Number);
			const selectedMinutes = hours * 60 + minutes;

			const [openHours, openMinutes] = systemSettings.restaurant_open_time.split(':').map(Number);
			const openMinutesTotal = openHours * 60 + openMinutes;

			const [closeHours, closeMinutes] = systemSettings.restaurant_close_time.split(':').map(Number);
			const closeMinutesTotal = closeHours * 60 + closeMinutes;

			const [lastBookingHours, lastBookingMinutes] = systemSettings.last_booking_time.split(':').map(Number);
			const lastBookingMinutesTotal = lastBookingHours * 60 + lastBookingMinutes;

			if (selectedMinutes < openMinutesTotal) {
				alert(`Ресторан открывается в ${systemSettings.restaurant_open_time}. Пожалуйста, выберите другое время.`);
				return;
			} else if (selectedMinutes >= closeMinutesTotal) {
				alert(`Ресторан работает с ${systemSettings.restaurant_open_time} до ${systemSettings.restaurant_close_time}. Пожалуйста, выберите другое время.`);
				return;
			} else if (selectedMinutes > lastBookingMinutesTotal) {
				alert(`Кухня не принимает заказы после ${systemSettings.last_booking_time}. Пожалуйста, выберите другое время.`);
				return;
			}

			// Проверка, что бронь не выходит за пределы работы ресторана
			const endTimeMinutes = selectedMinutes + (systemSettings.booking_duration_hours * 60);
			if (endTimeMinutes > closeMinutesTotal) {
				// Если бронь заканчивается после закрытия, то она заканчивается в момент закрытия
				// Это нормально для поздних броней
				console.log('Бронь заканчивается в момент закрытия ресторана');
			}

			// Открываем модальное окно бронирования
			document.getElementById('booking-modal').style.display = 'flex';
			document.getElementById('modal-table-id').value = tableId;
			const modalTitle = document.getElementById('modal-table-num');
			modalTitle.textContent = `Бронирование столика №${tableId}`;
			modalTitle.style.textAlign = 'center';

			// Автоматически заполняем поля даты и времени в модальном окне
			const modalForm = document.querySelector('#booking-modal form');
			const modalDateInput = modalForm.querySelector('input[name="date"]');
			const modalTimeInput = modalForm.querySelector('input[name="time"]');

			if (modalDateInput && modalTimeInput) {
				modalDateInput.value = date;
				modalTimeInput.value = time;

				// Блокируем поля даты и времени
				modalDateInput.disabled = true;
				modalTimeInput.disabled = true;
			}
		});
	});

	// Обработчик отправки формы бронирования
	const bookingForm = document.querySelector('#booking-modal form');
	if (bookingForm) {
		bookingForm.addEventListener('submit', function (e) {
			e.preventDefault();

			const formData = new FormData(this);

			// Включаем заблокированные поля в FormData
			const modalDateInput = this.querySelector('input[name="date"]');
			const modalTimeInput = this.querySelector('input[name="time"]');

			if (modalDateInput && modalTimeInput) {
				formData.set('date', modalDateInput.value);
				formData.set('time', modalTimeInput.value);
			}

			fetch(this.action, {
				method: 'POST',
				body: formData,
				headers: {
					'X-Requested-With': 'XMLHttpRequest',
				}
			})
				.then(response => response.json())
				.then(data => {
					if (data.success) {
						// Закрываем модальное окно
						document.getElementById('booking-modal').style.display = 'none';

						// Обновляем статус столов
						fetchTablesStatus();

						// Показываем сообщение об успехе
						alert(data.message);

						// Перенаправляем на главную страницу
						window.location.href = data.redirect_url;
					} else {
						// Показываем ошибки валидации
						let errorMessage = 'Ошибка при создании бронирования:\n';
						for (const field in data.errors) {
							errorMessage += `${field}: ${data.errors[field].join(', ')}\n`;
						}
						alert(errorMessage);
					}
				})
				.catch(error => {
					console.error('Ошибка при отправке формы:', error);
					alert('Произошла ошибка при создании бронирования. Попробуйте еще раз.');
				});
		});
	}

	// Обновляем доступность столов при изменении даты или времени
	[dateInput, timeInput].forEach(input => {
		input.addEventListener('change', fetchTablesStatus);
	});

	// Закрытие модалок по крестику
	document.querySelectorAll('.modal .close').forEach(btn => {
		btn.addEventListener('click', () => {
			btn.closest('.modal').style.display = 'none';

			// Разблокируем поля даты и времени при закрытии модального окна бронирования
			if (btn.closest('#booking-modal')) {
				const modalDateInput = document.querySelector('#booking-modal input[name="date"]');
				const modalTimeInput = document.querySelector('#booking-modal input[name="time"]');

				if (modalDateInput && modalTimeInput) {
					modalDateInput.disabled = false;
					modalTimeInput.disabled = false;
				}
			}
		});
	});

	// Закрытие модалок по клику вне
	window.addEventListener('click', (event) => {
		document.querySelectorAll('.modal').forEach(modal => {
			if (event.target === modal) {
				modal.style.display = 'none';

				// Разблокируем поля даты и времени при закрытии модального окна бронирования
				if (modal.id === 'booking-modal') {
					const modalDateInput = modal.querySelector('input[name="date"]');
					const modalTimeInput = modal.querySelector('input[name="time"]');

					if (modalDateInput && modalTimeInput) {
						modalDateInput.disabled = false;
						modalTimeInput.disabled = false;
					}
				}
			}
		});
	});

	// Подготовка карты столов для бронирования
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
					}
				});
			});
	}

	// Вызываем при изменении даты и времени
	[dateInput, timeInput].forEach(input => {
		input.addEventListener('change', updateTableIdMap);
	});
});
