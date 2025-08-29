/**
 * 登录页面JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            // 构建表单数据
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            
            // 发送登录请求
            const response = await fetch('/api/token', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || '登录失败');
            }
            
            // 保存令牌到本地存储
            localStorage.setItem('access_token', data.access_token);
            
            // 重定向到首页
            window.location.href = '/';
            
        } catch (error) {
            showError(error.message);
        }
    });
});
