# shadowstep/utils/write_project_structure.py

import os

# Папки и файлы, которые не включаем в вывод
EXCLUDE_DIRS = {'venv', '__pycache__', '.git', '.idea', '.vscode', 'node_modules', '.mypy_cache'}
EXCLUDE_FILES_EXT = {'.pyc', '.pyo', '.log'}

OUTPUT_FILE = 'project_structure.txt'


def print_structure(root_dir, prefix='', output_lines=None):
    if output_lines is None:
        output_lines = []
    for item in sorted(os.listdir(root_dir)):
        path = os.path.join(root_dir, item)
        if os.path.isdir(path):
            if item in EXCLUDE_DIRS:
                continue
            output_lines.append(f"{prefix}📁 {item}")
            print_structure(path, prefix + '    ', output_lines)
        else:
            if any(item.endswith(ext) for ext in EXCLUDE_FILES_EXT):
                continue
            output_lines.append(f"{prefix}📄 {item}")
    return output_lines


if __name__ == '__main__':
    structure = print_structure('../..')
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(structure))
    print(f'✅ Структура сохранена в файл: {OUTPUT_FILE}')
