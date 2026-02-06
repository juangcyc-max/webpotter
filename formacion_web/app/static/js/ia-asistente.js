// === IA NEXUS CORE - SISTEMA DE AYUDA INTELIGENTE ===
// Versión Mágica con Efectos Especiales
let nexusCargada = true;

function mostrarIA() {
    // Si ya existe el contenedor, no crear otro
    if (document.getElementById('nexus-container')) {
        document.getElementById('nexus-container').style.display = 'block';
        // Traer al frente
        document.getElementById('nexus-container').style.zIndex = '9999';
        return;
    }

    // Crear contenedor principal con efectos mágicos
    const container = document.createElement('div');
    container.id = 'nexus-container';
    container.style.cssText = `
        position: fixed;
        bottom: 120px;
        right: 40px;
        width: 380px;
        background: linear-gradient(135deg, rgba(10, 10, 15, 0.95), rgba(26, 26, 46, 0.98));
        border: 3px solid rgba(212, 175, 55, 0.4);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7),
                    0 0 30px rgba(174, 0, 1, 0.2),
                    0 0 50px rgba(34, 47, 91, 0.15);
        z-index: 9999;
        overflow: hidden;
        font-family: 'Work Sans', sans-serif;
        transform: scale(0.8);
        opacity: 0;
        animation: nexus-pop-in 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    `;

    // Efecto de brillo mágico alrededor
    const glowEffect = document.createElement('div');
    glowEffect.style.cssText = `
        position: absolute;
        inset: -5px;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.3) 0%, transparent 70%);
        border-radius: 25px;
        pointer-events: none;
        z-index: -1;
        animation: nexus-glow-pulse 3s ease-in-out infinite;
    `;
    container.appendChild(glowEffect);

    // Efecto de runas flotando
    const runesEffect = document.createElement('div');
    runesEffect.style.cssText = `
        position: absolute;
        inset: 0;
        pointer-events: none;
        overflow: hidden;
        z-index: -1;
    `;
    runesEffect.innerHTML = `
        <div class="nexus-rune rune-1">🔮</div>
        <div class="nexus-rune rune-2">✨</div>
        <div class="nexus-rune rune-3">⚡</div>
        <div class="nexus-rune rune-4">💫</div>
    `;
    container.appendChild(runesEffect);

    // Header de la IA con estilo mágico
    const header = document.createElement('div');
    header.style.cssText = `
        background: linear-gradient(135deg, #222f5b, #1a2345);
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 2px solid rgba(212, 175, 55, 0.3);
        position: relative;
        overflow: hidden;
    `;
    
    // Efecto de brillo en el header
    const headerGlow = document.createElement('div');
    headerGlow.style.cssText = `
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
        animation: nexus-header-glow 4s ease-in-out infinite;
        pointer-events: none;
    `;
    header.appendChild(headerGlow);

    header.innerHTML += `
        <div style="position: relative;">
            <div style="position: absolute; inset: 0; background: radial-gradient(circle, rgba(212, 175, 55, 0.4), transparent 70%); border-radius: 50%; animation: nexus-pulse-slow 3s ease-in-out infinite;"></div>
            <div style="position: relative; width: 36px; height: 36px; background: linear-gradient(135deg, #d4af37, #b8860b); border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid rgba(255, 255, 255, 0.3); box-shadow: 0 0 15px rgba(212, 175, 55, 0.6);">
                <span style="font-size: 18px;">🧠</span>
            </div>
        </div>
        <div style="flex: 1;">
            <h3 style="color: #f3e5ab; margin: 0; font-size: 16px; font-weight: bold; font-family: 'Cinzel', serif; letter-spacing: 1px;">NÚCLEO NEXUS</h3>
            <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #4ade80; animation: nexus-pulse 2s infinite;"></span>
                <span style="color: #a3a3a3; font-size: 11px; font-family: 'Work Sans', sans-serif;">Conectado • IA Activa</span>
            </div>
        </div>
        <div style="display: flex; gap: 8px;">
            <button id="nexus-minimize" style="
                background: rgba(212, 175, 55, 0.1);
                border: 1px solid rgba(212, 175, 55, 0.3);
                color: #d4af37;
                width: 28px;
                height: 28px;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                font-size: 16px;
            " title="Minimizar">
                <span>−</span>
            </button>
            <button id="nexus-close" style="
                background: rgba(174, 0, 1, 0.15);
                border: 1px solid rgba(174, 0, 1, 0.4);
                color: #ae0001;
                width: 28px;
                height: 28px;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                font-size: 18px;
                font-weight: bold;
            " title="Cerrar">
                <span>×</span>
            </button>
        </div>
    `;

    // Área de chat con efecto pergamino
    const chatArea = document.createElement('div');
    chatArea.id = 'nexus-chat';
    chatArea.style.cssText = `
        height: 280px;
        padding: 16px;
        overflow-y: auto;
        background: linear-gradient(135deg, rgba(34, 47, 91, 0.1), rgba(26, 26, 46, 0.3));
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(212, 175, 55, 0.1);
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
        font-family: 'Work Sans', sans-serif;
        position: relative;
    `;
    
    // Textura de pergamino sutil
    const parchmentTexture = document.createElement('div');
    parchmentTexture.style.cssText = `
        position: absolute;
        inset: 0;
        background-image: url('https://www.transparenttextures.com/patterns/parchment.png');
        opacity: 0.05;
        pointer-events: none;
    `;
    chatArea.appendChild(parchmentTexture);

    // Input de mensaje con estilo mágico
    const inputArea = document.createElement('div');
    inputArea.style.cssText = `
        padding: 16px;
        background: rgba(26, 26, 46, 0.8);
        border-top: 2px solid rgba(212, 175, 55, 0.2);
    `;
    
    const inputContainer = document.createElement('div');
    inputContainer.style.cssText = `
        display: flex;
        gap: 10px;
        align-items: center;
        background: rgba(46, 46, 76, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px;
        padding: 8px 12px;
        transition: all 0.3s ease;
    `;
    
    inputContainer.innerHTML = `
        <span style="color: #d4af37; font-size: 18px;">💬</span>
        <input type="text" id="nexus-input" 
               placeholder="Escribe tu pregunta..." 
               style="flex: 1; background: transparent; border: none; color: #f3e5ab; font-family: 'Work Sans', sans-serif; font-size: 14px; outline: none; padding: 4px 0;"
               autocomplete="off">
        <button id="nexus-send" style="
            background: linear-gradient(135deg, #ae0001, #8b0000);
            border: none;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(174, 0, 1, 0.3);
        " title="Enviar">
            <span style="font-size: 16px;">➤</span>
        </button>
    `;
    
    inputArea.appendChild(inputContainer);

    container.appendChild(header);
    container.appendChild(chatArea);
    container.appendChild(inputArea);
    document.body.appendChild(container);

    // Aplicar estilos CSS para animaciones
    aplicarEstilosNexus();

    // Eventos
    document.getElementById('nexus-close').onclick = () => {
        container.style.animation = 'nexus-pop-out 0.4s cubic-bezier(0.6, -0.28, 0.735, 0.045) forwards';
        setTimeout(() => {
            container.remove();
        }, 400);
    };

    document.getElementById('nexus-minimize').onclick = () => {
        if (container.style.height === '80px') {
            // Expandir
            container.style.height = '420px';
            chatArea.style.display = 'block';
            inputArea.style.display = 'block';
        } else {
            // Minimizar
            container.style.height = '80px';
            chatArea.style.display = 'none';
            inputArea.style.display = 'none';
        }
    };

    const inputField = document.getElementById('nexus-input');
    const sendButton = document.getElementById('nexus-send');

    sendButton.onclick = () => {
        const valor = inputField.value.trim();
        if (valor) {
            procesarPregunta(valor);
            inputField.value = '';
            // Efecto de envío
            sendButton.style.transform = 'scale(0.9)';
            setTimeout(() => {
                sendButton.style.transform = 'scale(1)';
            }, 200);
        }
    };

    inputField.onkeypress = (e) => {
        if (e.key === 'Enter') {
            const valor = e.target.value.trim();
            if (valor) {
                procesarPregunta(valor);
                e.target.value = '';
                // Efecto de envío
                sendButton.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    sendButton.style.transform = 'scale(1)';
                }, 200);
            }
        }
    };

    inputField.onfocus = () => {
        inputContainer.style.borderColor = '#d4af37';
        inputContainer.style.boxShadow = '0 0 15px rgba(212, 175, 55, 0.3)';
    };

    inputField.onblur = () => {
        inputContainer.style.borderColor = 'rgba(212, 175, 55, 0.2)';
        inputContainer.style.boxShadow = 'none';
    };

    // Mensaje de bienvenida con efecto
    setTimeout(() => {
        agregarMensaje("✨ ¡Saludos, joven aprendiz! 👋", "bot");
        setTimeout(() => {
            agregarMensaje("🧠 Soy Nexus Core, tu asistente de inteligencia artificial de GC ACADEMIA.", "bot");
        }, 500);
        setTimeout(() => {
            agregarMensaje("🔮 ¿En qué puedo ayudarte hoy? Puedo responder sobre cursos, funcionalidades o guiarte en tu aprendizaje.", "bot");
        }, 1000);
    }, 300);
}

