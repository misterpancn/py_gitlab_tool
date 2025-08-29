/**
 * 主JavaScript文件
 */

// 检查用户是否已登录
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token && window.location.pathname !== '/login') {
        window.location.href = '/login';
    }
}

// 设置请求头
function getHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// 处理认证失败
function handleAuthError(status) {
    if (status === 401) {
        // 清除本地存储的token
        localStorage.removeItem('access_token');
        // 如果不是登录页面，则跳转到登录页面
        if (window.location.pathname !== '/login') {
            alert('登录已过期，请重新登录');
            window.location.href = '/login';
            return true;
        }
    }
    return false;
}

// 显示错误信息
function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // 5秒后自动隐藏错误信息
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('zh-CN');
}

// 页面加载时检查认证状态
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname !== '/login') {
        checkAuth();
    }
});