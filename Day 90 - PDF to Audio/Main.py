from PyPDF2 import PdfReader
from gtts import gTTS
import os
import argparse

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except FileNotFoundError:
        print(f"Erro: O arquivo PDF \'{pdf_path}\' não foi encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return None
    return text

def convert_text_to_speech(text, lang='pt', output_file='audiobook.mp3'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_file)
        print(f"Áudio salvo como {output_file}")
    except Exception as e:
        print(f"Erro ao converter texto em fala: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converte um arquivo PDF em um audiolivro.")
    parser.add_argument("pdf_file", help="Caminho para o arquivo PDF de entrada.")
    parser.add_argument("-o", "--output", default="audiobook.mp3",
                        help="Nome do arquivo de áudio de saída (padrão: audiobook.mp3).")
    parser.add_argument("-l", "--lang", default="pt",
                        help="Idioma para a síntese de fala (padrão: pt para português).")

    args = parser.parse_args()

    print(f"Extraindo texto de {args.pdf_file}...")
    extracted_text = extract_text_from_pdf(args.pdf_file)

    if extracted_text:
        print("Texto extraído com sucesso. Convertendo para áudio...")
        convert_text_to_speech(extracted_text, lang=args.lang, output_file=args.output)
        print("Processo concluído.")
    else:
        print("Não foi possível extrair texto do PDF. O processo de conversão para áudio foi abortado.")