function aplicarEstilosNexus() {
    // Crear estilo para animaciones
    const style = document.createElement('style');
    style.textContent = `
        @keyframes nexus-pop-in {
            0% {
                transform: scale(0.5) translateY(20px);
                opacity: 0;
                filter: blur(10px);
            }
            70% {
                transform: scale(1.05);
                opacity: 1;
                filter: blur(0);
            }
            100% {
                transform: scale(1);
                opacity: 1;
                filter: blur(0);
            }
        }
        
        @keyframes nexus-pop-out {
            0% {
                transform: scale(1);
                opacity: 1;
                filter: blur(0);
            }
            100% {
                transform: scale(0.3) translateY(20px);
                opacity: 0;
                filter: blur(5px);
            }
        }
        
        @keyframes nexus-glow-pulse {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1);
            }
            50% {
                opacity: 0.6;
                transform: scale(1.05);
            }
        }
        
        @keyframes nexus-header-glow {
            0%, 100% {
                opacity: 0;
                transform: translateX(-100%);
            }
            50% {
                opacity: 0.2;
                transform: translateX(100%);
            }
        }
        
        @keyframes nexus-pulse {
            0%, 100% {
                opacity: 0.7;
                box-shadow: 0 0 5px rgba(74, 222, 128, 0.5);
            }
            50% {
                opacity: 1;
                box-shadow: 0 0 15px rgba(74, 222, 128, 0.8);
            }
        }
        
        @keyframes nexus-pulse-slow {
            0%, 100% {
                opacity: 0.3;
            }
            50% {
                opacity: 0.6;
            }
        }
        
        @keyframes nexus-float {
            0%, 100% {
                transform: translateY(0px) rotate(0deg);
            }
            50% {
                transform: translateY(-10px) rotate(5deg);
            }
        }
        
        @keyframes nexus-float-delay-1 {
            0%, 100% {
                transform: translateY(0px) rotate(0deg);
            }
            50% {
                transform: translateY(-8px) rotate(-3deg);
            }
        }
        
        @keyframes nexus-float-delay-2 {
            0%, 100% {
                transform: translateY(0px) rotate(0deg);
            }
            50% {
                transform: translateY(-12px) rotate(8deg);
            }
        }
        
        @keyframes nexus-float-delay-3 {
            0%, 100% {
                transform: translateY(0px) rotate(0deg);
            }
            50% {
                transform: translateY(-6px) rotate(-6deg);
            }
        }
        
        .nexus-rune {
            position: absolute;
            font-size: 20px;
            opacity: 0.4;
            pointer-events: none;
            animation: nexus-float 6s ease-in-out infinite;
        }
        
        .rune-1 {
            top: 10%;
            left: 10%;
            animation-delay: 0s;
        }
        
        .rune-2 {
            top: 20%;
            right: 15%;
            animation-delay: 1s;
            animation-name: nexus-float-delay-1;
        }
        
        .rune-3 {
            bottom: 15%;
            left: 20%;
            animation-delay: 2s;
            animation-name: nexus-float-delay-2;
        }
        
        .rune-4 {
            bottom: 25%;
            right: 10%;
            animation-delay: 3s;
            animation-name: nexus-float-delay-3;
        }
        
        /* Scroll personalizado para el chat */
        #nexus-chat::-webkit-scrollbar {
            width: 8px;
        }
        
        #nexus-chat::-webkit-scrollbar-track {
            background: rgba(212, 175, 55, 0.05);
            border-radius: 10px;
        }
        
        #nexus-chat::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #ae0001, #8b0000);
            border-radius: 10px;
            border: 2px solid rgba(212, 175, 55, 0.2);
        }
        
        #nexus-chat::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #d4af37, #b8860b);
        }
        
        /* Efecto hover en botones */
        #nexus-minimize:hover,
        #nexus-close:hover {
            transform: scale(1.1);
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
        
        #nexus-send:hover {
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 0 20px rgba(174, 0, 1, 0.6);
            background: linear-gradient(135deg, #d4af37, #b8860b);
        }
    `;
    document.head.appendChild(style);
}

