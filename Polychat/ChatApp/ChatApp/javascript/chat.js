const form = document.querySelector(".typing-area"),
    incoming_id = form.querySelector(".incoming_id").value,
    inputField = form.querySelector(".input-field"),
    sendBtn = form.querySelector("button"),
    chatBox = document.querySelector(".chat-box");

form.onsubmit = (e) => {
    e.preventDefault();
}

inputField.focus();
inputField.onkeyup = () => {
    if (inputField.value != "") {
        sendBtn.classList.add("active");
    } else {
        sendBtn.classList.remove("active");
    }
}

sendBtn.onclick = () => {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "php/insert-chat.php", true);
    xhr.onload = () => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                inputField.value = "";
                scrollToBottom();
            }
        }
    }
    let formData = new FormData(form);
    xhr.send(formData);
}

chatBox.onmouseenter = () => {
    chatBox.classList.add("active");
}

chatBox.onmouseleave = () => {
    chatBox.classList.remove("active");
}

// Function to mark message as read
function markMessageAsRead(messageId) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'php/mark-as-read.php', true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                console.log('Message marked as read:', messageId);
            } else {
                console.error('Failed to mark message as read');
            }
        }
    };
    xhr.send('messageId=' + messageId);
}

// Attach event listener to chatBox for message click events
chatBox.addEventListener('click', function(event) {
    if (event.target.classList.contains('message')) {
        event.target.classList.add('read'); // Mark the message as read visually
        let messageId = event.target.dataset.messageId;
        markMessageAsRead(messageId); // Send request to mark message as read
    }
});

// Function to scroll chat box to the bottom
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to update chat box with new messages
function updateChatBox(data) {
    chatBox.innerHTML = data;
    if (!chatBox.classList.contains("active")) {
        scrollToBottom();
    }
}

// Function to periodically fetch new messages
function fetchNewMessages() {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "php/get-chat.php", true);
    xhr.onload = () => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                let data = xhr.response;
                updateChatBox(data);
            }
        }
    }
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("incoming_id=" + incoming_id);
}

// Fetch new messages initially and set interval to fetch periodically
fetchNewMessages();
setInterval(fetchNewMessages, 500);