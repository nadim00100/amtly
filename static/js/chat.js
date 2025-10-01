document.addEventListener('DOMContentLoaded', function() {
    // ========================================================================
    // DOM ELEMENTS
    // ========================================================================
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const fileButton = document.getElementById('file-button');
    const clearButton = document.getElementById('clear-button');
    const fileInput = document.getElementById('file-input');
    const chatMessages = document.getElementById('chat-messages');
    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');

    // Sidebar Elements
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatList = document.getElementById('chat-list');
    const chatTitle = document.getElementById('chat-title');
    const chatSubtitle = document.getElementById('chat-subtitle');

    // ========================================================================
    // STATE - UPDATED FOR MULTIPLE FILES
    // ========================================================================
    let uploadedFiles = []; // Changed from single file to array
    let messageCounter = 0;
    let currentChatId = null;
    let chats = [];
    let isHomePage = true;
    let isProcessing = false;

    // ========================================================================
    // INITIALIZATION
    // ========================================================================
    init();

    function init() {
        setupEventListeners();
        updateFileButton();
        loadChats();
        showHomePage();
    }

    function setupEventListeners() {
        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', handleInputKeypress);
        fileButton.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelection);
        clearButton.addEventListener('click', clearSession);
        document.addEventListener('click', handleExampleClick);
        sidebarToggle.addEventListener('click', toggleSidebar);
        sidebarOverlay.addEventListener('click', closeSidebar);
        newChatBtn.addEventListener('click', startNewChat);
        window.addEventListener('resize', handleResize);
    }

    // ========================================================================
    // HOME PAGE & CHAT MANAGEMENT
    // ========================================================================

    function showHomePage() {
        isHomePage = true;
        currentChatId = null;

        chatTitle.textContent = "Welcome to Amtly";
        chatSubtitle.textContent = "AI German Bureaucracy Assistant";

        showWelcomeMessage();

        chatList.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });

        userInput.focus();
    }

    function startNewChat() {
        showHomePage();
        if (window.innerWidth <= 768) {
            closeSidebar();
        }
    }

    async function loadChats() {
        try {
            const response = await fetch('/api/chats');
            const data = await response.json();

            if (data.success) {
                chats = data.chats;
                renderChatList();
            } else {
                console.error('Failed to load chats:', data.error);
            }
        } catch (error) {
            console.error('Error loading chats:', error);
            showNotification('Failed to load chat history', 'error');
        }
    }

    async function createNewChatWithMessage(message, files = []) {
        try {
            const response = await fetch('/api/chats', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title: 'New Chat' })
            });

            const data = await response.json();

            if (data.success) {
                const newChat = data.chat;
                chats.unshift(newChat);
                renderChatList();

                currentChatId = newChat.id;
                isHomePage = false;

                chatTitle.textContent = newChat.title;
                chatMessages.innerHTML = '';
                updateActiveChatInSidebar(newChat.id);

                return newChat.id;
            } else {
                console.error('Failed to create chat:', data.error);
                showNotification('Failed to create new chat', 'error');
                return null;
            }
        } catch (error) {
            console.error('Error creating chat:', error);
            showNotification('Failed to create new chat', 'error');
            return null;
        }
    }

    async function loadChat(chatId) {
        try {
            setCurrentChat(chatId);
            isHomePage = false;
            showChatLoading();

            const response = await fetch(`/api/chats/${chatId}`);
            const data = await response.json();

            if (data.success) {
                currentChatId = chatId;
                chatTitle.textContent = data.chat.title;
                chatSubtitle.textContent = 'AI German Bureaucracy Assistant';

                chatMessages.innerHTML = '';
                messageCounter = 0;

                if (data.messages && data.messages.length > 0) {
                    const messagesToShow = data.messages.slice(-50);

                    messagesToShow.forEach(msg => {
                        addMessage(msg.content,
                                 msg.role === 'user' ? 'user-message' : 'bot-message',
                                 {
                                     timestamp: msg.timestamp,
                                     sources: msg.sources || [],
                                     type: msg.type || 'chat'
                                 });
                    });

                    if (data.messages.length > 50) {
                        showLoadMoreIndicator(data.messages.length - 50);
                    }
                } else {
                    showChatWelcomeMessage();
                }

                updateActiveChatInSidebar(chatId);
                hideChatLoading();
                scrollToBottom();
            } else {
                console.error('Failed to load chat:', data.error);
                showNotification('Failed to load chat', 'error');
                hideChatLoading();
            }
        } catch (error) {
            console.error('Error loading chat:', error);
            showNotification('Failed to load chat', 'error');
            hideChatLoading();
        }
    }

    function showLoadMoreIndicator(count) {
        const indicator = document.createElement('div');
        indicator.className = 'load-more-indicator';
        indicator.style.textAlign = 'center';
        indicator.style.padding = '10px';
        indicator.style.color = '#8e9aaf';
        indicator.style.fontSize = '14px';
        indicator.textContent = `📜 ${count} older messages not shown`;
        chatMessages.insertBefore(indicator, chatMessages.firstChild);
    }

    async function deleteChat(chatId) {
        if (!confirm('Are you sure you want to delete this chat?')) {
            return;
        }

        try {
            const response = await fetch(`/api/chats/${chatId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                chats = chats.filter(chat => chat.id !== chatId);
                renderChatList();

                if (currentChatId === chatId) {
                    showHomePage();
                }

                showNotification('Chat deleted', 'success');
            } else {
                console.error('Failed to delete chat:', data.error);
                showNotification('Failed to delete chat', 'error');
            }
        } catch (error) {
            console.error('Error deleting chat:', error);
            showNotification('Failed to delete chat', 'error');
        }
    }

    function renderChatList() {
        chatList.innerHTML = '';

        if (chats.length === 0) {
            chatList.innerHTML = '<div class="empty-state">No chats yet. Start a conversation!</div>';
            return;
        }

        chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            chatItem.setAttribute('data-chat-id', chat.id);

            const timeStr = formatChatTime(chat.updated_at);
            const preview = chat.title || 'New conversation';

            chatItem.innerHTML = `
                <div class="chat-title">${escapeHtml(preview)}</div>
                <div class="chat-preview">${chat.message_count} messages</div>
                <div class="chat-time">${timeStr}</div>
                <button class="chat-delete" title="Delete chat">×</button>
            `;

            chatItem.addEventListener('click', (e) => {
                if (e.target.classList.contains('chat-delete')) {
                    e.stopPropagation();
                    deleteChat(chat.id);
                } else {
                    loadChat(chat.id);
                    if (window.innerWidth <= 768) {
                        closeSidebar();
                    }
                }
            });

            chatList.appendChild(chatItem);
        });
    }

    function setCurrentChat(chatId) {
        currentChatId = chatId;
        isHomePage = false;
        updateActiveChatInSidebar(chatId);
    }

    function updateActiveChatInSidebar(chatId) {
        chatList.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });

        const currentChatItem = chatList.querySelector(`[data-chat-id="${chatId}"]`);
        if (currentChatItem) {
            currentChatItem.classList.add('active');
        }
    }

    // ========================================================================
    // SIDEBAR FUNCTIONALITY
    // ========================================================================

    function toggleSidebar() {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('show');
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('show');
    }

    function handleResize() {
        if (window.innerWidth > 768) {
            closeSidebar();
        }
    }

    // ========================================================================
    // FILE HANDLING - UPDATED FOR MULTIPLE FILES
    // ========================================================================

    function handleFileSelection(e) {
        if (e.target.files.length > 0) {
            const maxSize = 16 * 1024 * 1024; // 16MB per file
            const maxFiles = 10; // Maximum 10 files

            const files = Array.from(e.target.files);

            // Check file count
            if (files.length > maxFiles) {
                showNotification(`Maximum ${maxFiles} files allowed`, 'error');
                resetFileInput();
                return;
            }

            // Check each file size
            const oversizedFiles = files.filter(file => file.size > maxSize);
            if (oversizedFiles.length > 0) {
                showNotification(`Some files are too large. Maximum 16MB per file.`, 'error');
                resetFileInput();
                return;
            }

            uploadedFiles = files;
            updateFileButton();
        }
    }

    function resetFileInput() {
        uploadedFiles = [];
        fileInput.value = '';
        updateFileButton();
    }

    function updateFileButton() {
        if (uploadedFiles.length > 0) {
            if (uploadedFiles.length === 1) {
                fileButton.innerHTML = `📎 <span class="button-text">${truncateFilename(uploadedFiles[0].name)}</span>`;
            } else {
                fileButton.innerHTML = `📎 <span class="button-text">${uploadedFiles.length} files</span>`;
            }
            fileButton.classList.add('file-selected');

            const fileList = uploadedFiles.map(f => f.name).join(', ');
            fileButton.title = `Selected: ${fileList}`;
        } else {
            fileButton.innerHTML = '📎 <span class="button-text">Upload</span>';
            fileButton.classList.remove('file-selected');
            fileButton.title = 'Upload Documents (PDF/Image) - Multiple files supported';
        }
    }

    // ========================================================================
    // MESSAGE HANDLING - UPDATED FOR MULTIPLE FILES
    // ========================================================================

    function handleInputKeypress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    function handleExampleClick(e) {
        if (e.target.classList.contains('example-btn')) {
            const exampleText = e.target.getAttribute('data-example') ||
                               e.target.textContent.replace(/[""]/g, '').replace(/^[^"]*"([^"]*)".*$/, '$1');
            userInput.value = exampleText;
            userInput.focus();
            setTimeout(() => sendMessage(), 100);
        }
    }

    async function sendMessage() {
        // Prevent race conditions
        if (isProcessing) {
            console.log('Already processing a message, please wait...');
            return;
        }

        const message = userInput.value.trim();

        if (!message && uploadedFiles.length === 0) {
            userInput.focus();
            return;
        }

        isProcessing = true;
        sendButton.disabled = true;

        try {
            // Create new chat if on home page
            if (isHomePage || !currentChatId) {
                const newChatId = await createNewChatWithMessage(message, uploadedFiles);
                if (!newChatId) {
                    showNotification('Failed to start conversation', 'error');
                    return;
                }
                currentChatId = newChatId;
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            // Add user message to chat
            if (message) {
                addMessage(message, 'user-message', {
                    timestamp: new Date().toISOString()
                });
            }

            // Show file upload message
            if (uploadedFiles.length > 0) {
                const totalSize = uploadedFiles.reduce((sum, file) => sum + file.size, 0);

                if (uploadedFiles.length === 1) {
                    addMessage(
                        `📎 **Uploaded:** ${uploadedFiles[0].name} (${formatFileSize(uploadedFiles[0].size)})`,
                        'user-message',
                        {
                            timestamp: new Date().toISOString(),
                            isFileUpload: true
                        }
                    );
                } else {
                    const fileList = uploadedFiles.map(f => `• ${f.name}`).join('\n');
                    addMessage(
                        `📎 **Uploaded ${uploadedFiles.length} files:**\n${fileList}\n**Total:** ${formatFileSize(totalSize)}`,
                        'user-message',
                        {
                            timestamp: new Date().toISOString(),
                            isFileUpload: true
                        }
                    );
                }
            }

            userInput.value = '';

            // Show loading
            if (uploadedFiles.length > 0) {
                if (uploadedFiles.length === 1) {
                    showLoadingState('Processing document with OCR...');
                } else {
                    showLoadingState(`Processing ${uploadedFiles.length} documents with OCR...`);
                }
            } else if (message && message.toLowerCase().includes('email')) {
                showLoadingState('Generating email...');
            } else {
                showLoadingState('Searching knowledge base...');
            }

            // Prepare form data - MULTIPLE FILES
            const formData = new FormData();
            if (message) {
                formData.append('message', message);
            }

            // Append all files
            uploadedFiles.forEach((file) => {
                formData.append('files', file); // Note: 'files' plural
            });

            formData.append('chat_id', currentChatId);

            // Send to backend
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            hideLoadingState();
            handleChatResponse(data);

            await refreshCurrentChatInSidebar();

        } catch (error) {
            hideLoadingState();
            console.error('Chat error:', error);
            addMessage('❌ **Connection Error:** Please check your internet connection.', 'error-message');
        } finally {
            isProcessing = false;
            sendButton.disabled = false;
            resetFileInput();
            userInput.focus();
        }
    }

    async function refreshCurrentChatInSidebar() {
        try {
            const response = await fetch('/api/chats');
            const data = await response.json();
            if (data.success) {
                chats = data.chats;
                renderChatList();
                updateActiveChatInSidebar(currentChatId);

                const currentChat = chats.find(chat => chat.id === currentChatId);
                if (currentChat) {
                    chatTitle.textContent = currentChat.title;
                }
            }
        } catch (error) {
            console.error('Error refreshing sidebar:', error);
        }
    }

    function handleChatResponse(data) {
        if (data.error || data.error_code) {
            const errorMessage = data.error || 'An error occurred';
            addMessage(`❌ **Error:** ${errorMessage}`, 'error-message');
            return;
        }

        if (data.response) {
            const messageContent = data.response;
            const metadata = {
                timestamp: data.timestamp || new Date().toISOString(),
                sources: data.sources || [],
                type: data.type || 'chat',
                used_knowledge_base: data.used_knowledge_base || false
            };

            addMessage(messageContent, 'bot-message', metadata);

            if (data.type === 'document') {
                showNotification('Document processed successfully!', 'success');
            } else if (data.sources && data.sources.length > 0) {
                showNotification(`Found information from ${data.sources.length} source(s)`, 'success');
            }
        } else {
            addMessage('❌ **Invalid Response:** Received invalid response', 'error-message');
        }
    }

    function clearSession() {
        if (!confirm('This will clear the current chat context. Continue?')) {
            return;
        }

        fetch('/clear_session', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            showNotification('Session context cleared', 'success');
            userInput.focus();
        })
        .catch(error => {
            console.error('Clear session error:', error);
            showNotification('Failed to clear session', 'error');
        });
    }

    // ========================================================================
    // UI HELPERS
    // ========================================================================

    function addMessage(content, className, metadata = {}, isHTML = false) {
        messageCounter++;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.setAttribute('data-timestamp', metadata.timestamp || new Date().toISOString());
        messageDiv.setAttribute('data-message-id', messageCounter);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (isHTML) {
            contentDiv.innerHTML = content;
        } else {
            const formattedContent = formatMessageContent(content);
            contentDiv.innerHTML = formattedContent;
        }

        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = formatTimestamp(metadata.timestamp);
        metaDiv.appendChild(timeSpan);

        // Better source filtering
        if (metadata.sources && Array.isArray(metadata.sources) && metadata.sources.length > 0) {
            const validSources = metadata.sources
                .filter(source => {
                    if (!source || typeof source !== 'string') return false;
                    const cleanSource = source.trim();
                    return cleanSource.length > 0 &&
                           cleanSource !== '*' &&
                           cleanSource !== 'unknown' &&
                           cleanSource !== 'undefined' &&
                           cleanSource !== 'null';
                })
                .map(s => s.trim())
                .filter((value, index, self) => self.indexOf(value) === index);

            if (validSources.length > 0) {
                const sourcesSpan = document.createElement('span');
                sourcesSpan.className = 'message-sources';
                sourcesSpan.textContent = ` • Sources: ${validSources.join(', ')}`;
                metaDiv.appendChild(sourcesSpan);
            }
        }

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(metaDiv);

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function formatMessageContent(content) {
        let formatted = content;
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\n/g, '<br>');
        formatted = formatted.replace(/https?:\/\/[^\s]+/g, '<a href="$&" target="_blank" rel="noopener">$&</a>');
        return formatted;
    }

    function showWelcomeMessage() {
        const welcomeHTML = `
            <div class="message bot-message" id="welcome-message">
                <div class="message-content">
                    <p><strong>🤖 Welcome to Amtly!</strong></p>
                    <p>I'm your AI assistant for German bureaucracy, powered by advanced AI:</p>
                    <ul>
                        <li>📚 <strong>RAG System:</strong> Search official documents</li>
                        <li>📄 <strong>OCR Processing:</strong> Upload PDFs or photos (multiple files supported!)</li>
                        <li>📋 <strong>Form Intelligence:</strong> Get help with forms</li>
                        <li>✉️ <strong>German Emails:</strong> Automatic professional German</li>
                        <li>💾 <strong>Persistent Chats:</strong> Your conversations are saved!</li>
                    </ul>
                    <p><strong>Try these examples:</strong></p>
                    <div class="example-prompts">
                        <button class="example-btn" data-example="Was ist Bürgergeld?">📚 "Was ist Bürgergeld?"</button>
                        <button class="example-btn" data-example="Help me with WBA form">📝 "Help me with WBA form"</button>
                        <button class="example-btn" data-example="Explain this document">📄 "Explain this document"</button>
                        <button class="example-btn" data-example="Write an email to Jobcenter">✉️ "Email to Jobcenter"</button>
                    </div>
                </div>
                <div class="message-meta">
                    <span class="message-time">Just now</span>
                </div>
            </div>
        `;
        chatMessages.innerHTML = welcomeHTML;
    }

    function showChatWelcomeMessage() {
        const welcomeHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    <p><strong>🤖 Ready to help!</strong></p>
                    <p>Ask me about German bureaucracy, upload documents, or request form help.</p>
                </div>
                <div class="message-meta">
                    <span class="message-time">Just now</span>
                </div>
            </div>
        `;
        chatMessages.innerHTML = welcomeHTML;
    }

    function showLoadingState(message = 'Amtly AI is processing...') {
        loadingText.textContent = message;
        loading.classList.remove('hidden');
        scrollToBottom();
    }

    function hideLoadingState() {
        loading.classList.add('hidden');
    }

    function showChatLoading() {
        chatMessages.innerHTML = '<div class="chat-loading"><div class="loading-spinner"></div><p>Loading chat...</p></div>';
    }

    function hideChatLoading() {
        // Replaced by actual messages
    }

    function showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container') || createNotificationContainer();

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 4000);
    }

    function createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // ========================================================================
    // UTILITY FUNCTIONS
    // ========================================================================

    function formatTimestamp(timestamp) {
        if (!timestamp) return 'Just now';

        const date = new Date(timestamp);
        const now = new Date();
        const diffMinutes = Math.floor((now - date) / (1000 * 60));

        if (diffMinutes < 1) return 'Just now';
        if (diffMinutes < 60) return `${diffMinutes}m ago`;
        if (diffMinutes < 24 * 60) return `${Math.floor(diffMinutes / 60)}h ago`;

        return date.toLocaleDateString();
    }

    function formatChatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;

        return date.toLocaleDateString();
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function truncateFilename(filename, maxLength = 15) {
        if (filename.length <= maxLength) return filename;

        const extension = filename.split('.').pop();
        const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
        const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4);

        return `${truncatedName}...${extension}`;
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});