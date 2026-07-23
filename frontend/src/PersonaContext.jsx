import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";

const PersonaContext = createContext(null);

export function PersonaProvider({ children }) {
  const [personas, setPersonas] = useState([]);
  const [personaId, setPersonaId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listPersonas()
      .then((list) => {
        setPersonas(list);
        if (list.length) setPersonaId(list[0].persona_id);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <PersonaContext.Provider value={{ personas, personaId, setPersonaId, loading, error }}>
      {children}
    </PersonaContext.Provider>
  );
}

export function usePersona() {
  const ctx = useContext(PersonaContext);
  if (!ctx) throw new Error("usePersona must be used within PersonaProvider");
  return ctx;
}
