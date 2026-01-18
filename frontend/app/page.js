import MarketTicker from "@/components/MarketTicker";
import HomeHero from "@/components/HomeHero";
import NewsGrid from "@/components/NewsGrid";
import NewsLetterForm from "@/components/NewsLetterForm";
import Link from "next/link";

export default async function Home() {

  async function getData() {
    try{
      const[marketRes,techRes,businessRes] = await Promise.all([
        fetch("http://localhost:8000/api/markets",{cache:"no-store"}),
        fetch("http://localhost:8000/api/news?category=tecnologia&limit=10",{cache:"no-store"}),
        fetch("http://localhost:8000/api/news?category=negocios&limit=10",{cache:"no-store"})
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

  const heroStory = businessNews.length > 0 ? businessNews[0] : null;

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
          <div className="text-xs font-mono bg-gray-100 px-2 py-1">{today}</div>
        </div>
      </header>

      <div className="mb-8">
        <MarketTicker data={data.markets} />
      </div>

      <section className="mb-12">
        <HomeHero news={heroStory} />
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <NewsGrid title="Tecnología" news={techNews} />

        <NewsGrid title="Negocios" news={businessNews} />
      </div>

      <footer className="mt-16 border-t border-gray-300 pt-8 text-center">
        <h3 className="font-bold mb-4 uppercase tracking-widest text-sm text-gray-500">
          Únete a nuestro Newsletter
        </h3>
        <NewsLetterForm />
        <div className="mt-4">
          <Link
            href="/unsubscribe"
            className="text-[10px] text-gray-400 hover:underline"
          >
            ¿Quieres darte de baja? Haz clic aquí.
          </Link>
        </div>
      </footer>
    </main>
  );
}