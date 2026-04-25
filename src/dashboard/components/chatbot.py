# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import os
import pathlib


import pandas as pd


def render_floating_chatbot(df: pd.DataFrame = None):
    """Render a floating chatbot widget at the bottom-right corner of every page.
    
    This uses components.html to inject a fully self-contained HTML/CSS/JS widget
    directly into the parent document body, completely bypassing Streamlit's DOM.
    """

    # Force-load .env from the project root to guarantee GROQ_API_KEY is available
    from dotenv import load_dotenv
    env_path = pathlib.Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    groq_api_key = os.environ.get("GROQ_API_KEY", "")

    # ── Build real dataset context for the AI ──
    dataset_context = "No dataset is currently loaded."
    if df is not None and not df.empty:
        total = len(df)
        cols = list(df.columns)
        context_parts = [f"Current dataset: {total} rows, {len(cols)} columns."]
        context_parts.append(f"Columns: {', '.join(cols)}")

        if "Sentiment" in df.columns:
            counts = df["Sentiment"].value_counts()
            dist_parts = []
            for label, count in counts.items():
                pct = round(count / total * 100, 1)
                dist_parts.append(f"{label}: {count} ({pct}%)")
            context_parts.append(f"Sentiment distribution: {'; '.join(dist_parts)}")

        if "Platform" in df.columns:
            platforms = df["Platform"].value_counts().head(5)
            plat_parts = [f"{p}: {c}" for p, c in platforms.items()]
            context_parts.append(f"Top platforms: {'; '.join(plat_parts)}")

        if "text" in df.columns or "Text" in df.columns:
            text_col = "text" if "text" in df.columns else "Text"
            avg_len = round(df[text_col].astype(str).str.len().mean(), 1)
            context_parts.append(f"Average text length: {avg_len} chars")

        dataset_context = " | ".join(context_parts)

    # ── Theme Handling ──
    theme = st.session_state.get("theme", "dark")
    is_dark = theme == "dark"
    
    if is_dark:
        panel_bg = "#1a1d2e"
        panel_border = "rgba(255,255,255,0.08)"
        msg_bot_bg = "rgba(85, 66, 246, 0.12)"
        msg_bot_color = "#d4d4f7"
        text_primary = "#e0e0e0"
        input_bg = "rgba(255,255,255,0.06)"
        input_border = "rgba(255,255,255,0.1)"
        header_p_color = "rgba(255,255,255,0.65)"
        close_btn_color = "rgba(255,255,255,0.6)"
        input_placeholder = "rgba(255,255,255,0.3)"
    else:
        panel_bg = "#ffffff"
        panel_border = "#E5E7EB"
        msg_bot_bg = "rgba(85, 66, 246, 0.08)"
        msg_bot_color = "#374151"
        text_primary = "#111827"
        input_bg = "#F9FAFB"
        input_border = "#E5E7EB"
        header_p_color = "rgba(255,255,255,0.85)"
        close_btn_color = "rgba(255,255,255,0.8)"
        input_placeholder = "rgba(0,0,0,0.4)"

    # Create a version stamp based on dataset content so widget refreshes only when data or theme changes
    import hashlib
    data_hash = hashlib.md5(dataset_context.encode()).hexdigest()[:10]
    widget_version = f"{data_hash}_{theme}_{groq_api_key[:6] if groq_api_key else 'nokey'}"

    # Escape for safe JS string embedding
    dataset_context_js = dataset_context.replace("'", "\\'")

    chatbot_html = f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        const WIDGET_VER = '{widget_version}';

        // Always recreate widget on page load to ensure fresh event listeners
        const existing = parentDoc.getElementById('sentiintel-chatbot-root');
        if (existing) existing.remove();

        // ─── Create root container ───
        const root = parentDoc.createElement('div');
        root.id = 'sentiintel-chatbot-root';
        root.dataset.ver = WIDGET_VER;
        root.innerHTML = `
        <style>
            /* ── Floating Action Button ── */
            #si-fab {{
                position: fixed;
                bottom: 85px; /* Moved up to clear Streamlit Manage Bar */
                right: 28px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: #5542F6;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 18px rgba(85, 66, 246, 0.45);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 999999;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            #si-fab:hover {{
                transform: scale(1.08);
                box-shadow: 0 6px 24px rgba(85, 66, 246, 0.55);
            }}
            #si-fab svg {{
                width: 30px;
                height: 30px;
            }}

            /* ── Chat Panel ── */
            #si-panel {{
                position: fixed;
                bottom: 155px; /* Adjusted based on FAB move */
                right: 28px;
                width: 380px;
                height: 550px;
                border-radius: 16px;
                background: {panel_bg};
                border: 1px solid {panel_border};
                box-shadow: 0 12px 48px rgba(0,0,0,0.35);
                z-index: 999998;
                display: none;
                flex-direction: column;
                overflow: hidden;
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            }}
            #si-panel.open {{
                display: flex;
            }}

            /* ── Header ── */
            #si-header {{
                background: linear-gradient(135deg, #2D3748 0%, #5542F6 100%);
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 12px;
                flex-shrink: 0;
            }}
            #si-header-icon {{
                width: 38px;
                height: 38px;
                background: rgba(255,255,255,0.15);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            #si-header-icon svg {{
                width: 20px;
                height: 20px;
            }}
            #si-header-text h3 {{
                margin: 0;
                font-size: 15px;
                font-weight: 700;
                color: #ffffff !important;
                line-height: 1.2;
            }}
            #si-header-text p {{
                margin: 0;
                font-size: 11px;
                color: #ffffff !important;
                opacity: 0.8;
            }}
            #si-close {{
                margin-left: auto;
                background: none;
                border: none;
                color: {close_btn_color};
                cursor: pointer;
                font-size: 20px;
                padding: 4px 8px;
                border-radius: 6px;
                transition: background 0.15s;
            }}
            #si-close:hover {{
                background: rgba(255,255,255,0.1);
                color: #fff;
            }}

            /* ── Messages Area ── */
            #si-messages {{
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            #si-messages::-webkit-scrollbar {{
                width: 4px;
            }}
            #si-messages::-webkit-scrollbar-thumb {{
                background: rgba(255,255,255,0.15);
                border-radius: 4px;
            }}
            .si-msg {{
                max-width: 85%;
                padding: 10px 14px;
                border-radius: 12px;
                font-size: 13px;
                line-height: 1.5;
                word-wrap: break-word;
            }}
            .si-msg.bot {{
                align-self: flex-start;
                background: {msg_bot_bg};
                color: {msg_bot_color};
                border-bottom-left-radius: 4px;
            }}
            .si-msg.user {{
                align-self: flex-end;
                background: #5542F6;
                color: #fff;
                border-bottom-right-radius: 4px;
            }}
            .si-msg.error {{
                align-self: flex-start;
                background: rgba(220, 50, 50, 0.15);
                color: #ff8888;
                border-bottom-left-radius: 4px;
            }}
            .si-typing {{
                align-self: flex-start;
                color: {text_primary} !important;
                opacity: 0.6;
                font-size: 12px;
                font-style: italic;
                margin-top: 4px;
            }}

            /* ── Input Area ── */
            #si-input-area {{
                padding: 12px 16px;
                border-top: 1px solid {panel_border};
                display: flex;
                gap: 10px;
                align-items: center;
                flex-shrink: 0;
                background: rgba(0,0,0,0.05);
            }}
            #si-input {{
                flex: 1;
                background: {input_bg};
                border: 1px solid {input_border};
                border-radius: 22px;
                padding: 10px 16px;
                color: {text_primary};
                font-size: 13px;
                outline: none;
                font-family: inherit;
                transition: border-color 0.2s;
            }}
            #si-input::placeholder {{
                color: {input_placeholder};
            }}
            #si-input:focus {{
                border-color: #5542F6;
            }}
            #si-send {{
                width: 38px;
                height: 38px;
                border-radius: 50%;
                background: #5542F6;
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                transition: background 0.15s;
            }}
            #si-send:hover {{
                background: #4A3AD9;
            }}
            #si-send svg {{
                width: 18px;
                height: 18px;
            }}
        </style>

        <!-- Floating Action Button -->
        <button id="si-fab" title="SentiIntel AI Assistant">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="9" width="16" height="11" rx="3" ry="3"/>
                <line x1="9" y1="13" x2="9" y2="16"/>
                <line x1="15" y1="13" x2="15" y2="16"/>
                <line x1="1" y1="14" x2="4" y2="14"/>
                <line x1="20" y1="14" x2="23" y2="14"/>
                <line x1="10" y1="9" x2="10" y2="6"/>
                <line x1="10" y1="6" x2="14" y2="6"/>
            </svg>
        </button>

        <!-- Chat Panel -->
        <div id="si-panel">
            <div id="si-header">
                <div id="si-header-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="4" y="9" width="16" height="11" rx="3" ry="3"/>
                        <line x1="9" y1="13" x2="9" y2="16"/>
                        <line x1="15" y1="13" x2="15" y2="16"/>
                    </svg>
                </div>
                <div id="si-header-text">
                    <h3>SentiIntel</h3>
                    <p>Premium AI Assistant</p>
                </div>
                <button id="si-close">&times;</button>
            </div>
            <div id="si-messages">
                <div class="si-msg bot">Hi! I'm SentiIntel, your AI assistant. Ask me anything about sentiment analysis, data insights, or how to use this dashboard.</div>
            </div>
            <div id="si-input-area">
                <input id="si-input" type="text" placeholder="Type a message..." autocomplete="off" />
                <button id="si-send">
                    <svg viewBox="0 0 24 24" fill="white" stroke="none">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        </div>
        `;

        parentDoc.body.appendChild(root);

        // ─── Wire up interactions ───
        const fab = parentDoc.getElementById('si-fab');
        const panel = parentDoc.getElementById('si-panel');
        const closeBtn = parentDoc.getElementById('si-close');
        const input = parentDoc.getElementById('si-input');
        const sendBtn = parentDoc.getElementById('si-send');
        const messagesDiv = parentDoc.getElementById('si-messages');

        fab.addEventListener('click', () => {{
            panel.classList.toggle('open');
            if (panel.classList.contains('open')) {{
                input.focus();
            }}
        }});

        closeBtn.addEventListener('click', () => {{
            panel.classList.remove('open');
        }});

        function addMsg(text, cls) {{
            const div = parentDoc.createElement('div');
            div.className = 'si-msg ' + cls;
            div.textContent = text;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            return div;
        }}

        async function sendMessage() {{
            const text = input.value.trim();
            if (!text) return;

            input.value = '';
            addMsg(text, 'user');

            const typingDiv = parentDoc.createElement('div');
            typingDiv.className = 'si-typing';
            typingDiv.textContent = 'Thinking...';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            const apiKey = '{groq_api_key}';

            if (!apiKey) {{
                messagesDiv.removeChild(typingDiv);
                addMsg('Error: GROQ_API_KEY is not configured in the backend .env file.', 'error');
                return;
            }}

            // Build messages array from current chat
            const allMsgs = messagesDiv.querySelectorAll('.si-msg');
            const history = [];
            allMsgs.forEach(m => {{
                if (m.classList.contains('user')) {{
                    history.push({{ role: 'user', content: m.textContent }});
                }} else if (m.classList.contains('bot')) {{
                    history.push({{ role: 'assistant', content: m.textContent }});
                }}
            }});

            const payload = {{
                model: 'llama-3.3-70b-versatile',
                messages: [
                    {{ role: 'system', content: 'You are SentiIntel, a premium AI assistant for a Sentiment Analysis Dashboard. You MUST use the following REAL dataset statistics when answering questions about the current data. NEVER make up numbers. Here is the current dataset context: {dataset_context_js}. If the user asks about data you do not have, say you do not have that specific information. Keep answers concise and accurate.' }},
                    ...history
                ],
                stream: false
            }};

            try {{
                const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {{
                    method: 'POST',
                    headers: {{
                        'Authorization': 'Bearer ' + apiKey,
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(payload)
                }});

                messagesDiv.removeChild(typingDiv);

                if (!res.ok) {{
                    const errData = await res.text();
                    addMsg('API Error (' + res.status + '): ' + errData.substring(0, 200), 'error');
                    return;
                }}

                const data = await res.json();
                const reply = data.choices[0].message.content;
                addMsg(reply, 'bot');
            }} catch (err) {{
                messagesDiv.removeChild(typingDiv);
                addMsg('Network Error: ' + err.message, 'error');
            }}
        }}

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keydown', (e) => {{
            if (e.key === 'Enter' && !e.shiftKey) {{
                e.preventDefault();
                sendMessage();
            }}
        }});
    }})();
    </script>
    """

    components.html(chatbot_html, height=0)
