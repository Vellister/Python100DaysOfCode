#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime, timedelta

class DangerousWritingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicativo de Escrita Perigosa")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Variáveis de controle
        self.timer_seconds = 5
        self.current_timer = self.timer_seconds
        self.is_typing = False
        self.timer_thread = None
        self.start_time = None
        self.total_writing_time = 0
        self.is_running = False
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar interface
        self.create_widgets()
        
        # Iniciar timer
        self.reset_timer()
        
    def setup_styles(self):
        """Configura os estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('Title.TLabel', 
                       background='#2c3e50', 
                       foreground='white', 
                       font=('Arial', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background='#2c3e50', 
                       foreground='#bdc3c7', 
                       font=('Arial', 12))
        
        style.configure('Timer.TLabel', 
                       background='#34495e', 
                       foreground='#2ecc71', 
                       font=('Arial', 36, 'bold'),
                       anchor='center')
        
        style.configure('TimerWarning.TLabel', 
                       background='#34495e', 
                       foreground='#e74c3c', 
                       font=('Arial', 36, 'bold'),
                       anchor='center')
        
        style.configure('Stats.TLabel', 
                       background='#34495e', 
                       foreground='white', 
                       font=('Arial', 14, 'bold'),
                       anchor='center')
        
        style.configure('StatsValue.TLabel', 
                       background='#34495e', 
                       foreground='#3498db', 
                       font=('Arial', 18, 'bold'),
                       anchor='center')
        
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="Aplicativo de Escrita Perigosa", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="Não pare de escrever, ou todo o progresso será perdido.", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # Frame do timer
        timer_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        timer_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.timer_label = ttk.Label(timer_frame, 
                                    text=f"{self.timer_seconds}", 
                                    style='Timer.TLabel')
        self.timer_label.pack(pady=15)
        
        timer_desc_label = ttk.Label(timer_frame, 
                                    text="segundos restantes", 
                                    style='Subtitle.TLabel')
        timer_desc_label.pack(pady=(0, 10))
        
        # Barra de progresso do timer
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(timer_frame, 
                                           variable=self.progress_var, 
                                           maximum=self.timer_seconds,
                                           style='TProgressbar')
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Área de texto
        text_frame = tk.Frame(main_frame, bg='#2c3e50')
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Scrollbar para o texto
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(text_frame, 
                                wrap=tk.WORD, 
                                font=('Arial', 12),
                                bg='#ecf0f1',
                                fg='#2c3e50',
                                insertbackground='#3498db',
                                selectbackground='#3498db',
                                selectforeground='white',
                                yscrollcommand=scrollbar.set)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)
        
        # Bind eventos do texto
        self.text_area.bind('<KeyPress>', self.on_key_press)
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.focus_set()
        
        # Frame de estatísticas
        stats_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats_container = tk.Frame(stats_frame, bg='#34495e')
        stats_container.pack(pady=15)
        
        # Palavras
        words_frame = tk.Frame(stats_container, bg='#34495e')
        words_frame.pack(side=tk.LEFT, padx=20)
        
        self.words_label = ttk.Label(words_frame, text="0", style='StatsValue.TLabel')
        self.words_label.pack()
        ttk.Label(words_frame, text="palavras", style='Stats.TLabel').pack()
        
        # Caracteres
        chars_frame = tk.Frame(stats_container, bg='#34495e')
        chars_frame.pack(side=tk.LEFT, padx=20)
        
        self.chars_label = ttk.Label(chars_frame, text="0", style='StatsValue.TLabel')
        self.chars_label.pack()
        ttk.Label(chars_frame, text="caracteres", style='Stats.TLabel').pack()
        
        # Tempo escrevendo
        time_frame = tk.Frame(stats_container, bg='#34495e')
        time_frame.pack(side=tk.LEFT, padx=20)
        
        self.time_label = ttk.Label(time_frame, text="00:00", style='StatsValue.TLabel')
        self.time_label.pack()
        ttk.Label(time_frame, text="tempo escrevendo", style='Stats.TLabel').pack()
        
        # Botões
        buttons_frame = tk.Frame(main_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X)
        
        button_container = tk.Frame(buttons_frame, bg='#2c3e50')
        button_container.pack()
        
        reset_btn = tk.Button(button_container, 
                             text="Reiniciar", 
                             command=self.reset_app,
                             bg='#95a5a6', 
                             fg='white', 
                             font=('Arial', 12, 'bold'),
                             relief=tk.FLAT,
                             padx=20, 
                             pady=10)
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = tk.Button(button_container, 
                            text="Salvar Texto", 
                            command=self.save_text,
                            bg='#3498db', 
                            fg='white', 
                            font=('Arial', 12, 'bold'),
                            relief=tk.FLAT,
                            padx=20, 
                            pady=10)
        save_btn.pack(side=tk.LEFT, padx=10)
        
    def on_key_press(self, event):
        """Chamado quando uma tecla é pressionada"""
        if not self.is_running:
            self.start_writing_session()
        
        self.is_typing = True
        self.reset_timer()
        
    def on_key_release(self, event):
        """Chamado quando uma tecla é liberada"""
        self.is_typing = False
        self.update_stats()
        
    def start_writing_session(self):
        """Inicia uma nova sessão de escrita"""
        self.is_running = True
        self.start_time = datetime.now()
        self.update_writing_time()
        
    def reset_timer(self):
        """Reseta o timer de 5 segundos"""
        self.current_timer = self.timer_seconds
        self.update_timer_display()
        
        # Cancelar thread anterior se existir
        if self.timer_thread and self.timer_thread.is_alive():
            return
            
        # Iniciar nova thread do timer
        self.timer_thread = threading.Thread(target=self.countdown_timer, daemon=True)
        self.timer_thread.start()
        
    def countdown_timer(self):
        """Thread que executa a contagem regressiva"""
        while self.current_timer > 0:
            time.sleep(0.1)  # Atualização mais suave
            if self.is_typing:
                return  # Sair se o usuário estiver digitando
            
            self.current_timer -= 0.1
            self.root.after(0, self.update_timer_display)
            
        # Tempo esgotado
        self.root.after(0, self.time_expired)
        
    def update_timer_display(self):
        """Atualiza a exibição do timer"""
        seconds = max(0, int(self.current_timer))
        self.timer_label.config(text=str(seconds))
        
        # Atualizar barra de progresso
        self.progress_var.set(self.current_timer)
        
        # Mudar cor quando restam poucos segundos
        if self.current_timer <= 2:
            self.timer_label.config(style='TimerWarning.TLabel')
            self.root.configure(bg='#c0392b')
        else:
            self.timer_label.config(style='Timer.TLabel')
            self.root.configure(bg='#2c3e50')
            
    def time_expired(self):
        """Chamado quando o tempo expira"""
        # Limpar texto
        self.text_area.delete(1.0, tk.END)
        
        # Resetar variáveis
        self.is_running = False
        self.start_time = None
        self.total_writing_time = 0
        
        # Mostrar aviso
        messagebox.showwarning("Tempo Esgotado!", 
                              "Você parou de escrever por mais de 5 segundos.\n"
                              "Todo o seu texto foi apagado!")
        
        # Resetar interface
        self.reset_timer()
        self.update_stats()
        self.update_writing_time()
        
        # Focar no texto novamente
        self.text_area.focus_set()
        
    def update_stats(self):
        """Atualiza as estatísticas de palavras e caracteres"""
        text = self.text_area.get(1.0, tk.END).strip()
        
        # Contar palavras
        words = len(text.split()) if text else 0
        self.words_label.config(text=str(words))
        
        # Contar caracteres
        chars = len(text)
        self.chars_label.config(text=str(chars))
        
    def update_writing_time(self):
        """Atualiza o tempo total de escrita"""
        if self.start_time and self.is_running:
            elapsed = datetime.now() - self.start_time
            total_seconds = int(elapsed.total_seconds())
            
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.time_label.config(text=time_str)
            
            # Agendar próxima atualização
            self.root.after(1000, self.update_writing_time)
        else:
            self.time_label.config(text="00:00")
            
    def reset_app(self):
        """Reinicia o aplicativo"""
        result = messagebox.askyesno("Confirmar Reset", 
                                   "Tem certeza que deseja reiniciar?\n"
                                   "Todo o texto será perdido!")
        
        if result:
            self.text_area.delete(1.0, tk.END)
            self.is_running = False
            self.start_time = None
            self.total_writing_time = 0
            self.reset_timer()
            self.update_stats()
            self.update_writing_time()
            self.text_area.focus_set()
            
    def save_text(self):
        """Salva o texto em um arquivo"""
        text = self.text_area.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showinfo("Nada para salvar", "Não há texto para salvar!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            title="Salvar texto como..."
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(text)
                messagebox.showinfo("Sucesso", f"Texto salvo em:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")

def main():
    """Função principal"""
    root = tk.Tk()
    app = DangerousWritingApp(root)
    
    # Configurar fechamento da janela
    def on_closing():
        if messagebox.askokcancel("Sair", "Deseja realmente sair?\nTodo o texto não salvo será perdido!"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar aplicativo
    root.mainloop()

if __name__ == "__main__":
    main()

