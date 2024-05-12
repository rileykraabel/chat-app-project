import { useState } from "react";
import { useAuth } from "../context/auth";
import { useUser } from "../context/user";
import Button from "./Button";

function Profile() {
    const { logout } = useAuth();
    const user = useUser();

    if (!user) {
        return <div>Loading...</div>;
    }

    return (
        <div className="max-w-96 mx-auto px-4 py-8">
            <div className="border-2 border-gray-400 rounded-lg">
                <div className="flex flex-col">
                    <div className="border-b-2 border-gray-400 px-4 py-2 flex items-center">
                        <h2 className="text-2xl font-bold">details</h2>
                    </div>
                    <div className="border-b-2 border-gray-400 px-4 py-2 flex justify-between">
                        <span className="text-gray-500">username:</span>
                        <span className="text-white ml-4">{user.username}</span>
                    </div>
                    <div className="border-b-2 border-gray-400 px-4 py-2 flex justify-between">
                        <span className="text-gray-500">email:</span>
                        <span className="text-white ml-4">{user.email}</span>
                    </div>
                    <div className="px-4 py-2 flex justify-between">
                        <span className="text-gray-500">member since:</span>
                        <span className="text-white ml-4">{new Date(user.created_at).toDateString()}</span>
                    </div>
                </div>
            </div>
            <div className="mt-4">
                <Button className="border-2 border-gray-400 rounded-lg" onClick={logout}>
                    logout
                </Button>
            </div>
        </div>
    );
}

export default Profile;