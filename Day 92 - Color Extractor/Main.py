import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from sklearn.cluster import KMeans
import pyperclip
import os


class ColorExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Color Extractor - Extraia as cores dominantes")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')

        # Variáveis
        self.image_path = None
        self.original_image = None
        self.extracted_colors = []

        self.setup_ui()

    def setup_ui(self):
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')

        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(
            main_frame,
            text="🎨 Color Extractor",
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            main_frame,
            text="Extraia as 10 cores mais dominantes de qualquer imagem",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        subtitle_label.pack(pady=(0, 20))

        # Frame para upload
        upload_frame = tk.Frame(main_frame, bg='#f0f0f0')
        upload_frame.pack(fill=tk.X, pady=(0, 20))

        # Botão de upload
        self.upload_btn = tk.Button(
            upload_frame,
            text="📁 Selecionar Imagem",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            border=0,
            cursor='hand2',
            command=self.select_image
        )
        self.upload_btn.pack(side=tk.LEFT)

        # Botão de extração
        self.extract_btn = tk.Button(
            upload_frame,
            text="🎨 Extrair Cores",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            border=0,
            cursor='hand2',
            command=self.extract_colors,
            state=tk.DISABLED
        )
        self.extract_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Frame para imagem
        self.image_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Label para imagem
        self.image_label = tk.Label(
            self.image_frame,
            text="Nenhuma imagem selecionada\\n\\nClique em 'Selecionar Imagem' para começar",
            font=('Arial', 14),
            bg='#ffffff',
            fg='#95a5a6',
            justify=tk.CENTER
        )
        self.image_label.pack(expand=True)

        # Frame para cores
        self.colors_frame = tk.Frame(main_frame, bg='#f0f0f0')
        self.colors_frame.pack(fill=tk.X)

        # Label de cores
        self.colors_title = tk.Label(
            self.colors_frame,
            text="🎨 Cores Extraídas",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )

        # Frame para paleta de cores
        self.palette_frame = tk.Frame(self.colors_frame, bg='#f0f0f0')

    def select_image(self):
        """Seleciona uma imagem do sistema"""
        file_types = [
            ('Imagens', '*.png *.jpg *.jpeg *.gif *.bmp *.webp'),
            ('PNG', '*.png'),
            ('JPEG', '*.jpg *.jpeg'),
            ('GIF', '*.gif'),
            ('BMP', '*.bmp'),
            ('WEBP', '*.webp'),
            ('Todos os arquivos', '*.*')
        ]

        filename = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=file_types
        )

        if filename:
            self.image_path = filename
            self.load_image()

    def load_image(self):
        """Carrega e exibe a imagem selecionada"""
        try:
            # Carregar imagem original
            self.original_image = Image.open(self.image_path)

            # Redimensionar para exibição
            display_image = self.original_image.copy()
            display_image.thumbnail((400, 300), Image.Resampling.LANCZOS)

            # Converter para PhotoImage
            self.photo = ImageTk.PhotoImage(display_image)

            # Atualizar label da imagem
            self.image_label.configure(
                image=self.photo,
                text="",
                bg='#ffffff'
            )

            # Habilitar botão de extração
            self.extract_btn.configure(state=tk.NORMAL)

            # Limpar cores anteriores
            self.clear_colors()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {str(e)}")

    def extract_colors(self):
        """Extrai as cores dominantes da imagem"""
        if not self.original_image:
            return

        try:
            # Mostrar que está processando
            self.extract_btn.configure(text="⏳ Processando...", state=tk.DISABLED)
            self.root.update()

            # Converter imagem para RGB
            img = self.original_image.convert('RGB')

            # Redimensionar para melhorar performance
            img.thumbnail((300, 300))

            # Converter para array numpy
            img_array = np.array(img)

            # Reshape para lista de pixels
            pixels = img_array.reshape(-1, 3)

            # Aplicar K-Means clustering
            kmeans = KMeans(n_clusters=10, random_state=0, n_init=10)
            kmeans.fit(pixels)

            # Obter as cores dominantes
            dominant_colors = kmeans.cluster_centers_

            # Obter as labels para calcular frequência
            labels = kmeans.labels_
            unique_labels, counts = np.unique(labels, return_counts=True)

            # Criar lista de cores com frequências
            color_info = []
            for i, color in enumerate(dominant_colors):
                frequency = counts[i] / len(labels)
                hex_color = '#%02x%02x%02x' % (int(color[0]), int(color[1]), int(color[2]))
                color_info.append({
                    'hex': hex_color,
                    'rgb': [int(color[0]), int(color[1]), int(color[2])],
                    'frequency': frequency
                })

            # Ordenar por frequência
            color_info.sort(key=lambda x: x['frequency'], reverse=True)

            self.extracted_colors = color_info
            self.display_colors()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao extrair cores: {str(e)}")
        finally:
            # Restaurar botão
            self.extract_btn.configure(text="🎨 Extrair Cores", state=tk.NORMAL)

    def display_colors(self):
        """Exibe as cores extraídas"""
        # Mostrar título das cores
        self.colors_title.pack(pady=(20, 10))

        # Limpar paleta anterior
        for widget in self.palette_frame.winfo_children():
            widget.destroy()

        # Criar grid de cores
        for i, color_info in enumerate(self.extracted_colors):
            row = i // 5
            col = i % 5

            # Frame para cada cor
            color_frame = tk.Frame(self.palette_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
            color_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

            # Swatch de cor
            color_swatch = tk.Frame(
                color_frame,
                bg=color_info['hex'],
                width=80,
                height=80
            )
            color_swatch.pack(pady=5)
            color_swatch.pack_propagate(False)

            # Código HEX
            hex_label = tk.Label(
                color_frame,
                text=color_info['hex'],
                font=('Courier', 10, 'bold'),
                bg='#ffffff',
                fg='#2c3e50'
            )
            hex_label.pack(pady=2)

            # Percentual
            percent_label = tk.Label(
                color_frame,
                text=f"{color_info['frequency']:.1%}",
                font=('Arial', 8),
                bg='#ffffff',
                fg='#7f8c8d'
            )
            percent_label.pack()

            # Botão copiar
            copy_btn = tk.Button(
                color_frame,
                text="Copiar",
                font=('Arial', 8),
                bg='#27ae60',
                fg='white',
                border=0,
                cursor='hand2',
                command=lambda hex_code=color_info['hex']: self.copy_color(hex_code)
            )
            copy_btn.pack(pady=2)

        # Configurar grid
        for i in range(5):
            self.palette_frame.columnconfigure(i, weight=1)

        self.palette_frame.pack(fill=tk.X)

    def copy_color(self, hex_code):
        """Copia o código HEX para a área de transferência"""
        try:
            pyperclip.copy(hex_code)
            messagebox.showinfo("Copiado!", f"Cor {hex_code} copiada para a área de transferência!")
        except:
            # Fallback se pyperclip não funcionar
            self.root.clipboard_clear()
            self.root.clipboard_append(hex_code)
            messagebox.showinfo("Copiado!", f"Cor {hex_code} copiada para a área de transferência!")

    def clear_colors(self):
        """Limpa a exibição de cores"""
        self.colors_title.pack_forget()
        for widget in self.palette_frame.winfo_children():
            widget.destroy()
        self.palette_frame.pack_forget()


def main():
    root = tk.Tk()
    app = ColorExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
