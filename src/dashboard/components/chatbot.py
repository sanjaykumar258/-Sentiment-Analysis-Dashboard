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
        
        # 1. Sentiment distribution
        sent_info = "N/A"
        if "Sentiment" in df.columns:
            counts = df["Sentiment"].value_counts()
            dist_parts = []
            for label, count in counts.items():
                pct = round(count / total * 100, 1)
                dist_parts.append(f"{label}: {count} ({pct}%)")
            sent_info = "; ".join(dist_parts)

        # 2. Top platforms
        plat_info = "N/A"
        if "Platform" in df.columns:
            platforms = df["Platform"].value_counts().head(3)
            plat_info = ", ".join([f"{p} ({c} posts)" for p, c in platforms.items()])

        # 3. Top categories
        cat_info = "N/A"
        if "Category" in df.columns:
            categories = df["Category"].value_counts().head(3)
            cat_info = ", ".join([f"{c} ({n} posts)" for c, n in categories.items()])

        # 4. Virality & Engagement
        virality_info = "N/A"
        eng_cols = ["Likes", "Comments", "Shares", "Views"]
        if all(c in df.columns for c in eng_cols):
            cols.append("Virality_Score") # Explicitly add to columns to satisfy AI check
            df_temp = df.copy()
            df_temp["virality_score"] = (df_temp["Shares"] * 3 + df_temp["Comments"] * 2 + df_temp["Likes"]) / (df_temp["Views"] + 1)
            
            if "Category" in df.columns:
                cat_vir = df_temp.groupby("Category")["virality_score"].mean().sort_values(ascending=False).head(5)
                vir_parts = [f"{c} (Score: {round(v, 4)})" for c, v in cat_vir.items()]
                virality_info = " | ".join(vir_parts)

        # 5. Top Performers
        performer_info = "N/A"
        if "Post_ID" in df.columns and "Engagement_Rate" in df.columns:
            top_posts = df.sort_values("Engagement_Rate", ascending=False).head(3)
            performer_info = ", ".join([f"{row['Post_ID']} on {row['Platform']} ({row['Engagement_Rate']}% engagement)" for _, row in top_posts.iterrows()])

        # Construct a highly structured context string
        dataset_context = (
            f"DATASET_OVERVIEW: Total Rows={total}, Columns={', '.join(cols)}. "
            f"SENTIMENT_DISTRIBUTION: {sent_info}. "
            f"TOP_PLATFORMS: {plat_info}. "
            f"TOP_CATEGORIES_BY_VOLUME: {cat_info}. "
            f"TOP_CATEGORIES_BY_VIRALITY_SCORE: {virality_info}. "
            f"TOP_PERFORMING_POSTS: {performer_info}."
        )

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

    # Escape for safe JS string embedding (handle quotes and template literals)
    dataset_context_js = dataset_context.replace("'", "\\'").replace("`", "\\`").replace("${", "$\\{")

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
                    {{ 
                        role: 'system', 
                        content: `You are SentiIntel, a premium AI data assistant. 
                        You MUST use the REAL dataset statistics provided below. NEVER claim you lack information that is present in the context.
                        
                        CRITICAL: "Virality Score" is a valid calculated metric in this dashboard (weighted by Shares, Comments, and Likes). 
                        You HAVE this information in the context below under "TOP_CATEGORIES_BY_VIRALITY_SCORE".
                        
                        CONTEXT: {dataset_context_js}
                        
                        Answer concisely and professionally based ONLY on this context.` 
                    }},
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
