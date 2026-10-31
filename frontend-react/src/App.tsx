import React from 'react';
import {BrowserRouter,Routes,Route,Navigate,Outlet,useLocation} from 'react-router-dom';
import {AppProvider,useApp} from './context/AppContext';
import {ToastContainer} from './components/ToastContainer';
import {ConfirmModal} from './components/ConfirmModal';
import {Login} from './pages/Login';
import {StudentLayout} from './layouts/StudentLayout';
import {FacultyLayout} from './layouts/FacultyLayout';
import {HODLayout} from './layouts/HODLayout';
import {AdminLayout} from './layouts/AdminLayout';
import {LivePage} from './pages/LivePages';
function ScrollReset(){const location=useLocation();React.useLayoutEffect(()=>{window.scrollTo({top:0,left:0,behavior:'instant'})},[location.pathname]);return null}
function Gate({role}:{role:string}){const {currentUser,loading}=useApp();if(loading)return <div className="p-16 text-center">Connecting to your workspace…</div>;if(!currentUser)return <Navigate to="/login" replace/>;if(currentUser.role!==role)return <Navigate to={'/'+currentUser.role} replace/>;return <Outlet/>}
function Registration(){return <div className="max-w-lg mx-auto mt-24 p-8 bg-white rounded-xl border border-slate-200"><h1 className="text-2xl font-bold mb-4">Your administrator creates your account</h1><p className="text-slate-600 mb-6">Student and staff accounts are managed in User Management and mapped to their department, section and subjects. Role privileges cannot be selected through public registration.</p><a href="/app/login" className="text-blue-600 font-semibold">Back to sign in →</a></div>}
export default function App(){return <AppProvider><BrowserRouter basename="/app"><ScrollReset/><Routes><Route path="/" element={<Navigate to="/login" replace/>}/><Route path="login" element={<Login/>}/><Route path="register" element={<Registration/>}/>{[['student',StudentLayout],['faculty',FacultyLayout],['hod',HODLayout],['admin',AdminLayout]].map(([role,Layout]:any)=><Route key={role} element={<Gate role={role}/>}><Route path={role} element={<Layout/>}><Route index element={<LivePage/>}/><Route path="*" element={<LivePage/>}/></Route></Route>)}<Route path="*" element={<Navigate to="/login" replace/>}/></Routes><ToastContainer/><ConfirmModal/></BrowserRouter></AppProvider>}
