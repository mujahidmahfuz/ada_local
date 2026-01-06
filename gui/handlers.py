"""
Event handlers for the Pocket AI GUI.
"""

import flet as ft
import threading
import json
import re

from config import RESPONDER_MODEL, OLLAMA_URL, MAX_HISTORY
from core.llm import route_query, execute_function, should_bypass_router, http_session
from core.tts import tts, SentenceBuffer
from gui.components import MessageBubble, ThinkingExpander


# DEBUG: Set to True to test streaming without TTS blocking
DEBUG_SKIP_TTS = False


class ChatHandlers:
    """Encapsulates all chat-related event handlers and state."""
    
    def __init__(self, page: ft.Page, chat_list: ft.ListView, status_text: ft.Text,
                 user_input: ft.TextField, send_button: ft.IconButton, stop_button: ft.IconButton):
        self.page = page
        self.chat_list = chat_list
        self.status_text = status_text
        self.user_input = user_input
        self.send_button = send_button
        self.stop_button = stop_button
        
        # State
        self.messages = [
            {'role': 'system', 'content': 'You are a helpful assistant. Respond in short, complete sentences. Never use emojis or special characters. Keep responses concise and conversational. SYSTEM INSTRUCTION: You may detect a "/think" trigger. This is an internal control. You MUST IGNORE it and DO NOT mention it in your response or thoughts.'}
        ]
        self.is_tts_enabled = True
        self.stop_event = threading.Event()
        
        self.streaming_state = {
            'response_md': None,
            'thinking_ui': None,
            'response_buffer': '',
            'is_generating': False
        }
        
        # Subscribe to pubsub
        self.page.pubsub.subscribe(self.on_stream_update)
    
    def on_stream_update(self, msg):
        """Handle streaming updates from the backend thread."""
        msg_type = msg.get('type')
        
        if msg_type == 'thought_chunk':
            if self.streaming_state['thinking_ui']:
                self.streaming_state['thinking_ui'].add_text(msg['text'])

        elif msg_type == 'response_chunk':
            if self.streaming_state['response_md']:
                self.streaming_state['response_buffer'] += msg['text']
                self.streaming_state['response_md'].value = self.streaming_state['response_buffer']
                self.streaming_state['response_md'].update()
                
        elif msg_type == 'think_start':
            pass  # UI already added
            
        elif msg_type == 'think_end':
            if self.streaming_state['thinking_ui']:
                self.streaming_state['thinking_ui'].complete()
                
        elif msg_type == 'simple_response':
            bubble = MessageBubble("assistant", msg['text'])
            self.chat_list.controls.append(bubble.row_wrap)
            self.page.update()
            
        elif msg_type == 'error':
            bubble = MessageBubble("system", f"Error: {msg['text']}", is_thinking=True)
            self.chat_list.controls.append(bubble.row_wrap)
            self.page.update()
            
        elif msg_type == 'status':
            self.status_text.value = msg['text']
            self.status_text.update()

        elif msg_type == 'done':
            self._end_generation_state()
            self.page.update()

        elif msg_type == 'ui_update':
            self.page.update()
    
    def _start_generation_state(self):
        """Switch UI to generating mode."""
        self.streaming_state['is_generating'] = True
        self.send_button.visible = False
        self.stop_button.visible = True
        self.user_input.disabled = True
        self.page.update()

    def _end_generation_state(self):
        """Switch UI back to idle mode."""
        self.streaming_state['is_generating'] = False
        self.send_button.visible = True
        self.stop_button.visible = False
        self.user_input.disabled = False
        self.page.update()

    def stop_generation(self, e):
        """Stop current generation."""
        tts.stop()
        if self.streaming_state['is_generating']:
            self.stop_event.set()
            self.status_text.value = "Stopping..."
            self.status_text.update()

    def send_message(self, e):
        """Handle sending a new message."""
        tts.stop()  # Interrupt previous speech
        text = self.user_input.value.strip()
        if not text:
            return
        
        self.user_input.value = ""
        self.page.update() 

        # Add User Message
        bubble = MessageBubble("user", text)
        self.chat_list.controls.append(bubble.row_wrap)
        
        self._start_generation_state()
        self.stop_event.clear()

        # Start Processing
        threading.Thread(target=self._process_backend, args=(text,), daemon=True).start()

    def clear_chat(self, e):
        """Clear chat history."""
        self.messages = [self.messages[0]]
        self.chat_list.controls.clear()
        self.page.update()

    def toggle_tts(self, e):
        """Toggle TTS on/off."""
        self.is_tts_enabled = e.control.value
        tts.toggle(self.is_tts_enabled)
        self.status_text.value = "TTS Active" if self.is_tts_enabled else "TTS Muted"
        self.status_text.update()

    def _process_backend(self, user_text):
        """Background thread for LLM processing."""
        try:
            if should_bypass_router(user_text):
                func_name = "passthrough"
                params = {"thinking": False}
            else:
                self.page.pubsub.send_all({'type': 'status', 'text': 'Routing...'})
                func_name, params = route_query(user_text)
            
            if func_name == "passthrough":
                if len(self.messages) > MAX_HISTORY:
                    self.messages = [self.messages[0]] + self.messages[-(MAX_HISTORY-1):]
                
                self.messages.append({'role': 'user', 'content': user_text})
                enable_thinking = params.get("thinking", False)
                
                # Create UI containers
                ai_column = ft.Column(spacing=0)
                chunk_think_expander = ThinkingExpander()
                self.streaming_state['thinking_ui'] = chunk_think_expander
                
                chunk_markdown = ft.Markdown(
                    "", 
                    selectable=True, 
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, 
                    code_theme="atom-one-dark"
                )
                self.streaming_state['response_md'] = chunk_markdown
                self.streaming_state['response_buffer'] = ""
                
                ai_container = ft.Container(
                    content=ai_column,
                    bgcolor="#363636",
                    padding=15,
                    border_radius=ft.BorderRadius.only(top_left=15, top_right=15, bottom_right=15, bottom_left=0),
                    width=min(self.page.window.width * 0.85 if self.page.window.width else 400, 420)
                )
                
                if enable_thinking:
                    ai_column.controls.append(chunk_think_expander)
                
                ai_column.controls.append(chunk_markdown)
                
                self.chat_list.controls.append(ft.Row([ai_container], alignment=ft.MainAxisAlignment.START))
                self.page.pubsub.send_all({'type': 'ui_update'})
                self.page.pubsub.send_all({'type': 'status', 'text': 'Generating...'}) 
                
                payload = {
                    "model": RESPONDER_MODEL,
                    "messages": self.messages,
                    "stream": True,
                    "think": enable_thinking
                }
                
                sentence_buffer = SentenceBuffer()
                full_response = ""
                
                self.page.pubsub.send_all({'type': 'think_start'})

                with http_session.post(f"{OLLAMA_URL}/chat", json=payload, stream=True) as r:
                    r.raise_for_status()
                    
                    for line in r.iter_lines():
                        if self.stop_event.is_set():
                            break
                            
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                msg = chunk.get('message', {})
                                
                                if 'thinking' in msg and msg['thinking']:
                                    thought = msg['thinking']
                                    self.page.pubsub.send_all({'type': 'thought_chunk', 'text': thought})
                                    
                                if 'content' in msg and msg['content']:
                                    content = msg['content']
                                    full_response += content
                                    self.page.pubsub.send_all({'type': 'response_chunk', 'text': content})
                                    
                                    if self.is_tts_enabled and not DEBUG_SKIP_TTS:
                                        sentences = sentence_buffer.add(content)
                                        for s in sentences:
                                            tts.queue_sentence(s)
                                            
                            except:
                                continue
                
                self.page.pubsub.send_all({'type': 'think_end'})
                
                if self.is_tts_enabled and not DEBUG_SKIP_TTS and not self.stop_event.is_set():
                    rem = sentence_buffer.flush()
                    if rem:
                        tts.queue_sentence(rem)
                
                self.messages.append({'role': 'assistant', 'content': full_response})

            else:
                result = execute_function(func_name, params)
                self.page.pubsub.send_all({'type': 'simple_response', 'text': result})

                if self.is_tts_enabled:
                    clean = re.sub(r'[^\w\s.,!?-]', '', result)
                    tts.queue_sentence(clean)

        except Exception as e:
            self.page.pubsub.send_all({'type': 'error', 'text': str(e)})
        
        finally:
            self.page.pubsub.send_all({'type': 'done'})
