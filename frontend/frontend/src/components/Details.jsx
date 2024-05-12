import React, { useState, useEffect } from 'react';
import { NavLink, useParams } from 'react-router-dom';
import { useQuery } from "react-query";
import { useAuth } from "../context/auth.jsx";

import Button from './Button';
import FormInput from './FormInput';

//  --------------------
//  |    ui elements   |
//  --------------------

// this method renders the link to the new chat page //
function NewChatElement() {
    return (
        <div className="flex justify-center px-2 mt-2">
            <NavLink to="/chats/new" className="text-fuchsia-500">
                <Button>create a new chat</Button>
            </NavLink>
        </div>
    );
}

// this method renders the UI element where there are no users of a chat [not expected to be used] //
function NoUser() {
    return (
        <div className="font-bold text-2xl py-4 text-center">
            there are no users for the chat
        </div>
    );
}

// this method renders the UI element that represents the list of the chat users //
function ChatUsers({ chatId, chatDetails, owner }) {
    if (chatId) {
        return (
            <div>
                <p className="text-orange-500">chat users</p>
                <FetchUsers chatId={chatId} chatDetails={chatDetails} owner={owner}/>
            </div>
        );
    }
}

// this method renders the owner row for the list of users //
function OwnerRow({ user }) {
    return (
        <div className="flex flex-row justify-between items-center">
            <p className="pl-4">{user.username}</p>
            <Button className="h-full ml-2" type="submit" disabled={true}>owner</Button>
        </div>
    );
}

// ----------------------
// |    fetch methods   |
// ----------------------

// this form input method handles updating the chat's name //
function ChatName({ chatId, owner }) {
    const { token } = useAuth();
    const [newChatName, setNewChatName] = useState("");

    const handleUpdateChatName = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}?new_name=${encodeURIComponent(newChatName)}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name: newChatName })
            });

            if (!response.ok) {
                throw new Error('Failed to update chat name.');
            }
            else {
                console.log('Chat name updated successfully.');
                setNewChatName("");
            }
        } 
        catch (error) {
            console.error('Error updating chat name:', error);
        }
    }

    const handleInputChange = (e) => {
        setNewChatName(e.target.value);
    };

    return (
        <div className="border-2 rounded border-white-900 p-3 ">
            <p className="text-green-300">edit chat name</p>
            <div className="flex flex-row justify-between items-center">
                <FormInput type="chatname" value={newChatName} onChange={handleInputChange} placeholder="update chat name" />
                <Button className="h-full ml-2" type="button" onClick={handleUpdateChatName} disabled={!owner}>update</Button>
            </div>
        </div>
    );
}

// this method handles the fetch call to the database to remove a use from the current chat's list of users //
function RemoveUser({ user, chatDetails, owner }) {
    const { token } = useAuth();
    const { chatId } = useParams();
    const [users, setUsers] = useState([]);

    var disabled = true;
    if (owner) {
        disabled = false;
    }

    useEffect(() => {
        const fetchUsersInChat = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/users`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch users in the chat. ");
                }
                else {
                    const data = await response.json();
                    setUsers(data.users);
                }
            }
            catch (error) {
                  console.error("Error fetching users in the chat: ", error);  
            }
        };

        if (chatId) {
            fetchUsersInChat();
        }
    }, [chatId, token]);

    const handleRemoveUser = async (userId) => {
        try {
            console.log("Removing user with ID:", userId, "from chat with ID:", chatId);
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });
            if (!response.ok) {
                throw new Error("Failed to remove user from the chat.");
            }
            else {
                console.log("User removed successfully.");
                setUsers(users.filter(user => user.id !== userId));
            }
        }
        catch (error) {
            console.error("Error removing user from the chat: ", error);
        }
    }

    if (chatDetails?.chat?.owner?.id === user.id) {
        return (<OwnerRow user={user} />);
    }
    else {
        return (
            <div className="flex flex-row justify-between items-center">
                <p className="pl-4">{user.username}</p>
                <Button className="h-full ml-2" type="button" onClick={() => handleRemoveUser(user.id)} 
                    hidden={disabled} disabled={disabled}>remove</Button>
            </div>
        );
    }
}

// this method handles the fetch call to the database to add a new user to the current chat's list of users //
function AddUser({ chatId }) {
    const { token } = useAuth();
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(0);
    const [addUser, setAddUser] = useState(false);

    // Retrieve all users from the database //
    const { data: allUsersData } = useQuery("allUsers", async () => {
        const response = await fetch("http://127.0.0.1:8000/users", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.json();
    });

    // Retrieve all users in the current chat //
    const { data: chatUsersData } = useQuery(["chatUsers", chatId], async () => {
        const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/users`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.json();
    });

    // Filter out the users who are already in the chat; only display the ones not present //
    useEffect(() => {
        if (allUsersData && chatUsersData) {
            const filteredUsers = allUsersData.users.filter(user =>
                !chatUsersData.users.find(chatUser => chatUser.id === user.id)
            );
            setUsers(filteredUsers);
        }
    }, [allUsersData, chatUsersData]);

    // method to handle when the user changes //
    const handleUserChange = (e) => {
        const value = e.target.value;
        setSelectedUser(value);
        return value;
    };

    // Fetch method to add the selected user to the current chat //
    const handleAddUser = async (selectedUser) => {
        if (selectedUser) {
            try {
                setAddUser(true); // disable the add button while adding the user
                const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/users/${selectedUser}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                });
    
                if (!response.ok) {
                    throw new Error('Failed to add user to chat.');
                }
                else {
                    const data = await response.json();
                    console.log('User added successfully:', data);
    
                    setSelectedUser("");
                    setAddUser(false);
                }        
            } 
            catch (error) {
                console.error('Error adding user to chat:', error);
                setAddUser(false);
            }
        }
    };

    // handle updating the currently selected user //
    const handleAddUserClick = () => {
        handleAddUser(selectedUser);
    }

    return (
        <div className="flex flex-row justify-between items-center ml-3 mb-3">
            <select className="border-2 rounded border-white-900 bg-zinc-800 w-1/2" onChange={handleUserChange} value={selectedUser}>
                <option value="" disabled>add a user</option>
                {users.map(user => (
                    <option key={user.id} value={user.id}>{user.username}</option>
                ))}
            </select>
            <Button className="h-full" onClick={handleAddUserClick} disabled={addUser}>add</Button>
        </div>
    );
}

