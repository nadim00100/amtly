document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
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

    // State
    let uploadedFile = null;
    let messageCounter = 0;
    let currentChatId = null;
    let chats = [];
    let isHomePage = true; // NEW: Track if we're on home page

    // Initialize
    init();

    function init() {
        setupEventListeners();
        updateFileButton();
        loadChats();
        showHomePage(); // NEW: Always start with home page
    }

    function setupEventListeners() {
        // Basic chat functionality
        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', handleInputKeypress);

        // File handling
        fileButton.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelection);

        // Session management
        clearButton.addEventListener('click', clearSession);

        // Example prompts
        document.addEventListener('click', handleExampleClick);

        // Sidebar functionality
        sidebarToggle.addEventListener('click', toggleSidebar);
        sidebarOverlay.addEventListener('click', closeSidebar);
        newChatBtn.addEventListener('click', startNewChat); // UPDATED: Different function

        // Mobile responsiveness
        window.addEventListener('resize', handleResize);
    }

    // ========================================================================
    // HOME PAGE & CHAT MANAGEMENT
    // ========================================================================

    function showHomePage() {
        // Set home page state
        isHomePage = true;
        currentChatId = null;

        // Update header
        chatTitle.textContent = "Welcome to Amtly";
        chatSubtitle.textContent = "AI German Bureaucracy Assistant";

        // Show welcome message
        showWelcomeMessage();

        // Remove active state from all chats in sidebar
        chatList.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });

        // Focus on input
        userInput.focus();
    }

    function startNewChat() {
        // Simply go to home page - don't create chat until user sends message
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
                // REMOVED: Don't auto-load any chat - stay on home page
            } else {
                console.error('Failed to load chats:', data.error);
                // REMOVED: Don't create new chat automatically
            }
        } catch (error) {
            console.error('Error loading chats:', error);
            showNotification('Failed to load chat history', 'error');
        }
    }

    async function createNewChatWithMessage(message, file = null) {
        // Create new chat when user actually sends a message
        try {
            const response = await fetch('/api/chats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title: 'New Chat' }) // Will be renamed automatically
            });

            const data = await response.json();

            if (data.success) {
                const newChat = data.chat;
                chats.unshift(newChat); // Add to beginning
                renderChatList();

                // Set as current chat
                currentChatId = newChat.id;
                isHomePage = false;

                // Update header with initial title (will change after message)
                chatTitle.textContent = newChat.title;

                // Clear welcome message
                chatMessages.innerHTML = '';

                // Update active chat in sidebar
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
            isHomePage = false; // We're now in a specific chat
            showChatLoading();

            const response = await fetch(`/api/chats/${chatId}`);
            const data = await response.json();

            if (data.success) {
                currentChatId = chatId;

                // Update header
                chatTitle.textContent = data.chat.title;
                chatSubtitle.textContent = 'AI German Bureaucracy Assistant';

                // Clear messages and load from database
                chatMessages.innerHTML = '';
                messageCounter = 0;

                // Load messages
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        addMessage(msg.content,
                                 msg.role === 'user' ? 'user-message' : 'bot-message',
                                 {
                                     timestamp: msg.timestamp,
                                     sources: msg.sources || [],
                                     type: msg.type || 'chat'
                                 });
                    });
                } else {
                    // Show welcome message for empty chats
                    showChatWelcomeMessage();
                }

                // Update active chat in sidebar
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

    async function deleteChat(chatId) {
        if (!confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/chats/${chatId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                // Remove from local state
                chats = chats.filter(chat => chat.id !== chatId);
                renderChatList();

                // If this was the current chat, go to home page
                if (currentChatId === chatId) {
                    showHomePage(); // UPDATED: Go to home page instead of creating new chat
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

            // Chat click handler
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
        // Remove active class from all chat items
        chatList.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to current chat
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
    // MESSAGE HANDLING (Updated for home page behavior)
    // ========================================================================

    function handleInputKeypress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    function handleFileSelection(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            const maxSize = 16 * 1024 * 1024; // 16MB

            if (file.size > maxSize) {
                showNotification('File too large. Maximum size is 16MB.', 'error');
                resetFileInput();
                return;
            }

            uploadedFile = file;
            updateFileButton();
        }
    }

    function resetFileInput() {
        uploadedFile = null;
        fileInput.value = '';
        updateFileButton();
    }

    function handleExampleClick(e) {
        if (e.target.classList.contains('example-btn')) {
            const exampleText = e.target.getAttribute('data-example') || e.target.textContent.replace(/[""]/g, '').replace(/^[^"]*"([^"]*)".*$/, '$1');
            userInput.value = exampleText;
            userInput.focus();
            // Auto-send example
            setTimeout(() => sendMessage(), 100);
        }
    }

    async function sendMessage() {
        const message = userInput.value.trim();

        if (!message && !uploadedFile) {
            userInput.focus();
            return;
        }

        // UPDATED: Create new chat if we're on home page
        if (isHomePage || !currentChatId) {
            const newChatId = await createNewChatWithMessage(message, uploadedFile);
            if (!newChatId) {
                showNotification('Failed to start conversation', 'error');
                return;
            }
            currentChatId = newChatId;
        }

        // Disable send button during processing
        sendButton.disabled = true;

        // Add user message to chat if there's text
        if (message) {
            addMessage(message, 'user-message', {
                timestamp: new Date().toISOString()
            });
        }

        // Show file info if file was uploaded
        if (uploadedFile) {
            addMessage(`📎 **Uploaded:** ${uploadedFile.name} (${formatFileSize(uploadedFile.size)})`, 'user-message', {
                timestamp: new Date().toISOString(),
                isFileUpload: true
            });
        }

        // Clear input
        userInput.value = '';

        // Show appropriate loading message
        if (uploadedFile) {
            showLoadingState('Processing document with OCR...');
        } else if (message && message.toLowerCase().includes('email')) {
            showLoadingState('Generating email...');
        } else if (message && (message.toLowerCase().includes('translate') || message.toLowerCase().includes('übersetzen'))) {
            showLoadingState('Translating and explaining...');
        } else if (message && message.toLowerCase().includes('form')) {
            showLoadingState('Analyzing form requirements...');
        } else {
            showLoadingState('Searching knowledge base...');
        }

        // Prepare form data
        const formData = new FormData();
        if (message) {
            formData.append('message', message);
        }
        if (uploadedFile) {
            formData.append('file', uploadedFile);
        }
        // Add current chat ID
        formData.append('chat_id', currentChatId);

        // Send to backend
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            hideLoadingState();
            handleChatResponse(data);

            // UPDATED: Refresh chat list and update title after first message
            await refreshCurrentChatInSidebar();

        } catch (error) {
            hideLoadingState();
            console.error('Chat error:', error);
            addMessage('❌ **Connection Error:** Please check your internet connection and try again.', 'error-message');
        } finally {
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

                // UPDATED: Also update the header title with the new smart title
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

            // Show success notification for different types
            if (data.type === 'document' || messageContent.includes('📄 **Document Analysis')) {
                showNotification('Document processed successfully!', 'success');
            } else if (messageContent.includes('📝 **Form')) {
                showNotification('Form help provided!', 'success');
            } else if (data.sources && data.sources.length > 0) {
                showNotification(`Found information from ${data.sources.length} source(s)`, 'success');
            }
        } else {
            addMessage('❌ **Invalid Response:** Received invalid response from server', 'error-message');
        }
    }

    function clearSession() {
        if (!confirm('This will clear the current chat context but keep the message history. Continue?')) {
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
            // Convert markdown-like formatting
            const formattedContent = formatMessageContent(content);
            contentDiv.innerHTML = formattedContent;
        }

        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = formatTimestamp(metadata.timestamp);
        metaDiv.appendChild(timeSpan);

        // Add sources if available and valid
        if (metadata.sources && Array.isArray(metadata.sources) && metadata.sources.length > 0) {
            // Filter out empty or invalid sources, but keep actual filenames
            const validSources = metadata.sources.filter(source => {
                if (!source || typeof source !== 'string') return false;
                const cleanSource = source.trim();
                // Keep actual filenames and valid source names, filter out just "*" or empty strings
                return cleanSource !== '' && cleanSource !== '*' && cleanSource !== 'unknown';
            });

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
        // Convert basic markdown-like formatting
        let formatted = content;

        // Bold text **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        // Links (simple)
        formatted = formatted.replace(/https?:\/\/[^\s]+/g, '<a href="$&" target="_blank" rel="noopener">$&</a>');

        // List items starting with •
        formatted = formatted.replace(/^• /gm, '• ');

        return formatted;
    }

    function showWelcomeMessage() {
        const welcomeHTML = `
            <div class="message bot-message" id="welcome-message">
                <div class="message-content">
                    <p><strong>🤖 Welcome to Amtly!</strong></p>
                    <p>I'm your AI assistant for German bureaucracy, powered by advanced AI technologies:</p>
                    <ul>
                        <li>📚 <strong>RAG System:</strong> Search official documents with vector embeddings</li>
                        <li>📄 <strong>OCR Processing:</strong> Upload PDFs or photos for text extraction</li>
                        <li>📋 <strong>Form Intelligence:</strong> Get help with specific forms and sections</li>
                        <li>✉️ <strong>German Emails:</strong> All emails to German offices automatically in German</li>
                        <li>🤖 <strong>Smart Commands:</strong> I do exactly what you ask - explain, translate, or both!</li>
                        <li>💾 <strong>Persistent Chats:</strong> Your conversations are saved and organized!</li>
                    </ul>
                    <p><strong>Try these examples:</strong></p>
                    <div class="example-prompts">
                        <button class="example-btn" data-example="Was ist Bürgergeld?">📚 "Was ist Bürgergeld?"</button>
                        <button class="example-btn" data-example="Help me with WBA form">📝 "Help me with WBA form"</button>
                        <button class="example-btn" data-example="WBA form section B">🎯 "WBA form section B"</button>
                        <button class="example-btn" data-example="Explain this document">📄 "Explain this document"</button>
                        <button class="example-btn" data-example="Write an email to Jobcenter about my application">✉️ "Email to Jobcenter (auto-DE)"</button>
                        <button class="example-btn" data-example="Schreibe eine E-Mail an das Sozialamt">📧 "E-Mail an Sozialamt"</button>
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
        // Simplified welcome for existing but empty chats
        const welcomeHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    <p><strong>🤖 Ready to help!</strong></p>
                    <p>Ask me anything about German bureaucracy, upload documents, or request form help.</p>
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
        // Chat loading will be replaced by actual messages
    }

    function updateFileButton() {
        if (uploadedFile) {
            fileButton.innerHTML = `📎 <span class="button-text">${truncateFilename(uploadedFile.name)}</span>`;
            fileButton.classList.add('file-selected');
            fileButton.title = `Selected: ${uploadedFile.name} - Click to change`;
        } else {
            fileButton.innerHTML = '📎 <span class="button-text">Upload</span>';
            fileButton.classList.remove('file-selected');
            fileButton.title = 'Upload Document (PDF/Image)';
        }
    }

    function showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container') || createNotificationContainer();

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        // Auto-remove after 4 seconds
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