# ⚡ Gemini MKT Express — Mini‑Agente de Marketing

Gera **3 ideias** de post e **2 legendas/ideia** a partir de Tema/Público/Oferta/Tom e calcula **estimativa ≈ orçamento ÷ CPR**. Feito para aula/workshop: simples, seguro e fácil de adaptar.

## Requisitos
- Python 3.10+
- Conta no **Google AI Studio** e **API Key** (gratuita, com cotas)
- (Opcional) Conta no **Streamlit Community Cloud**

## Instalação
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPO.git
cd SEU_REPO
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## Variáveis/Secrets
Defina **UMA** das opções abaixo (nunca exponha a chave no código):

**Local/Codespaces**
```bash
# macOS/Linux
export GOOGLE_API_KEY="SUA_CHAVE_DO_AI_STUDIO"
# Windows PowerShell
$env:GOOGLE_API_KEY="SUA_CHAVE_DO_AI_STUDIO"
```

**Streamlit Cloud (Deploy)**
- Em **Advanced settings → Secrets**, adicione:
```
GOOGLE_API_KEY="SUA_CHAVE_DO_AI_STUDIO"
```

## Como rodar (local)
```bash
streamlit run app.py
```
Abra o link mostrado no terminal.

## Deploy no Streamlit Cloud
1. Suba `app.py` e `requirements.txt` no GitHub.  
2. Acesse https://share.streamlit.io/ → **New app** → selecione o repo/branch/`app.py`.  
3. Em **Secrets**, adicione `GOOGLE_API_KEY`.  
4. **Deploy** e use **Rerun** após mudanças.

## Uso
1. Preencha **Tema/Nicho**, **Público**, **Oferta/Ângulo**, **Tom**.  
2. Informe **Orçamento (R$)** e **CPR (R$)**.  
3. Clique **Gerar ideias e estimativa**.  
4. Veja o texto gerado e **Resultados ≈ orçamento ÷ CPR** (ex.: 300/3 = 100).

## Guardrails
- `sanitize_text` (limita/limpa texto)  
- `validate_numbers` (números > 0 e limites razoáveis)  
- Prompt com políticas (sem promessas) e retry curto se estourar tokens.

## Estrutura
```
.
├─ app.py
├─ requirements.txt
└─ README.md
```
Sugestão `.gitignore`:
```
__pycache__/
*.pyc
.venv/
.env
.streamlit/secrets.toml
.ipynb_checkpoints/
.DS_Store
```

