import { useQuery } from "react-query";
import { useState, useEffect } from "react";
import { NavLink, useParams } from "react-router-dom";
import { useAuth } from "../context/auth.jsx";
import Button from './Button.jsx';
import NewChat from './NewChat';

function HandleDeleteMessage({ messageId }) {
    const { token } = useAuth();
    const { chatId } = useParams();

    const handleDeleteMessage = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/messages/${messageId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error("Failed to delete message.");
            } else {
                console.log("Message deleted successfully.");
            }
        } catch (error) {
            console.error("Error deleting message: ", error);
        }
    }

    return (
        <Button onClick={handleDeleteMessage} className="border-slate-500 text-slate-500 ml-2">X</Button>
    );
}

function EditMessageForm({ messageId, originalText, onSave, onCancel }) {
    const [editedText, setEditedText] = useState(originalText);

    const handleSave = () => {
        onSave(messageId, editedText);
    };

    const handleCancel = () => {
        onCancel();
    };

    const handleInputChange = (e) => {
        setEditedText(e.target.value);
    };

    return (
        <div className="flex flex-row justify-between items-center">
            <input type="text" className="border rounded bg-transparent px-2 py-2 mx-2 flex-1"
                value={editedText} onChange={handleInputChange} placeholder="new message"/>
            <div className="flex flex-row flex-none">
                <Button onClick={handleSave} className="border-slate-500 text-slate-500">save</Button>
                <Button onClick={handleCancel} className="border-slate-500 text-slate-500 ml-2">cancel</Button>
            </div>
        </div>
    );
}

function MessageRow({ message, author }) {
    const created_at_date = new Date(message.created_at)
    const createdDateString = created_at_date.toDateString()
    const createdTimeString = created_at_date.toLocaleTimeString()
    const isCurrentUserMessage = message.user.id === author.id;

    const { token } = useAuth();
    const { chatId } = useParams();
    const [isEditing, setIsEditing] = useState(false);

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleCancelEdit = () => {
        setIsEditing(false);
    };

    const handleSaveEdit = (editedMessageId, editedText) => {
        const handleEditMessage = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/messages/${messageId}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    throw new Error("Failed to update message.");
                } else {
                    console.log("Message updated successfully.");
                }
            } catch (error) {
                console.error("Error updating message: ", error);
            }
        }

        console.log(`Message with ID ${editedMessageId} edited to: ${editedText}`);
        setIsEditing(false);
    };

    return (
        <div className="flex flex-row">
            {isEditing ? (
                <>
                    <div className="flex flex-col w-full">
                        <div className="flex flex-row items-center justify-between p-2">
                            <div className="font-bold text-sm text-center text-green-300">{message.user.username}</div>
                            <div className="font-mono text-xs text-slate-500">{createdDateString} - {createdTimeString}</div>
                        </div>
                        <EditMessageForm
                            messageId={message.id}
                            originalText=""
                            onSave={handleSaveEdit}
                            onCancel={handleCancelEdit}
                        />
                    </div>
                </>
            ) : (
                <>
                    <div className="flex flex-col flex-1 pb-3">
                        <div className="flex flex-row items-center justify-between p-2 w-full">
                            <div className="font-bold text-sm text-center text-green-300">{message.user.username}</div>
                            <div className="font-mono text-xs text-slate-500">{createdDateString} - {createdTimeString}</div>
                        </div>
                        <div className="text-white text-left px-3">{message.text}</div>
                    </div>

                    {isCurrentUserMessage && (
                        <div className="flex flex-row flex-none items-center">
                            <Button onClick={handleEdit} className="border-slate-500 ml-5 text-slate-500">edit</Button>
                            <HandleDeleteMessage messageId={message.id} />
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

function NoChat() {
    return (
        <div className="font-bold text-2xl py-4 text-center">
            no messages have been sent yet
        </div>
    );
}

function ChatCard({ chat, author }) {
    const { token } = useAuth();
    const { data } = useQuery({
        queryKey: ["messages", chat.id],
        queryFn: () => (
            fetch(`http://127.0.0.1:8000/chats/${chat.id}/messages`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
                .then((response) => response.json())
        ),
        enabled: chat !== undefined,
    });

    const cardClassName = [
        "bg-lgrn text-black"
    ].join(" ");

    const messageClassName = [
        "bg-zinc-800",
        "border-1 border-orange-500 rounded-xl",
        "shadow-sm shadow-orange-500",
        "px-2 m-2"
    ].join(" ")

    if (data?.messages) {
        return (
            <div className="flex flex-col">
                <div className="flex flex-col px-2 bg-fuchsia-900 border-2 border-sky-300">
                    <div className={cardClassName}>
                        {data?.messages.length > 0 ? (
                            data?.messages.map((message) => (
                                <div key={message.id} className={messageClassName}>
                                    <MessageRow key={message.id} message={message} author={author}/>
                                </div>
                            ))
                        ) : (
                            <NoChat />
                        )}
                    </div>
                </div>
                <div>
                    <NewChat />
                </div>
            </div>
        );
    }

    return <NoChat />;
}

function ChatCardQueryContainer({ chatId, author }) {
    const { token } = useAuth();
    const { data } = useQuery({
        queryKey: ["chats", chatId],
        queryFn: () => (
            fetch(`http://127.0.0.1:8000/chats/${chatId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
                .then((response) => response.json())
        ),
        enabled: chatId !== undefined,
    });

    if (data?.chat) {
        return <ChatCard chat={data.chat} author={author}/>
    }

    return <NoChat />;
}

function Chat() {
    const { token } = useAuth();
    const { chatId } = useParams();
    const [ currentUser, setCurrentUser ] = useState(null);

    useEffect(() => {
        const fetchCurrentUser = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/users/me`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch the current user.");
                }

                const userData = await response.json();
                setCurrentUser(userData.user);
            }
            catch (error) {
                console.error("Error fetching current user: ", error);
            }
        };

        fetchCurrentUser();
    }, [token]);

    if (chatId) {
        const url = `/chats/${chatId}/details`
        return (
            <div>
                <div className="flex justify-center items-center p-2 border-x-2 border-sky-300">
                    <NavLink to={url} className="text-green-300 border-2 rounded border-orange-500 m-3 p-2">
                        chat details
                    </NavLink>
                </div>
                <ChatCardQueryContainer chatId={chatId} author={currentUser}/>
            </div>
        );
    }

    return (
        <div className="text-center text-2xl text-white font-bold py-4">
            select a chat
        </div>
    );
}

export default Chat;