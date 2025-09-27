// BEFORE (what you currently have):
async function loadChats() {
    try {
        const response = await fetch('/api/chats');
        const data = await response.json();

        if (data.success) {
            chats = data.chats;
            renderChatList();

            await createNewChat();  // ← THIS LINE (line ~74)

        } else {
            console.error('Failed to load chats:', data.error);
            await createNewChat();  // ← Don't change this one
        }
    } catch (error) {
        console.error('Error loading chats:', error);
        showNotification('Failed to load chat history', 'error');
    }
}

// AFTER (what it should be):
async function loadChats() {
    try {
        const response = await fetch('/api/chats');
        const data = await response.json();

        if (data.success) {
            chats = data.chats;
            renderChatList();

            // REPLACED the single line with conditional logic:
            if (chats.length > 0) {
                await loadChat(chats[0].id);
            } else {
                await createNewChat();
            }

        } else {
            console.error('Failed to load chats:', data.error);
            await createNewChat();  // ← Keep this one unchanged
        }
    } catch (error) {
        console.error('Error loading chats:', error);
        showNotification('Failed to load chat history', 'error');
    }
}