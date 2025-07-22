import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white shadow-xl rounded-xl p-10 text-center">
        <h1 className="text-3xl font-bold text-blue-600">NormaPy</h1>
        <p className="mt-2 text-gray-500">
          Sistema inteligente de importación y normalización de productos
        </p>
        <Link
          to="/importar"
          className="inline-block mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Comenzar
        </Link>
      </div>
    </div>
  );
} 