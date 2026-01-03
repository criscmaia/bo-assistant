#!/usr/bin/env python3
"""Script para iniciar o backend do BO Inteligente"""

import sys
import os

if __name__ == '__main__':
    # Adicionar pasta backend ao path para imports funcionarem
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.insert(0, backend_path)

    # Agora importar e rodar o main
    os.chdir(backend_path)

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
