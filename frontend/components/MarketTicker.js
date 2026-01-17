"use client"; 

export default function MarketTicker({ data }) {
  if (!data) return <div className="h-10 bg-black"></div>;

  const stocks = data.acciones || [];
  const cryptos = data.cripto || [];

  if (stocks.length === 0 && cryptos.length === 0) return null;

  return (
    <div className="w-full bg-black text-white overflow-hidden h-10 flex items-center border-b border-gray-800 relative font-mono text-xs">
      
      <div className="bg-slate-800 text-slate-200 px-3 h-full flex items-center font-bold uppercase tracking-widest z-10 absolute left-0 border-r border-slate-700">
        MERCADOS
      </div>
      
      <div className="animate-marquee whitespace-nowrap flex items-center pl-32">
        
        {[1, 2].map((i) => (
            <div key={`run-${i}`} className="flex items-center">
                
                {stocks.length > 0 && (
                    <div className="flex items-center px-4 bg-blue-900/50 h-6 mx-2 rounded text-blue-200 font-bold tracking-wider">
                        NYSE/NASDAQ
                    </div>
                )}
                
                {stocks.map((item, idx) => (
                    <div key={`stock-${i}-${idx}`} className="flex items-center gap-2 mx-4 border-r border-gray-800 pr-4 last:border-0">
                        <span className="font-bold text-blue-400">{item.symbol}</span>
                        <span>${item.price?.toLocaleString()}</span>
                        <span className={item.change_24h >= 0 ? "text-green-400" : "text-red-400"}>
                            {item.change_24h > 0 ? "▲" : "▼"} {Math.abs(item.change_24h).toFixed(2)}%
                        </span>
                    </div>
                ))}

                {cryptos.length > 0 && (
                    <div className="flex items-center px-4 bg-yellow-900/50 h-6 mx-2 rounded text-yellow-200 font-bold tracking-wider ml-8">
                        CRYPTO
                    </div>
                )}

                {cryptos.map((item, idx) => (
                    <div key={`crypto-${i}-${idx}`} className="flex items-center gap-2 mx-4 border-r border-gray-800 pr-4 last:border-0">
                        <span className="font-bold text-yellow-500">{item.symbol}</span>
                        <span>${item.price?.toLocaleString()}</span>
                        <span className={item.change_24h >= 0 ? "text-green-400" : "text-red-400"}>
                            {item.change_24h > 0 ? "▲" : "▼"} {Math.abs(item.change_24h).toFixed(2)}%
                        </span>
                    </div>
                ))}
            </div>
        ))}

      </div>
    </div>
  );
}