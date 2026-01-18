'use client';
import { useState } from 'react';
import axios from 'axios';

export default function DemoPage() {
  const [loading, setLoading] = useState(null);
  const [log, setLog] = useState('...');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const updateAllNews = async () => {
    setLoading('news');
    setLog('SCRAPING de Tecnología + Negocios...');
    try {
      await Promise.all([
        axios.post(`${API_URL}/api/update-news/tecnologia`),
        axios.post(`${API_URL}/api/update-news/negocios`)
      ]);
      setLog('NOTICIAS ACTUALIZADAS: Base de datos renovada.');
    } catch (error) {
      console.error(error);
      setLog('ERROR: Revisa la consola del backend.');
    } finally {
      setLoading(null);
    }
  };

  const simpleAction = async (id, url, name) => {
    setLoading(id);
    setLog(`Ejecutando ${name}...`);
    try {
      const res = await axios.post(`${API_URL}${url}`);
      setLog(`${name}: ${res.data.mensaje}`);
    } catch (error) {
      setLog('Error ejecutando acción.');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8 font-mono">
      
      <h1 className="text-2xl border-b-2 border-white pb-4 mb-8 uppercase text-yellow-400">
        Panel de Control (Demo)
      </h1>

      <div className="flex flex-col gap-6 max-w-xl">
        
        <button 
          onClick={updateAllNews}
          disabled={loading}
          className="p-6 bg-[#00ff00] text-black font-bold text-lg hover:bg-green-400 disabled:opacity-50 text-left"
        >
          {loading === 'news' ? '/// TRABAJANDO...' : '[1] ACTUALIZAR TODAS LAS NOTICIAS'}
        </button>

        <button 
          onClick={() => simpleAction('markets', '/api/update-markets/now', 'Mercados')}
          disabled={loading}
          className="p-4 bg-[#00ffff] text-black font-bold hover:bg-cyan-200 disabled:opacity-50 text-left"
        >
          {loading === 'markets' ? '...' : '[2] Forzar Mercados (Yahoo)'}
        </button>

        <button 
          onClick={() => simpleAction('newsletter', '/api/trigger-newsletter', 'Newsletter')}
          disabled={loading}
          className="p-4 bg-[#ff00ff] text-black font-bold hover:bg-pink-400 disabled:opacity-50 text-left"
        >
          {loading === 'newsletter' ? '...' : '[3] Enviar Newsletter'}
        </button>

      </div>

      <div className="mt-8 p-4 bg-[#222] border border-white text-green-400 min-h-[100px]">
        <strong>&gt; LOG DEL SISTEMA:</strong><br/>
        {log}
      </div>

    </div>
  );
}