

import re
import sys
from collections import defaultdict

def parse_patterns(readme_content):
    """Parses the README.md file to extract patterns and their relationships."""
    patterns = {}
    # Patterns are separated by '---'
    pattern_blocks = readme_content.strip().split('---\n')
    
    for block in pattern_blocks:
        if not block.strip():
            continue

        # Pattern titles are H3 headings
        title_match = re.search(r'^###\s(.*?)$\n', block, re.MULTILINE)
        if not title_match:
            continue
        
        title = title_match.group(1).strip()
        
        # Subheadings are H4
        related_patterns_match = re.search(r'^#### Related Patterns$\n(.*?)$\n\n^####', block, re.DOTALL | re.MULTILINE)
        
        related_patterns = []
        if related_patterns_match:
            related_text = related_patterns_match.group(1).strip()
            related_patterns = [p.strip() for p in related_text.split(',') if p.strip()]

        patterns[title] = related_patterns
        
    return patterns

def generate_mermaid_graph(patterns):
    """Generates a Mermaid.js graph from the patterns."""
    mermaid_string = "graph TD;\n"
    
    all_pattern_titles = set(patterns.keys())
    
    # Check for non-existent related patterns
    for pattern, related_patterns in patterns.items():
        for related in related_patterns:
            if related and related not in all_pattern_titles:
                print(f"Warning: Related pattern '{related}' for pattern '{pattern}' does not exist.", file=sys.stderr)

    # Add nodes and edges to the graph
    for pattern, related_patterns in patterns.items():
        pattern_id = re.sub(r'[^a-zA-Z0-9_]', '', pattern.replace(" ", ""))
        mermaid_string += f'    {pattern_id}["{pattern}"];\n'
        for related in related_patterns:
            if related:
                related_id = re.sub(r'[^a-zA-Z0-9_]', '', related.replace(" ", ""))
                mermaid_string += f'    {pattern_id} --> {related_id};\n'
                
    return mermaid_string

def main():
    """Main function to generate and integrate the graph into README.md."""
    readme_path = 'README.md'

    try:
        with open(readme_path, 'r') as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(f"Error: {readme_path} not found.", file=sys.stderr)
        return

    patterns = parse_patterns(readme_content)
    mermaid_graph = generate_mermaid_graph(patterns)
    
    graph_content = f"<!-- START-GENERATED-GRAPH -->\n\n## Pattern Overview and Relationships\n\n```mermaid\n{mermaid_graph}```\n\n<!-- END-GENERATED-GRAPH -->"

    # Use regex to replace the content between markers
    new_readme_content, count = re.subn(
        r"<!-- START-GENERATED-GRAPH -->.*?<!-- END-GENERATED-GRAPH -->",
        graph_content,
        readme_content,
        flags=re.DOTALL
    )

    # If markers were not found, insert the graph after the disclaimer
    if count == 0:
        disclaimer = "_Disclaimer: this content is completely AI-generated and is for demo purposes only._"
        if disclaimer in new_readme_content:
            new_readme_content = new_readme_content.replace(disclaimer, f"{disclaimer}\n\n{graph_content}")
        else:
            # As a fallback, add to the end of the file
            new_readme_content += f"\n{graph_content}"

    with open(readme_path, 'w') as f:
        f.write(new_readme_content)

    print(f"Successfully updated {readme_path} with the new graph.")

if __name__ == "__main__":
    main()
