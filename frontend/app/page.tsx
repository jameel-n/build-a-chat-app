import Sidebar from '@/components/Sidebar';
import ChatCanvas from '@/components/ChatCanvas';

export default function Home() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#1a1b26]">
      <Sidebar />
      <ChatCanvas />
    </div>
  );
}
