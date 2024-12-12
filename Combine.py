import os
import re

# Directories to exclude
EXCLUDE_DIRS = {'.venv', '__pycache__', 'build', 'caches'}

# File extensions to include
INCLUDE_EXTENSIONS = {'.py','yaml'}

# Patterns to sanitize sensitive data
SENSITIVE_PATTERNS = [
    re.compile(r'(?i)(password\s*=\s*["\'])([^"\']+)(["\'])'),
    re.compile(r'(?i)(api_key\s*=\s*["\'])([^"\']+)(["\'])'),
    re.compile(r'(?i)(secret\s*=\s*["\'])([^"\']+)(["\'])')
]

def sanitize_content(content):
    """Sanitize sensitive data in the content."""
    for pattern in SENSITIVE_PATTERNS:
        content = pattern.sub(r'\1<REDACTED>\3', content)
    return content

def is_excluded_dir(dir_name):
    """Check if a directory should be excluded."""
    return dir_name in EXCLUDE_DIRS

def combine_source_code(project_dir, output_file):
    """Combine source code into a single file."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write project structure overview
        outfile.write("Project Structure Overview:\n")
        for root, dirs, files in os.walk(project_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
            # Write directory structure
            level = root.replace(project_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                if any(f.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                    outfile.write(f"{sub_indent}{f}\n")
        outfile.write("\n\n")

        # Combine files
        for root, dirs, files in os.walk(project_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
            for file in files:
                if any(file.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        # Write file separator
                        outfile.write(f"\n\n# {'=' * 40}\n")
                        outfile.write(f"# File: {file_path}\n")
                        outfile.write(f"# {'=' * 40}\n\n")
                        # Read and sanitize content
                        content = infile.read()
                        sanitized_content = sanitize_content(content)
                        outfile.write(sanitized_content)

if __name__ == '__main__':
    project_directory = r'C:\Users\Zhu Xian\source\repos\ZXReader'# Replace with your project directory
    output_filename = 'combined_code.txt'
    combine_source_code(project_directory, output_filename)
    print(f"Combined source code saved to {output_filename}")