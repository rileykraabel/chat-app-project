import { QueryClient, QueryClientProvider } from 'react-query';
import { Link, BrowserRouter, Navigate, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from "./context/auth";
import { UserProvider } from "./context/user";

import Chats from './components/Chats.jsx';
import Details from './components/Details.jsx';
import Login from './components/Login.jsx';
import NewChatPage from './components/NewChatPage.jsx';
import Profile from './components/Profile.jsx';
import Registration from './components/Registration.jsx';
import TopNav from './components/TopNav.jsx';

const queryClient = new QueryClient();

function NotFound() {
  return <h1>404: Not Found</h1>;
}

function Home() {
  const { isLoggedIn, logout } = useAuth();
  return (
    <div className="max-w-4/5 mx-auto text-center px-4 py-8">
      <div className="py-2">
        {isLoggedIn ?
          (<span>currently logged in as: {isLoggedIn.toString()}</span>) :
          (<div className="flex flex-col px-4 py-4 items-center">
            <span className="mb-4">
              welcome to pony express!<br />
              this is a chat application for cs4550 (university of utah sp2024).<br />
            </span>
            <div className="flex flex-row">
            <button className="bg-gray-500 text-white px-4 py-2 rounded">
              <Link to="/login">get started</Link>
            </button>
            </div>
          </div>)
        }
      </div>
    </div>
  );
}

function Header() {
  return (
    <header>
      <TopNav />
    </header>
  );
}

function AuthenticatedRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Chats />} />
      <Route path="/chats" element={<Chats />} />
      <Route path="/chats/:chatId" element={<Chats />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/error/404" element={<NotFound />} />
      <Route path="/chats/:chatId/details" element={<Details />} />
      <Route path="/chats/new" element={<NewChatPage />} />
      <Route path="*" element={<Navigate to="/error/404" />} />
    </Routes>
  );
}

function UnauthenticatedRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Registration />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

function Main() {
  const { isLoggedIn } = useAuth();
  return (
    <main className="h-full max-h-full">
      {isLoggedIn ?
        <AuthenticatedRoutes /> :
        <UnauthenticatedRoutes />
      }
    </main>
  );
}

function App() {
  const className = [
    "h-screen max-h-screen",
    "max-w-screen mx-auto",
    "bg-zinc-800 text-white",
    "flex flex-col",
  ].join(" ");

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <UserProvider>
            <div className={className}>
              <Header />
              <Main />
            </div>
          </UserProvider>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;