function agregarMensaje(texto, tipo) {
    const chat = document.getElementById('nexus-chat');
    const mensaje = document.createElement('div');
    mensaje.style.cssText = `
        margin: 10px 0;
        padding: 12px 16px;
        border-radius: 14px;
        max-width: 88%;
        word-wrap: break-word;
        font-size: 14px;
        position: relative;
        animation: nexus-message-fade 0.4s ease-out forwards;
        opacity: 0;
        transform: translateY(10px);
    `;
    
    // Aplicar animación con delay
    setTimeout(() => {
        mensaje.style.opacity = '1';
        mensaje.style.transform = 'translateY(0)';
    }, 10);

    if (tipo === 'user') {
        mensaje.style.cssText += `
            background: linear-gradient(135deg, rgba(174, 0, 1, 0.2), rgba(139, 0, 0, 0.3));
            margin-left: auto;
            color: #ffd700;
            border: 1px solid rgba(212, 175, 55, 0.3);
            box-shadow: 0 4px 15px rgba(174, 0, 1, 0.2);
        `;
        // Icono de usuario
        mensaje.innerHTML = `
            <div style="display: flex; align-items: start; gap: 10px;">
                <span style="font-size: 18px;">🧙‍♂️</span>
                <div>${texto}</div>
            </div>
        `;
    } else {
        mensaje.style.cssText += `
            background: linear-gradient(135deg, rgba(34, 47, 91, 0.3), rgba(26, 26, 46, 0.5));
            color: #e0e0e0;
            border-left: 3px solid #d4af37;
            border: 1px solid rgba(212, 175, 55, 0.1);
            box-shadow: 0 4px 15px rgba(34, 47, 91, 0.2);
        `;
        // Icono de IA
        mensaje.innerHTML = `
            <div style="display: flex; align-items: start; gap: 10px;">
                <span style="font-size: 18px;">🧠</span>
                <div>${texto}</div>
            </div>
        `;
    }
    
    chat.appendChild(mensaje);
    chat.scrollTop = chat.scrollHeight;
    
    // Añadir animación CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes nexus-message-fade {
            0% {
                opacity: 0;
                transform: translateY(10px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

function procesarPregunta(pregunta) {
    if (!pregunta.trim()) return;
    
    agregarMensaje(pregunta, 'user');
    
    // Palabras clave para derivar al soporte
    const palabrasSoporte = [
        'problema', 'error', 'no funciona', 'ayuda', 'soporte', 'técnico', 'bug',
        'falla', 'roto', 'avería', 'difícil', 'complicado', 'no puedo', 'imposible',
        'pago', 'factura', 'dinero', 'cobro', 'facturación', 'administrador',
        'crash', 'lento', 'bloqueado', 'atascado', 'urgente', 'emergencia'
    ];
    
    const incluyeSoporte = palabrasSoporte.some(palabra => 
        pregunta.toLowerCase().includes(palabra)
    );
    
    setTimeout(() => {
        if (incluyeSoporte) {
            // Derivar al soporte con mensaje mágico
            agregarMensaje("⚠️ ⚡ Detecto una situación que requiere atención especializada.", "bot");
            setTimeout(() => {
                agregarMensaje("🔮 Te recomiendo contactar directamente con nuestro equipo de soporte mágico para una solución rápida y personalizada.", "bot");
            }, 500);
            setTimeout(() => {
                agregarMensaje("🚪 Puedes acceder a la sección de Soporte desde el menú de navegación superior. ¡Allí recibirás ayuda inmediata de nuestros expertos!", "bot");
            }, 1000);
        } else {
            // Respuesta general con toque mágico
            const respuestas = [
                "✨ Estoy aquí para iluminar tu camino en el aprendizaje. ¿Qué te gustaría explorar hoy?",
                "📚 La sabiduría está a tu alcance. Puedo ayudarte con información sobre cursos y funcionalidades de la plataforma.",
                "🔮 Para asistencia técnica o problemas específicos, te recomiendo visitar la sección de Soporte en el menú. ¡Nuestros magos técnicos te ayudarán!",
                "⚡ Recuerda que para cualquier desafío técnico, el equipo de soporte está disponible en la sección 'Soporte'. ¡Están preparados para cualquier hechizo!",
                "🧙‍♂️ La magia del conocimiento fluye a través de GC ACADEMIA. ¿Sobre qué tema te gustaría aprender más?",
                "💡 Cada pregunta es una oportunidad para crecer. ¿Qué misterio educativo quieres resolver hoy?"
            ];
            const respuesta = respuestas[Math.floor(Math.random() * respuestas.length)];
            agregarMensaje(respuesta, "bot");
        }
    }, 1200);
}

// Inicializar si ya hay sesión activa
if (document.querySelector('[data-curso-id]')) {
    window.nexusCargada = true;
}