# SumTube 🎬

> YouTube Video Summarizer powered by [LangChain](https://python.langchain.com/) and your choice of LLM.

SumTube fetches a YouTube transcript, sends it to a language model, and saves a clean Markdown summary — alongside the raw transcript files — in an organised output directory.

---

## Features

- **Interactive wizard** — guided setup that detects existing API keys in the environment and lets you confirm, override, or enter new ones.
- **Non-interactive / scripted mode** — all settings available as CLI flags for CI pipelines or shell scripts.
- **Multi-provider** — works with OpenAI, Anthropic, Google Gemini, Groq, Mistral, Ollama, and any other LangChain-supported provider.
- **Batch processing** — point it at a file of URLs and summarise them all in one run.
- **Custom prompts** — supply your own system prompt file or paste one interactively.
- **Configurable output** — choose which artefacts to save (summary Markdown, transcript JSON, transcript TXT).

---

## Installation

```bash
# Base install (no provider-specific packages)
pip install sumtube

# With OpenAI support
pip install "sumtube[openai]"

# With Anthropic support
pip install "sumtube[anthropic]"

# With everything
pip install "sumtube[all]"
```

Or, for local development:

```bash
git clone https://github.com/your-username/sumtube
cd sumtube
pip install -e ".[all]"
```

---

## Usage

### Interactive (default)

Just run `sumtube` with no arguments and the wizard guides you:

```
sumtube
```

You'll be asked for:
1. YouTube URL(s)
2. LLM provider & model
3. API key (shown masked if already in the environment)
4. System prompt choice
5. Output directory and artefact options

### Non-interactive

```bash
sumtube --no-interactive \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --model-provider openai \
  --model gpt-4o-mini \
  --output-dir ./summaries
```

### Batch (file of URLs)

```bash
sumtube --no-interactive -f urls.txt -p anthropic -m claude-3-5-haiku-20241022
```

### Full flag reference

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--interactive` | `-i` | *on* | Run interactive wizard |
| `--no-interactive` | `-I` | — | Skip wizard, use flags |
| `--url` | `-u` | — | Single YouTube URL |
| `--file` | `-f` | — | File with one URL per line |
| `--model` | `-m` | `gpt-4o-mini` | Model name |
| `--model-provider` | `-p` | `openai` | LangChain provider |
| `--api-key` | `-k` | env var | Override API key |
| `--model-kwargs` | — | `{}` | Extra model kwargs (JSON) |
| `--prompt-file` | `-c` | — | Custom system prompt file |
| `--output-dir` | `-o` | `outputs` | Output directory |
| `--no-transcript-json` | — | — | Skip saving transcript JSON |
| `--no-transcript-txt` | — | — | Skip saving transcript TXT |


#### Examples
Here's what `sumtube` supports:

**Installation**
```bash
pip install -e ".[openai]"        # OpenAI only
pip install -e ".[anthropic]"     # Anthropic only
pip install -e ".[all]"           # every provider
```

**Interactive wizard (default)**
```bash
sumtube                            # full guided setup
```

**Single video, non-interactive**
```bash
sumtube -I -u "https://youtube.com/watch?v=..." -p openai -m gpt-4o-mini
sumtube -I -u "https://youtube.com/watch?v=..." -p anthropic -m claude-3-5-haiku-20241022
sumtube -I -u "https://youtube.com/watch?v=..." -p google_genai -m gemini-2.0-flash
sumtube -I -u "https://youtube.com/watch?v=..." -p ollama -m llama3.2
```

**Batch (file of URLs)**
```bash
sumtube -I -f urls.txt -p openai -m gpt-4o-mini
```

**Custom output directory**
```bash
sumtube -I -u "https://..." -o ./my-summaries
```

**Custom system prompt**
```bash
sumtube -I -u "https://..." -c my_prompt.txt
```

**Skip saving transcript files**
```bash
sumtube -I -u "https://..." --no-transcript-json --no-transcript-txt
```

**Override API key inline**
```bash
sumtube -I -u "https://..." -p openai -k sk-proj-...
```

**Extra model parameters (e.g. temperature)**
```bash
sumtube -I -u "https://..." --model-kwargs '{"temperature": 0.3}'
```

**Mix flags freely**
```bash
sumtube -I -f urls.txt -p groq -m llama-3.3-70b-versatile -o ./out --no-transcript-json
```

The `-I` flag (`--no-interactive`) is the key switch — omit it and you get the wizard instead.

---

## Output structure

```
outputs/
└── Video Title_videoId/
    ├── Video Title.md       ← formatted Markdown summary
    ├── transcript.json      ← raw transcript (timestamped snippets)
    └── transcript.txt       ← plain joined transcript text
```

---

## Supported providers

| Provider | Optional extra | Env var |
|----------|---------------|---------|
| OpenAI | `sumtube[openai]` | `OPENAI_API_KEY` |
| Anthropic | `sumtube[anthropic]` | `ANTHROPIC_API_KEY` |
| Google Gemini | `sumtube[google]` | `GOOGLE_API_KEY` |
| Groq | `sumtube[groq]` | `GROQ_API_KEY` |
| Mistral | `sumtube[mistral]` | `MISTRAL_API_KEY` |
| Ollama | `sumtube[ollama]` | *(none needed)* |

---

## Environment variables

SumTube loads a `.env` file from the current directory automatically. Create one like:

```dotenv
OPENAI_API_KEY=sk-...
```

In interactive mode you'll always be asked whether you want to use, override, or ignore any key found in the environment.

---

## License

MIT