// static/js/script.js

// Показать форму регистрации
function showRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

// Вернуться к форме входа
function showLogin() {
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
}

// Закрыть модальное окно
function closeModal() {
    document.getElementById('loginModal').style.display = 'none';
}

// Открыть модальное окно
function openModal() {
    document.getElementById('loginModal').style.display = 'block';
}
document.addEventListener("DOMContentLoaded", () => {
    const calendar = document.getElementById("calendar");
    const events = window.events || []; // Список событий из шаблона Flask

    // Функция для отрисовки календаря
    function renderCalendar() {
        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth();

        const firstDay = new Date(year, month, 1).getDay(); // День недели первого дня месяца
        const daysInMonth = new Date(year, month + 1, 0).getDate(); // Количество дней в месяце

        calendar.innerHTML = ""; // Очистка календаря

        // Заголовок месяца
        const monthTitle = document.createElement("h3");
        monthTitle.textContent = today.toLocaleString("default", { month: "long", year: "numeric" });
        calendar.appendChild(monthTitle);

        // Создание сетки календаря
        const calendarGrid = document.createElement("div");
        calendarGrid.style.display = "grid";
        calendarGrid.style.gridTemplateColumns = "repeat(7, 1fr)";
        calendarGrid.style.gap = "5px";

        // Заполнение пустых дней до начала месяца
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement("div");
            calendarGrid.appendChild(emptyCell);
        }

        // Заполнение дней месяца
        for (let day = 1; day <= daysInMonth; day++) {
            const dateCell = document.createElement("div");
            dateCell.style.padding = "10px";
            dateCell.style.border = "1px solid #ddd";
            dateCell.style.borderRadius = "5px";
            dateCell.style.textAlign = "center";
            dateCell.textContent = day;

            // Проверка наличия событий в этот день
            const event = events.find((e) => new Date(e.date).getDate() === day);
            if (event) {
                dateCell.style.backgroundColor = "#007bff";
                dateCell.style.color = "white";
                dateCell.style.cursor = "pointer";

                // Всплывающее описание события
                dateCell.addEventListener("mouseenter", () => {
                    const tooltip = document.createElement("div");
                    tooltip.textContent = event.title;
                    tooltip.style.position = "absolute";
                    tooltip.style.padding = "5px";
                    tooltip.style.backgroundColor = "#333";
                    tooltip.style.color = "white";
                    tooltip.style.borderRadius = "5px";
                    tooltip.style.zIndex = "1000";
                    document.body.appendChild(tooltip);

                    const rect = dateCell.getBoundingClientRect();
                    tooltip.style.top = `${rect.bottom + window.scrollY}px`;
                    tooltip.style.left = `${rect.left + window.scrollX}px`;

                    dateCell.addEventListener("mouseleave", () => {
                        tooltip.remove();
                    });
                });
            }

            calendarGrid.appendChild(dateCell);
        }

        calendar.appendChild(calendarGrid);
    }

    renderCalendar();
});
