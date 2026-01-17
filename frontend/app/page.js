import MarketTicker from "@/components/MarketTicker";

export default async function Home() {

  async function getData() {
    try{
      const[marketRes,businessRes,techRes] = await Promise.all([
        fetch("http://localhost:8000/api/markets",{cache:"no-store"}),
        fetch("http://localhost:8000/api/news?category=tecnologia&limit=4",{cache:"no-store"}),
        fetch("http://localhost:8000/api/news?category=negocios&limit=4",{cache:"no-store"})
      ]);

      return {
        markets: await marketRes.json(),
        tech: await techRes.json(),
        business: await businessRes.json()
      };

    }catch(error){
      console.error("Error conectando al backend:", error);
      return { markets: {}, tech: {}, business: {} };
    }
  }

  const data = await getData();

  const techNews = data.tech?.data || [];
  const businessNews = data.business?.data || [];
  const marketCount = (data.markets?.acciones?.length || 0) + (data.markets?.cripto?.length || 0);

  const today = new Date().toLocaleDateString('es-MX', { 
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
  });

  return (
    <main className="min-h-screen p-6 font-sans text-black bg-white">
      
      <header className="flex flex-col md:flex-row justify-between items-end mb-8 border-b-2 border-black pb-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter">SynapseNews</h1>
          <p className="text-sm text-gray-600">Hackathon Edition</p>
        </div>
        <div className="text-right">
          <div className="text-xs font-mono bg-gray-100 px-2 py-1">
            {today}
          </div>
        </div>
      </header>
  
      <div className="mb-8">
         <MarketTicker data={data.markets} />
      </div>

      <section className="mb-12">
        <div className="border border-gray-300 h-64 bg-gray-50 flex flex-col items-center justify-center text-gray-400">
          <span className="font-bold text-lg text-black mb-2">HERO SECTION</span>
          <p>Aquí se renderizará la noticia principal</p>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        <div className="border-t border-black pt-4">
          <h2 className="text-xl font-bold mb-4 uppercase">Tecnología</h2>
   
          <div className="space-y-4">

            <div className="border border-gray-200 p-4 bg-gray-50">
              <div className="h-4 bg-gray-300 w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 w-full"></div>
            </div>

            <div className="border border-gray-200 p-4 bg-gray-50">
              <div className="h-4 bg-gray-300 w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 w-full"></div>
            </div>
          </div>
        </div>

        <div className="border-t border-black pt-4">
          <h2 className="text-xl font-bold mb-4 uppercase">Negocios</h2>
          
          <div className="space-y-4">
             <div className="border border-gray-200 p-4 bg-gray-50">
              <div className="h-4 bg-gray-300 w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 w-full"></div>
            </div>

            <div className="border border-gray-200 p-4 bg-gray-50">
              <div className="h-4 bg-gray-300 w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 w-full"></div>
            </div>
          </div>
        </div>

      </div>

      <footer className="mt-16 border-t border-gray-300 pt-8 text-center">
        <h3 className="font-bold mb-4">Newsletter Module</h3>
        <div className="max-w-md mx-auto border border-dashed border-gray-400 p-6">
          [ Formulario de Suscripción ]
        </div>
      </footer>

    </main>
  );
}