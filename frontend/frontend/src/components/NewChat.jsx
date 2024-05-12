import { useState } from "react";
import { useMutation, useQueryClient } from "react-query";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/auth";
import Button from "./Button";

function Input(props) {
  return (
    <div className="flex flex-col w-full pr-2">
      <label className="text-s text-gray-400" htmlFor={props.text}>
        {props.text}
      </label>
      <input
        {...props}
        className="border rounded bg-transparent px-2 py-2"
      />
    </div>
  );
}

function NewChatForm() {
  const { chatId } = useParams();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [message, setMessage] = useState("");
  const mutation = useMutation({
    mutationFn: () => (
      fetch(
        `http://127.0.0.1:8000/chats/${chatId}/messages`,
        {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: message
          }),
        },
      ).then((response) => response.json())
    ),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["chats"],
      });
      navigate(`/chats/${data.message.chat_id}`);
    },
  });

  const onSubmit = (e) => {
    e.preventDefault();
    mutation.mutate();
  };

  return (
    <div>
      <form onSubmit={onSubmit} className="flex flex-row items-center justify-between">
        <Input
          name="message"
          type="text"
          placeholder="new message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <Button type="submit" className="bg-sky-300 text-white-800 hover:sky-400">send</Button>
      </form>
    </div>
  );
}

function NewChat() {
  return (
    <div className="w-100 border-2 border-t-0 border-sky-300 bg-zinc-800">
      <div className="px-4">
        <NewChatForm />
      </div>
    </div>
  );
}

export default NewChat;