const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = [];

class Particle {
    constructor(x, y, radius, color, dx, dy) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
        this.dx = dx;
        this.dy = dy;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        ctx.fillStyle = this.color;
        ctx.fill();
    }

    update() {
        this.x += this.dx;
        this.y += this.dy;

        if (this.x + this.radius > canvas.width || this.x - this.radius < 0) {
            this.dx = -this.dx;
        }

        if (this.y + this.radius > canvas.height || this.y - this.radius < 0) {
            this.dy = -this.dy;
        }

        this.draw();
    }
}

function createParticles() {
    for (let i = 0; i < 100; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const radius = Math.random() * 3;
        const color = '#000000';
        const dx = (Math.random() - 0.5) * 2;
        const dy = (Math.random() - 0.5) * 2;

        particles.push(new Particle(x, y, radius, color, dx, dy));
    }
}

function animateParticles() {
    if (!document.hidden) {
        requestAnimationFrame(animateParticles);
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
        }
    }
}


createParticles();
animateParticles();
//登录相关的
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginLink = document.getElementById('login-link');
const registerLink = document.getElementById('register-link');
const langToggle = document.getElementById('lang-toggle');

loginLink.addEventListener('click', function(e) {
    e.preventDefault();
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
});

registerLink.addEventListener('click', function(e) {
    e.preventDefault();
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
});

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginButton = document.getElementById('login-button');
    const registerLink = document.getElementById('register-link');
    const loginLink = document.getElementById('login-link');

    // 显示登录表单，隐藏注册表单
    function showLoginForm() {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    }

    // 显示注册表单，隐藏登录表单
    function showRegisterForm() {
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    }

    // 点击“点击注册”链接切换到注册表单
    registerLink.addEventListener('click', function(event) {
        event.preventDefault(); // 阻止默认跳转行为
        showRegisterForm();
    });

    // 点击“点击登录”链接切换到登录表单
    loginLink.addEventListener('click', function(event) {
        event.preventDefault(); // 阻止默认跳转行为
        showLoginForm();
    });

    // 处理登录按钮点击事件
    loginButton.addEventListener('click', function() {
		const username = document.getElementById('username').value;
		const password = document.getElementById('password').value;

        // 向后端发送登录请求
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Login failed.');
            }
            // 登录成功后跳转到用户个人资料页面
            window.location.href = '/profile';
        })
        .catch(error => {
            console.error('Login error:', error);
            alert('登录失败，请检查用户名和密码。');
        });
    });
});


		// 注册表单提交事件处理
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('register-form');
    const registerButton = document.getElementById('register-button');
    const loginLink = document.getElementById('login-link');

    // 点击登录链接的处理
    loginLink.addEventListener('click', function(event) {
        event.preventDefault();
        // 这里可以跳转到登录页面的逻辑
        console.log('跳转到登录页面');
    });

    // 注册按钮点击事件处理
    registerButton.addEventListener('click', function(event) {
        event.preventDefault(); // 阻止表单默认提交行为

        // 获取表单字段的值
        const username = document.getElementById('new-username').value;
        const password = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        // 前端验证确认密码
        if (password !== confirmPassword) {
            alert('确认密码不匹配，请重新输入。');
            return;
        }

        // 向后端发送注册请求
        const data = {
            username: username,
            password: password
        };

        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('注册失败，请稍后重试。');
            }
            // 注册成功后的处理，例如跳转到登录页面
            window.location.href = '/'; // 这里是示例，可以根据实际需求调整跳转页面
        })
        .catch(error => {
            console.error('注册失败:', error);
            alert('注册失败，请稍后重试。');
        });
    });
});



