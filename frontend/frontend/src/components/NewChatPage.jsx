import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth.jsx';
import FormInput from "./FormInput";
import Button from "./Button";

function CreateNewChat({ newChatName }) {
    const { token } = useAuth();
    const navigate = useNavigate(); // Use useNavigate hook to get the navigate function

    const createNewChat = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats?chat_name=${newChatName}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });
            if (!response.ok) {
                throw new Error("Failed to create new chat.");
            }
            else {
                console.log("New chat created successfully.");
                const data = await response.json();
                navigate(`/chats/${data.chat.id}/details`); // Redirect to the chat details page
            }
        }
        catch (error) {
            console.error("Error creating new chat: ", error);
        }
    }

    return (
        <div>
            <Button className="ml-3" type="button" onClick={createNewChat}>create</Button>
        </div>
    );
}

function NewChatPage() {
    const [newChatName, setNewChatName] = useState("");

    const handleNameChange = (event) => {
        setNewChatName(event.target.value);
    };

    return (
        <div className="flex flex-col justify-evenly items-center p-2">
            <p className="mb-2">create a new chat</p>
            <div className="flex flex-col justify-evenly p-2 border-2 rounded border-white-900">
                <p className="text-green-300">chat name</p>
                <div className="flex flex-row justify-between items-center">
                    <FormInput className="ml-4" placeholder="new chat name" onChange={handleNameChange} />
                    <CreateNewChat newChatName={newChatName} />
                </div>
            </div>
        </div>
    );
}

export default NewChatPage;