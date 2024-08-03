        function deleteUser(username) {
            fetch(`/delete_user/${username}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to delete user.');
                }
                return response.json();
            })
            .then(data => {
                alert(data.message);
                location.reload(); // Refresh the page to update user list
            })
            .catch(error => alert(error.message));
        }

		        function switchLanguage(language) {
            const elements = document.querySelectorAll('.lang');
            elements.forEach(el => {
                el.classList.toggle('hidden', el.dataset.lang !== language);
            });
        }
		
		function validateForm() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const usernameError = document.getElementById('username-error');
    const passwordError = document.getElementById('password-error');
    
    // Example validation rules
    if (username.length < 4) {
        usernameError.classList.remove('hidden');
        return false;
    } else {
        usernameError.classList.add('hidden');
    }
    
    if (!password.match(/[A-Z]/)) {
        passwordError.classList.remove('hidden');
        return false;
    } else {
        passwordError.classList.add('hidden');
    }
    
    return true;
}
		// 使用fetch API向Flask服务器获取连接客户端列表数据
        fetch('/connected_clients')
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch connected clients.');
        }
        return response.json();
    })
    .then(data => {
        if (!data.hasOwnProperty('clients') || !Array.isArray(data.clients)) {
            throw new Error('Expected an array of clients, but received something else.');
        }
        const clientList = document.getElementById('client-list');
        clientList.innerHTML = ''; // Clear previous list items
        
        data.clients.forEach(client => {
            const listItem = document.createElement('li');
            listItem.textContent = `User: ${client.user}, IP: ${client.ip}`;
            clientList.appendChild(listItem);
        });
    })
    .catch(error => console.error('Error fetching connected clients:', error));
	
	
	// 在 <script> 标签中或者单独的 admin.js 文件中添加以下代码

function refreshClientList() {
    fetch('/connected_clients')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to refresh client list.');
            }
            return response.json();
        })
        .then(data => {
            const clientList = document.getElementById('client-list');
            clientList.innerHTML = ''; // 清空现有列表

            data.clients.forEach(client => {
                const listItem = document.createElement('li');
                listItem.textContent = `User: ${client.user}, IP: ${client.ip}`;
                clientList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error refreshing client list:', error));
}