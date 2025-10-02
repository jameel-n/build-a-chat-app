'use client';

export default function ChatCanvas() {
  return (
    <div className="flex-1 flex flex-col h-screen bg-[#1a1b26]">
      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
      </div>
      {/* Input Area */}
      <div className="border-t border-[#2a2e42] p-4">
        <div className="max-w-3xl mx-auto">
          <div className="relative">
            <textarea
              placeholder="Type your message here..."
              className="w-full bg-[#24283b] text-[#c0caf5] placeholder-[#565f89] rounded-lg px-4 py-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-[#7aa2f7] border border-[#2a2e42]"
              rows={3}
            />
            <button className="absolute right-3 bottom-3 text-[#7aa2f7] hover:text-[#89b4fa] transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
