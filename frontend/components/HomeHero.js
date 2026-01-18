"use client";
import { useState } from "react";

export default function HomeHero({ news }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!news) {
    return (
      <section className="w-full border-y-4 border-black py-12 px-6 bg-zinc-50 mb-12 animate-pulse">
        <div className="max-w-4xl mx-auto space-y-4 text-center">
           <div className="h-4 bg-gray-300 w-32 mx-auto rounded"></div>
           <div className="h-12 bg-gray-300 w-3/4 mx-auto rounded"></div>
        </div>
      </section>
    );
  }

  const rawText = news.ai_summary || "Análisis no disponible. Esperando procesamiento...";
  
  const paragraphs = rawText.split(/\n\n+/); 

  return (
    <section className="w-full border-y-2 border-black bg-white mb-12 transition-colors">
      <div className="max-w-5xl mx-auto py-12 px-6 text-center">
        
        <div className="mb-6 flex justify-center items-center gap-3">
          <span className="bg-red-700 text-white text-xs font-bold px-2 py-1 uppercase tracking-widest">
            Breaking News
          </span>
          <span className="text-xs font-mono text-gray-500 uppercase tracking-widest">
            {news.category || "Global Markets"}
          </span>
        </div>

        <h2 className="text-4xl md:text-6xl font-serif font-black text-slate-900 mb-8 leading-tight">
          {news.original_title}
        </h2>


        <div className="relative max-w-3xl mx-auto text-left">
          
          <div 
            className={`
              text-lg md:text-xl text-slate-800 font-serif leading-relaxed text-justify 
              transition-all duration-500 ease-in-out overflow-hidden
              ${isExpanded ? "max-h-[3000px]" : "max-h-48"} 
            `}
          >

            {paragraphs.map((paragraph, index) => (
              <p key={index} className="mb-6 last:mb-0">
                {paragraph}
              </p>
            ))}
          </div>


          {!isExpanded && (
            <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-white via-white/90 to-transparent pointer-events-none"></div>
          )}
        </div>

        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-6 border-2 border-black px-8 py-2 text-sm font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-all flex items-center gap-2 mx-auto"
        >
          {isExpanded ? "Colapsar Análisis" : "Leer Reporte Completo"} 
          <span>{isExpanded ? "▲" : "▼"}</span>
        </button>

      </div>
    </section>
  );
}