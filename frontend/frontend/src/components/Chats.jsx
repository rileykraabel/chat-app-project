import Chat from './Chat.jsx';
import LeftNav from './LeftNav';

function Chats() {
// Header height
const headerHeight = 48; // Assuming 12 * 4px for each unit of height

// Calculate remaining height after considering the header
const remainingHeight = `calc(100vh - ${headerHeight}px)`;

  return (
    <div className="flex flex-row h-screen" style={{ height: remainingHeight }}>
      <div className="w-1/5 border-sky-300">
        <LeftNav />
      </div>
      <div className="w-4/5 border-r-4 border-sky-300 overflow-y-scroll">
        <Chat />
      </div>
    </div>
  );
}

export default Chats;