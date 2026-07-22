import os
import re
from src.llm_manager import llm_manager
from github import Github, Auth

def get_clean_content_str(content) -> str:
    """Helper to convert string or list-based content into a clean string."""
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            else:
                text_parts.append(str(part))
        return "".join(text_parts)
    return str(content)

def generate_frontend():
    print("Generating modern React frontend for Agent Milo using Google AI Studio...")
    
    prompt = """
    You are an expert UI/UX frontend engineer. Generate the complete source code for a modern, state-of-the-art React frontend for 'Agent Milo'.
    The app must be a single-page React app (Vite style) with Tailwind CSS styling and Lucide icons.
    
    Output each file clearly with a markdown header specifying the file path:

    ### package.json
    ```json
    {
      "name": "agent-milo-ui",
      "private": true,
      "version": "1.0.0",
      "type": "module",
      "scripts": {
        "dev": "vite",
        "build": "vite build"
      },
      "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "lucide-react": "^0.263.1"
      },
      "devDependencies": {
        "@vitejs/plugin-react": "^4.0.0",
        "autoprefixer": "^10.4.14",
        "postcss": "^8.4.27",
        "tailwindcss": "^3.3.3",
        "vite": "^4.4.5"
      }
    }
    ```

    ### index.html
    ```html
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>Agent Milo Command Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body class="bg-gray-900 text-white">
        <div id="root"></div>
        <script type="module" src="/src/main.jsx"></script>
      </body>
    </html>
    ```

    ### src/main.jsx
    ```jsx
    import React from 'react'
    import ReactDOM from 'react-dom/client'
    import App from './App.jsx'

    ReactDOM.createRoot(document.getElementById('root')).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
    )
    ```

    ### src/App.jsx
    ```jsx
    // Write a full, modern, interactive Agent Milo Dashboard component here with state, sidebar, chat, and metrics!
    ```
    """
    
    response = llm_manager.invoke_with_waterfall(prompt, intensity="heavy")
    content = get_clean_content_str(response.content)
    
    # Parse markdown file headers: ### filepath \n ```lang ... ```
    pattern = r"###\s+([^\n]+)\s*\n```[a-z]*\n(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL)
    
    if not matches:
        print("No file blocks matched. Content snippet:", content[:300])
        return

    # Write files locally
    for filepath, file_body in matches:
        filepath = filepath.strip()
        full_path = os.path.join("./frontend", filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file_body.strip())
        print(f"Successfully generated locally: {full_path}")
        
    # Push to GitHub using PyGithub API directly
    print("\nPushing generated frontend code to GitHub API...")
    token = os.getenv("GITHUB_TOKEN", "")
    repo_name = "milo-agent-frontend"
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
    user = g.get_user()
    
    try:
        repo = user.create_repo(repo_name, private=False)
        print(f"Created GitHub repo: {repo_name}")
    except Exception:
        repo = user.get_repo(repo_name)
        print(f"Using existing GitHub repo: {repo_name}")
        
    for filepath, file_body in matches:
        filepath = filepath.strip()
        file_body_str = file_body.strip()
        try:
            # Check if file exists to update or create
            try:
                existing_file = repo.get_contents(filepath)
                repo.update_file(existing_file.path, f"Update {filepath} via Agent Milo", file_body_str, existing_file.sha)
                print(f"Updated GitHub: {filepath}")
            except Exception:
                repo.create_file(filepath, f"Add {filepath} via Agent Milo", file_body_str)
                print(f"Created GitHub: {filepath}")
        except Exception as e:
            print(f"Failed to push {filepath}: {e}")
            
    print(f"\n🎉 SUCCESS! Agent Milo built its frontend and pushed it live to:")
    print(f"👉 https://github.com/{user.login}/{repo_name}")

if __name__ == "__main__":
    generate_frontend()
