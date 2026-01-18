"use client";
import { useState } from "react";
import axios from "axios";
import { Ban, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function UnsubscribePage() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleUnsubscribe = async (e) => {
    e.preventDefault();
    setStatus("loading");

    try {
      const response = await axios.post(`${API_URL}/api/unsubscribe`, {
        email: email,
      });

      setStatus("success");
      setMessage(response.data.mensaje);
      setEmail("");
    } catch (error) {
      setStatus("error");
      const errorMsg =
        error.response?.data?.detail || "Error al procesar la solicitud.";
      setMessage(errorMsg);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">

      <Link
        href="/"
        className="absolute top-8 left-8 flex items-center text-gray-500 hover:text-black transition-colors"
      >
        <ArrowLeft size={20} className="mr-2" /> Volver a SynapseNews
      </Link>

      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 text-center border border-gray-100">
        <div className="mx-auto w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-6 text-red-500">
          <Ban size={32} />
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-2">Darse de baja</h1>
        <p className="text-gray-500 mb-8 text-sm leading-relaxed">
          Si te vas, dejarás de recibir el resumen diario de IA.
          <br />
          Puedes volver a suscribirte cuando quieras.
        </p>

        {status === "success" ? (
          <div className="bg-green-50 text-green-700 p-4 rounded-lg flex items-center justify-center animate-in zoom-in">
            <CheckCircle size={20} className="mr-2" />
            <span>{message}</span>
          </div>
        ) : (
          <form onSubmit={handleUnsubscribe} className="space-y-4">
            <div>
              <input
                type="email"
                required
                placeholder="Ingresa tu correo para confirmar"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder:text-gray-500 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={status === "loading"}
              />
            </div>

            <button
              type="submit"
              disabled={status === "loading"}
              className="w-full bg-black text-white font-bold py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {status === "loading"
                ? "Procesando..."
                : "Confirmar desuscripción"}
            </button>
          </form>
        )}

        {status === "error" && (
          <div className="mt-4 text-red-500 text-sm flex items-center justify-center">
            <AlertCircle size={16} className="mr-2" /> {message}
          </div>
        )}
      </div>
    </div>
  );
}
