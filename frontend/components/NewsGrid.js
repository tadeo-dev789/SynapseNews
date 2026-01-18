'use client';
import { useState } from 'react';
import { Calendar, ExternalLink, X } from 'lucide-react';

const THEMES = {
  tecnologia: {
    tag: "text-indigo-600 bg-indigo-50",
    titleHover: "group-hover:text-indigo-700",
    button: "text-indigo-600 bg-indigo-50 hover:bg-indigo-100",
    modalTag: "bg-indigo-600 text-white",
    prose: "prose-indigo"
  },
  negocios: {
    tag: "text-red-700 bg-red-50",
    titleHover: "group-hover:text-red-700",
    button: "text-red-700 bg-red-50 hover:bg-red-100",
    modalTag: "bg-red-700 text-white",
    prose: "prose-red"
  },
  default: {
    tag: "text-slate-600 bg-slate-100",
    titleHover: "group-hover:text-slate-800",
    button: "text-slate-600 bg-slate-100 hover:bg-slate-200",
    modalTag: "bg-slate-800 text-white",
    prose: "prose-slate"
  }
};

// Función auxiliar para detectar el tema según la categoría del JSON
const getThemeByCategory = (catName) => {
  if (!catName) return THEMES.default;
  const lower = catName.toLowerCase().trim();
  
  if (lower === 'negocios') {
    return THEMES.negocios;
  }
  if (lower === 'tecnologia') {
    return THEMES.tecnologia;
  }
  return THEMES.default;
};

export default function NewsGrid({ title, news }) {
  const [selectedNews, setSelectedNews] = useState(null);

  if (!news || news.length === 0) {
    return (
      <div className="border-t border-black pt-4">
        <h2 className="text-xl font-bold mb-4 uppercase">{title}</h2>
        <p className="text-gray-500 text-sm">No hay noticias disponibles.</p>
      </div>
    );
  }

  const modalStyle = selectedNews ? getThemeByCategory(selectedNews.category) : THEMES.default;

  return (
    <>
      <div className="border-t border-black pt-4">
        <h2 className="text-xl font-bold mb-6 uppercase flex items-center justify-between">
          {title}
          <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
            {news.length} ITEMS
          </span>
        </h2>
        
        <div className="grid grid-cols-1 gap-8">
          {news.map((item) => {
            const style = getThemeByCategory(item.category);

            return (
              <article key={item.id} className="group border-b border-gray-100 pb-6 last:border-0 flex flex-col">
                <span className={`text-[10px] font-bold uppercase tracking-widest mb-1 block w-fit px-1 rounded ${style.tag}`}>
                  {item.category}
                </span>

                <h3 className={`text-lg font-bold leading-tight mb-2 transition-colors cursor-pointer ${style.titleHover}`}
                    onClick={() => setSelectedNews(item)}>
                  {item.original_title}
                </h3>

                <div 
                  className="text-sm text-gray-600 leading-relaxed mb-3 line-clamp-3 cursor-pointer hover:text-gray-900 transition-colors"
                  onClick={() => setSelectedNews(item)}
                  title="Clic para leer análisis completo"
                >
                  {item.ai_summary || "Procesando resumen inteligente..."}
                </div>

                <div className="flex items-center text-xs text-gray-400 font-mono mt-auto pt-2">
                  <Calendar size={12} className="mr-1" />
                  <span className="mr-4">
                    {new Date(item.created_at).toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })}
                  </span>
                  
                  <button 
                    onClick={() => setSelectedNews(item)}
                    className={`flex items-center font-bold ml-auto px-2 py-1 rounded transition-colors ${style.button}`}
                  >
                    VER ANÁLISIS IA
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </div>

      {selectedNews && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl shadow-2xl flex flex-col animate-in zoom-in-95 duration-200">
            
            <div className="sticky top-0 bg-white border-b border-gray-100 p-6 flex justify-between items-start z-10">
              <div>
                <span className={`inline-block px-2 py-1 mb-2 text-xs font-bold tracking-widest rounded uppercase ${modalStyle.modalTag}`}>
                  {selectedNews.category}
                </span>
                <h3 className="text-2xl font-black leading-tight text-gray-900">
                  {selectedNews.original_title}
                </h3>
              </div>
              <button 
                onClick={() => setSelectedNews(null)}
                className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            <div className="p-8">
              <div className={`prose max-w-none ${modalStyle.prose}`}>
                <h4 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">
                  Análisis de Synapse AI
                </h4>
                <p className="text-lg text-gray-700 leading-relaxed whitespace-pre-wrap font-serif">
                  {selectedNews.ai_summary}
                </p>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-100 bg-gray-50 -mx-8 -mb-8 p-6 flex justify-between items-center">
                <div className="text-xs text-gray-500 font-mono">
                  Procesado: {new Date(selectedNews.created_at).toLocaleString()}
                </div>
                <a 
                  href={selectedNews.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center px-4 py-2 bg-black text-white text-sm font-bold rounded-lg hover:bg-gray-800 transition-colors"
                >
                  Leer Noticia Original <ExternalLink size={16} className="ml-2" />
                </a>
              </div>
            </div>
          </div>
          <div className="absolute inset-0 -z-10" onClick={() => setSelectedNews(null)}></div>
        </div>
      )}
    </>
  );
}