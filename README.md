# windmill-codegen
Generating code for Windmill integrations

# Installation

1. Create a virtual environment
```bash
 python -m virtualenv codegen
```


2. Activate it
```bash
 source codegen/bin/activate
```

3. Install the dependencies
```bash
 pip install -r requirements.txt
```

4. Get the necessary credentials, put them in `.env`

```bash
echo GROQ_API_KEY=YOUR_KEY_HERE > .env
echo TAVILY_API_KEY=YOUR_KEY_HERE >> .env
```

5. Run the CLI
```bash
 python codegen.py
```
