import { useState } from "react";
import { NavLink } from "react-router-dom";
import { useQuery } from "react-query";
import { useAuth } from "../context/auth.jsx";

const emptyChat = (id) => ({
  id,
  name: "loading...",
  empty: true,
});

function Link({ chat }) {
  const url = chat.empty ? "#" : `/chats/${chat.id}`;
  const className = ({ isActive }) => [
    "p-2",
    "hover:bg-fuchsia-900 hover:text-green-300",
    "flex flex-row justify-between",
    isActive ?
      "bg-fuchsia-900 text-green-300 font-bold" :
      ""
  ].join(" ");

  const chatName = ({ isActive }) => (
    (isActive ? "\u00bb " : "") + chat.name
  );

  return (
    <NavLink to={url} className={className}>
      {chatName}
    </NavLink>
  );
}

function LeftNav() {
  const { token } = useAuth();
  const [search, setSearch] = useState("");
  const { data } = useQuery({
    queryKey: ["chats"],
    queryFn: () => (
      fetch("http://127.0.0.1:8000/chats", {
        headers: {
          Authorization: `Bearer ${token}`
        },
      })
        .then((response) => response.json())
    ),
  });

  const regex = new RegExp(search.split("").join(".*"));
  const chats = ( data?.chats || [1, 2, 3].map(emptyChat)
  ).filter((chat) => (
    search === "" || regex.test(chat.name)
  ));

  return (
    <nav className="flex flex-col border-l-4 border-sky-300 h-main">
      <div className="flex flex-col overflow-y-scroll border-b-2 border-sky-300">
        {chats.map((chat) => (
          <Link key={chat.id} chat={chat} />
        ))}
      </div>
      <div className="border-b-2 border-sky-300 p-2">
        <input
          className="w-11/12 py-2 bg-zinc-800 text-gray-700 border rounded border-white"
          type="text"
          placeholder=" chat search"
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
    </nav>
  );
}

export default LeftNav;