// this method fetches the list of users for the given chat id //
function FetchUsers({ chatId, chatDetails, owner }) {
    const { token } = useAuth(); 
    const { data } = useQuery({
        queryKey: ["users", chatId],
        queryFn: () => (
            fetch(`http://127.0.0.1:8000/chats/${chatId}/users`, {
                headers: {
                    Authorization: `Bearer ${token}`, 
                },
            })
                .then((response) => response.json())
        ),
        enabled: chatId !== undefined,
    });

    if (data?.users) {
        return (
            <div className="flex flex-col">
                <div className="flex flex-col">
                    <div className="">
                        {data?.users.length > 0 ? (
                            data?.users.map((user) => (
                                <div key={user.id} className="">
                                    <RemoveUser key={user.id} user={user} chatDetails={chatDetails} owner={owner}/>
                                </div>
                            ))
                        ) : (
                            <NoUser />
                        )}
                    </div>
                </div>
            </div>
        );
    }

    return <NoUser />;
}

// renders the page element for the current chat's details //
function Details() {
    const { token } = useAuth(); 
    const { chatId } = useParams();
    const [ currentUser, setCurrentUser ] = useState(null);
    const [ chatDetails, setChatDetails ] = useState(null);
    const [ currentUserIsOwner, setCurrentUserIsOwner ] = useState(false);

    // send fetch request to the server to retrieve the current user //
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

    // send fetch request to the server to retrieve the current chat's details //
    useEffect(() => {
        const fetchChatDetails = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}`, {
                    headers: {
                        Authorization: `Bearer ${token}`, 
                    },
                });

                const data = await response.json();
                setChatDetails(data);

                if (currentUser) {
                    setCurrentUserIsOwner(data.chat?.owner?.id === currentUser.id);
                }
            } 
            catch (error) {
                console.error("Error fetching chat details: ", error);
            }
        };

        if (chatId) {
            fetchChatDetails();
        }
    }, [chatId, token, currentUser]);

    // return the elements for the page structure //
    return (
        <div className="flex flex-col justify-evenly items-center p-2 w-screen">
            <div className="flex flex-col justify-evenly p-2">
                <div className="flex flex-row justify-between items-center">
                    <p className="pr-10">current chat: {chatDetails?.chat.name}</p>
                    <NavLink to={`/chats/${chatId}`}>
                        <Button>back to messages</Button>
                    </NavLink>
                </div>
                <ChatName chatId={chatId} owner={currentUserIsOwner}/>
                <div className="border-2 rounded border-white-900 p-3 mt-2 max-h-80 overflow-y-auto">
                    <ChatUsers chatId={chatId} chatDetails={chatDetails} owner={currentUserIsOwner}/>
                    {currentUserIsOwner && <AddUser chatId={chatId} enabled={currentUserIsOwner}/>}
                </div>
                <NewChatElement />
            </div>
        </div>
    );
}

export default Details;