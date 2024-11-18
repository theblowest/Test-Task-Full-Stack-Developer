document.addEventListener("DOMContentLoaded", function() {
    const fadeElements = document.querySelectorAll(".fade-in");
    fadeElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add("visible");
        }, index * 300); // Задержка для плавности
    });

    
    // Показать/скрыть пароль
    const toggleButtons = document.querySelectorAll('.password-toggle');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const passwordInput = this.previousElementSibling;
            const icon = this.querySelector('i');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            }
        });
    });

    // Анимация кнопки при отправке
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function () {
            const submitButton = loginForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...';
        });
    }

    // Уведомления об ошибках или успешных действиях
    function showAlert(message, type = 'success') {
        const alertContainer = document.createElement('div');
        alertContainer.classList.add('alert', `alert-${type}`, 'alert-dismissible', 'fade', 'show');
        alertContainer.role = 'alert';
        alertContainer.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
        document.body.appendChild(alertContainer);
        setTimeout(() => alertContainer.remove(), 5000); // Удаляем уведомление через 5 секунд
    }

    // Пример работы с AJAX для загрузки файла
    document.querySelector('#uploadForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(this);
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('File uploaded successfully!', 'success');
            } else {
                showAlert('Error uploading file.', 'danger');
            }
        })
        .catch(error => {
            showAlert('An error occurred. Please try again.', 'danger');
            console.error('Error:', error);
        });
    });

    // Плавный скролл к элементам с ID
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

