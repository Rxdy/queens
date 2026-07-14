// Hash déterministe d'une chaîne en entier 32 bits (cyrb53 tronqué), même
// résultat sur tout navigateur pour une même chaîne.
export const hashStringToInt = (str) => {
  let h1 = 0xdeadbeef;
  let h2 = 0x41c6ce57;
  for (let i = 0; i < str.length; i++) {
    const ch = str.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  return h1 >>> 0;
};

// PRNG déterministe (mulberry32) : même contrat que Math.random (float dans [0, 1)),
// utilisable comme remplacement direct partout où Math.random() est attendu.
export const mulberry32 = (seed) => {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

// Construit un générateur pseudo-aléatoire déterministe à partir d'une chaîne de seed.
export const createSeededRng = (seedString) => mulberry32(hashStringToInt(seedString));
