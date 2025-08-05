const { useState, useEffect, useRef } = React;

// --- Main Chat Component ---
function App() {
  // State for messages in the chat window
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! Ask me any questions you have about Hemant's resume.",
    },
  ]);

  // State for the user's input
  const [input, setInput] = useState('');
  // State to track if the assistant is thinking
  const [isLoading, setIsLoading] = useState(false);

  // Ref to the end of the messages list for auto-scrolling
  const messagesEndRef = useRef(null);

  // Function to scroll to the bottom of the messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Scroll to bottom whenever messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // --- Form Submission Handler ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input; // Capture input before clearing
    setInput('');
    setIsLoading(true);

    // --- API Call to the Flask Backend ---
    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: currentInput }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Could not parse error response.' }));
        throw new Error(`Server responded with status ${response.status}: ${errorData.error || 'Unknown error'}`);
      }

      const data = await response.json();
      const assistantMessage = { role: 'assistant', content: data.answer };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
      const errorMessage = { role: 'assistant', content: `Sorry, an error occurred. Please make sure the Python backend is running. [${error.message}]` };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Render JSX ---
  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto bg-white border border-gray-200 rounded-lg shadow-lg font-sans">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-800">Chat with Hemant's Resume</h1>
        <p className="text-sm text-gray-500">Ask questions about his experience</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
        {messages.map((msg, index) => (
          <div key={index} className={`flex my-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`rounded-lg px-4 py-2 max-w-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start my-2">
            <div className="rounded-lg px-4 py-2 bg-gray-200 text-gray-800">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="ml-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300"
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

// Mount the App component to the 'root' div in index.html
ReactDOM.render(<App />, document.getElementById('root'));