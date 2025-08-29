/**
 * 首页JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    const queryForm = document.getElementById('query-form');
    const resultsTableContainer = document.getElementById('results-table-container');
    const resultsBody = document.getElementById('results-body');
    const loading = document.getElementById('loading');
    const noResults = document.getElementById('no-results');
    const commitModal = document.getElementById('commit-modal');
    const commitDetails = document.getElementById('commit-details');
    const closeModal = document.querySelector('.close');
    
    // 分页相关元素
    const paginationInfo = document.getElementById('pagination-info');
    const currentPageEl = document.getElementById('current-page');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    
    // 文本导出相关元素
    const exportTextBtn = document.getElementById('export-text-btn');
    const textExportModal = document.getElementById('text-export-modal');
    const textExportContent = document.getElementById('text-export-content');
    const textExportClose = document.querySelector('.text-export-close');
    const copyTextBtn = document.getElementById('copy-text-btn');
    
    // 查询参数
    let currentQueryParams = {
        project_id: '',
        branch: '',
        start_date: '',
        end_date: '',
        author_emails: '',
        page: 1,
        page_size: 10
    };
    
    // 分页数据
    let paginationData = {
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 1
    };
    
    // 设置日期默认值为当天和当月最后一天
    function setDefaultDates() {
        const today = new Date();
        const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        
        document.getElementById('start_date').value = formatDateForInput(today);
        document.getElementById('end_date').value = formatDateForInput(lastDay);
    }
    
    // 格式化日期为YYYY-MM-DD格式
    function formatDateForInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // 关闭提交详情模态框
    closeModal.addEventListener('click', function() {
        commitModal.style.display = 'none';
    });
    
    // 关闭文本导出模态框
    textExportClose.addEventListener('click', function() {
        textExportModal.style.display = 'none';
    });
    
    // 点击模态框外部关闭模态框
    window.addEventListener('click', function(event) {
        if (event.target === commitModal) {
            commitModal.style.display = 'none';
        }
        if (event.target === textExportModal) {
            textExportModal.style.display = 'none';
        }
    });
    
    // 显示提交详情
    function showCommitDetails(commit) {
        commitDetails.innerHTML = `
            <dl>
                <dt>提交ID</dt>
                <dd>${commit.short_id}</dd>
                
                <dt>作者</dt>
                <dd>${commit.author_name}</dd>
                
                <dt>邮箱</dt>
                <dd>${commit.author_email}</dd>
                
                <dt>时间</dt>
                <dd>${formatDateTime(commit.created_at)}</dd>
                
                <dt>标题</dt>
                <dd>${commit.title}</dd>
                
                <dt>完整信息</dt>
                <dd class="commit-message">${commit.message}</dd>
            </dl>
        `;
        
        commitModal.style.display = 'block';
    }
    
    // 更新分页信息
    function updatePagination(data) {
        paginationData = {
            total: data.total,
            page: data.page,
            page_size: data.page_size,
            total_pages: data.total_pages
        };
        
        // 计算当前页显示的记录范围
        const start = data.total > 0 ? (data.page - 1) * data.page_size + 1 : 0;
        const end = Math.min(data.page * data.page_size, data.total);
        
        // 更新分页信息
        paginationInfo.textContent = `显示 ${start}-${end} 条，共 ${data.total} 条`;
        currentPageEl.textContent = `第 ${data.page} 页，共 ${data.total_pages} 页`;
        
        // 更新分页按钮状态
        prevPageBtn.disabled = data.page <= 1;
        nextPageBtn.disabled = data.page >= data.total_pages;
    }
    
    // 处理认证错误
    async function processResponse(response) {
        if (response.status === 401) {
            const data = await response.json();
            if (data.auth_error) {
                // 清除本地存储的token
                localStorage.removeItem('access_token');
                // 显示提示
                alert(data.detail || '认证失败，请重新登录');
                // 重定向到登录页面
                window.location.href = data.redirect || '/login';
                return null;
            }
        }
        return response;
    }
    
    // 加载提交数据
    async function loadCommits(params) {
        // 显示加载状态
        loading.style.display = 'block';
        resultsTableContainer.style.display = 'none';
        noResults.style.display = 'none';
        
        try {
            // 发送请求获取提交信息
            const response = await fetch('/api/commits', {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify(params)
            });
            
            // 处理认证错误
            const processedResponse = await processResponse(response);
            if (!processedResponse) return;
            
            const data = await processedResponse.json();
            
            if (!processedResponse.ok) {
                throw new Error(data.detail || '获取提交信息失败');
            }
            
            // 隐藏加载状态
            loading.style.display = 'none';
            
            // 如果没有结果
            if (data.items.length === 0) {
                noResults.style.display = 'block';
                return;
            }
            
            // 清空结果表格
            resultsBody.innerHTML = '';
            
            // 填充结果表格
            data.items.forEach(commit => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${commit.short_id}</td>
                    <td>${commit.author_name}</td>
                    <td>${commit.author_email}</td>
                    <td>${formatDateTime(commit.created_at)}</td>
                    <td>${commit.title}</td>
                    <td><span class="view-details">查看详情</span></td>
                `;
                
                // 添加查看详情事件
                row.querySelector('.view-details').addEventListener('click', function() {
                    showCommitDetails(commit);
                });
                
                resultsBody.appendChild(row);
            });
            
            // 更新分页信息
            updatePagination(data);
            
            // 显示结果表格
            resultsTableContainer.style.display = 'block';
            
        } catch (error) {
            loading.style.display = 'none';
            showError(error.message);
        }
    }
    
    // 导出文本格式
    async function exportTextFormat(params) {
        // 显示加载状态
        loading.style.display = 'block';
        
        try {
            // 发送请求获取文本格式的提交信息
            const response = await fetch('/api/commits/text', {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify(params)
            });
            
            // 处理认证错误
            const processedResponse = await processResponse(response);
            if (!processedResponse) return;
            
            const data = await processedResponse.json();
            
            if (!processedResponse.ok) {
                throw new Error(data.detail || '导出文本格式失败');
            }
            
            // 隐藏加载状态
            loading.style.display = 'none';
            
            // 如果没有内容
            if (!data.content) {
                showError('没有可导出的内容');
                return;
            }
            
            // 显示文本内容
            textExportContent.textContent = data.content;
            textExportModal.style.display = 'block';
            
        } catch (error) {
            loading.style.display = 'none';
            showError(error.message);
        }
    }
    
    // 复制文本到剪贴板
    copyTextBtn.addEventListener('click', function() {
        const text = textExportContent.textContent;
        
        if (!text) {
            showError('没有可复制的内容');
            return;
        }
        
        // 创建临时文本区域
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        
        // 选择文本并复制
        textarea.select();
        document.execCommand('copy');
        
        // 移除临时文本区域
        document.body.removeChild(textarea);
        
        // 显示成功提示
        alert('已复制到剪贴板');
    });
    
    // 查询提交信息
    queryForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // 获取表单数据
        const projectId = document.getElementById('project_id').value;
        const branch = document.getElementById('branch').value;
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const authorEmails = document.getElementById('author_emails').value;
        const pageSize = parseInt(document.getElementById('page_size').value);
        
        // 更新当前查询参数
        currentQueryParams = {
            project_id: projectId,
            branch: branch,
            start_date: startDate,
            end_date: endDate,
            author_emails: authorEmails,
            page: 1, // 重置为第一页
            page_size: pageSize
        };
        
        // 加载提交数据
        await loadCommits(currentQueryParams);
    });
    
    // 导出文本格式
    exportTextBtn.addEventListener('click', async function() {
        // 获取表单数据
        const projectId = document.getElementById('project_id').value;
        const branch = document.getElementById('branch').value;
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const authorEmails = document.getElementById('author_emails').value;
        
        if (!projectId || !branch || !startDate || !endDate) {
            showError('请填写必填字段');
            return;
        }
        
        // 导出文本格式
        await exportTextFormat({
            project_id: projectId,
            branch: branch,
            start_date: startDate,
            end_date: endDate,
            author_emails: authorEmails
        });
    });
    
    // 上一页
    prevPageBtn.addEventListener('click', async function() {
        if (currentQueryParams.page > 1) {
            currentQueryParams.page--;
            await loadCommits(currentQueryParams);
        }
    });
    
    // 下一页
    nextPageBtn.addEventListener('click', async function() {
        if (currentQueryParams.page < paginationData.total_pages) {
            currentQueryParams.page++;
            await loadCommits(currentQueryParams);
        }
    });
    
    // 设置默认日期
    setDefaultDates();
});