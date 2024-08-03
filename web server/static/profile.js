        function logout() {
            fetch('/logout_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                // 如果需要CSRF令牌，可以在这里添加
                // body: JSON.stringify({ csrf_token: 'your_csrf_token_here' }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                alert(data.message); // 显示成功的登出消息
                // 可以重定向到登录页面或其他适当的页面
                window.location.href = '/login'; // 示例中重定向到登录页面
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
                alert('登出失败，请重试。');
            });
        }
		
        // 使用 Fetch API 获取随机背景图片路径
        fetch('/api/background-image')
            .then(response => response.json())
            .then(data => {
                const imageUrl = data.imageUrl;
                document.body.style.backgroundImage = `url(${imageUrl})`;
            })
            .catch(error => console.error('Error fetching random background image:', error));
