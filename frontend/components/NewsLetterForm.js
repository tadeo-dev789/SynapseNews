'use client';
import { useState } from 'react';
import axios from 'axios';
import { Mail, Loader2, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';

export default function NewsLetterForm() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleSubscribe = async (e) => {
    e.preventDefault();
    
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if (!email || !emailRegex.test(email)) {
      setStatus('error');
      setMessage('Ese correo no parece real. Revisa el formato.');
      return;
    }

    setStatus('loading');
    setMessage('');

    try {
      const response = await axios.post(`${API_URL}/api/subscribe`, { 
        email: email 
      });

      setStatus('success');
      setMessage(response.data.mensaje); 
      setEmail('');

      setTimeout(() => {
        setStatus('idle');
        setMessage('');
      }, 5000);

    } catch (error) {
      setStatus('error');
      const errorMsg = error.response?.data?.detail || "Ocurrió un error al suscribirse.";
      setMessage(errorMsg);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubscribe} className="relative flex items-center">
        
        <div className="relative w-full">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
            <Mail size={18} />
          </div>
          <input
            type="email"
            className="block w-full p-4 pl-10 text-sm text-slate-900 border border-slate-300 rounded-lg bg-white focus:ring-indigo-500 focus:border-indigo-500 transition-all shadow-sm disabled:bg-slate-100 disabled:text-slate-400"
            placeholder="tu@correo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={status === 'loading' || status === 'success'}
            required
          />
        </div>

        <button
          type="submit"
          disabled={status === 'loading' || status === 'success'}
          className={`absolute right-2 top-2 bottom-2 px-4 py-1 text-white font-medium rounded-md text-sm transition-all flex items-center justify-center min-w-[100px]
            ${status === 'success' 
              ? 'bg-green-600 hover:bg-green-700' 
              : 'bg-indigo-600 hover:bg-indigo-700'
            } disabled:opacity-70 disabled:cursor-not-allowed`}
        >
          {status === 'loading' ? (
            <Loader2 size={18} className="animate-spin" />
          ) : status === 'success' ? (
            <>
              <CheckCircle size={18} className="mr-1" /> Listo
            </>
          ) : (
            <>
              Unirme <ArrowRight size={16} className="ml-1" />
            </>
          )}
        </button>
      </form>

      {message && (
        <div className={`mt-3 text-sm flex items-center justify-center animate-in fade-in slide-in-from-top-1
          ${status === 'error' ? 'text-red-400' : 'text-green-400'}`}
        >
          {status === 'error' ? <AlertCircle size={14} className="mr-2" /> : <CheckCircle size={14} className="mr-2" />}
          {message}
        </div>
      )}

      <p className="mt-4 text-xs text-slate-500">
        Sin spam. Date de baja cuando quieras.
      </p>
    </div>
  );
}