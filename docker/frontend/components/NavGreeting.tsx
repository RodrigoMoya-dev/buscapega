"use client";

import { useEffect, useState } from "react";
import { getSettings } from "@/lib/api";

export default function NavGreeting() {
  const [name, setName] = useState<string | null>(null);

  useEffect(() => {
    getSettings().then((s) => {
      if (s?.user_name) setName(s.user_name);
    });
  }, []);

  if (!name) return null;

  return (
    <span className="text-sm text-gray-400">
      Hola, <span className="text-white font-medium">{name}</span>
    </span>
  );
}
