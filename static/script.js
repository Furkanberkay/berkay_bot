document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');

    // Form gönderildiğinde
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Kullanıcı mesajını ekle
        addMessage(message, 'user');
        
        // Input'u temizle ve devre dışı bırak
        userInput.value = '';
        userInput.disabled = true;
        sendButton.disabled = true;
        sendButton.innerHTML = '<span class="loading"></span> Yanıt bekleniyor...';

        // Formu gönder
        const formData = new FormData();
        formData.append('user_input', message);
        
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            // HTML'den bot yanıtını çıkar
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const responseContent = doc.querySelector('.response-content');
            
            if (responseContent) {
                addMessage(responseContent.textContent, 'bot');
            }
        })
        .catch(error => {
            console.error('Hata:', error);
            addMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'bot');
        })
        .finally(() => {
            // Input'u tekrar aktif et
            userInput.disabled = false;
            sendButton.disabled = false;
            sendButton.innerHTML = '<span>Gönder</span>';
            userInput.focus();
        });
    });

    // Mesaj ekleme fonksiyonu
    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Otomatik scroll
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Enter tuşu ile gönderme
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Input'a odaklan
    userInput.focus();
});
