import React, { useEffect, useState } from "react";

interface Producto {
  id: number;
  nombre: string;
  sku: string;
  precio: string;
  stock: number;
  marca: string;
}

export default function Dashboard() {
  const [productos, setProductos] = useState<Producto[]>([]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL}/api/productos/`)
      .then((res) => res.json())
      .then(setProductos)
      .catch((err) => console.error("Error:", err));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Productos Importados</h2>
      {productos.length ? (
        <ul className="space-y-2">
          {productos.map((p) => (
            <li key={p.id} className="bg-gray-100 p-4 rounded-lg">
              <strong>{p.nombre}</strong>
              <p>SKU: {p.sku} – Precio: ${p.precio} – Stock: {p.stock} – Marca: {p.marca}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500">No hay productos cargados.</p>
      )}
    </div>
  );
} 