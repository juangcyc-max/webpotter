// emoji-data.js - Emojis PNG de Harry Potter (exactamente como los tienes)
window.EMOJIS_MAGICOS = [
  // 🐉 CRIATURAS MÁGICAS
  { 
    emoji: '<img src="/static/emojis/dragon.png" alt="🐉" class="inline-emoji">', 
    name: 'dragon', 
    code: ':dragon:', 
    category: 'criaturas' 
  },
  { 
    emoji: '<img src="/static/emojis/lechuza.png" alt="🦉" class="inline-emoji">', 
    name: 'lechuza', 
    code: ':lechuza:', 
    category: 'criaturas' 
  },
  { 
    emoji: '<img src="/static/emojis/nagini.png" alt="🐍" class="inline-emoji">', 
    name: 'nagini', 
    code: ':nagini:', 
    category: 'criaturas' 
  },
  { 
    emoji: '<img src="/static/emojis/hipogrifo.png" alt="🦜" class="inline-emoji">', 
    name: 'hipogrifo', 
    code: ':hipogrifo:', 
    category: 'criaturas' 
  },
  
  // 🐈 ANIMALES Y MASCOTAS
  { 
    emoji: '<img src="/static/emojis/gato.png" alt="🐱" class="inline-emoji">', 
    name: 'gato', 
    code: ':gato:', 
    category: 'animales' 
  },
  { 
    emoji: '<img src="/static/emojis/perro.png" alt="🐶" class="inline-emoji">', 
    name: 'perro', 
    code: ':perro:', 
    category: 'animales' 
  },
  
  // 👤 PERSONAJES
  { 
    emoji: '<img src="/static/emojis/harry.png" alt="🧙‍♂️" class="inline-emoji">', 
    name: 'harry', 
    code: ':harry:', 
    category: 'personajes' 
  },
  { 
    emoji: '<img src="/static/emojis/hermione.png" alt="👩‍🎓" class="inline-emoji">', 
    name: 'hermione', 
    code: ':hermione:', 
    category: 'personajes' 
  },
  { 
    emoji: '<img src="/static/emojis/dumbledore.png" alt="🧙‍♂️" class="inline-emoji">', 
    name: 'dumbledore', 
    code: ':dumbledore:', 
    category: 'personajes' 
  },
  { 
    emoji: '<img src="/static/emojis/ron.png" alt="🧑‍🦰" class="inline-emoji">', 
    name: 'ron', 
    code: ':ron:', 
    category: 'personajes' 
  }
];

// Función para obtener emojis por categoría
window.getEmojisByCategory = function(category) {
  return window.EMOJIS_MAGICOS.filter(e => e.category === category);
};

// Función para convertir códigos a imágenes
window.convertCodesToImages = function(text) {
  let result = text;
  window.EMOJIS_MAGICOS.forEach(emoji => {
    const escapedCode = emoji.code.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const regex = new RegExp(escapedCode, 'g');
    result = result.replace(regex, emoji.emoji);
  });
  return result;
};