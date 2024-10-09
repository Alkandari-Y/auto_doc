IGNORED_DIRS_SET = {
    '.venv', 'venv',               # Virtual environments
    '.env',                        # Environment variable files
    '__pycache__',                 # Python bytecode cache
    '.git',                        # Git version control directory
    '.mypy_cache',                 # mypy static type checker cache
    '.pytest_cache',               # pytest testing framework cache
    '.ipynb_checkpoints',          # Jupyter Notebook checkpoints
    'node_modules',                # Node.js modules
    '.vscode',                     # Visual Studio Code settings
    'build', 'dist',               # Directories for compiled files/packaged distributions
    'site-packages',               # Python packages installation directory
    '.idea',                       # JetBrains IDE settings (e.g., PyCharm)
    'logs', 'log',                 # Log directories
    'assets', 'static',            # Directories for non-code resources
    '.tox',                        # tox virtual environment
    '.sass-cache',                 # Sass/CSS caching
    '.cache',                      # General cache directory
    '.dockerignore',               # Docker ignore file
    '.hypothesis',                 # Hypothesis testing framework storage
    '.eggs',                       # Egg package directories
    'eggs',                        # Egg package directories
    'parts',                       # Buildout parts directory
    'bin',                         # Executable or binary scripts
    'lib64',                       # Library directories
    'include',                     # C headers for Python packages
    'share',                       # Shared data directory
    'local',                       # Local data directory
    'instance',                    # Flask instance folder
    '.bundle',                     # Bundler directory
    '.config',                     # Configuration directory
    '.yarn-cache',                 # Yarn cache directory
    'htmlcov',                     # Coverage HTML files
    'doc', 'docs',                 # Documentation directories
    '.DS_Store',                   # macOS filesystem file
    'Thumbs.db'                    # Windows image file cache
}

WORKER_COUNT = 4
