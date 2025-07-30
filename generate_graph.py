import re
import sys
from collections import defaultdict

def parse_patterns(raw_md_content):
    """Parses the raw.md file to extract patterns and their relationships."""
    patterns = {}
    # Split the content by '---' which separates each pattern
    pattern_blocks = raw_md_content.strip().split('---\n')
    
    for block in pattern_blocks:
        if not block.strip():
            continue

        title_match = re.search(r'###\s(.*?)\n', block)
        if not title_match:
            continue
        
        title = title_match.group(1).strip()
        
        related_patterns_match = re.search(r'#### Related Patterns\n(.*?)\n\n####', block, re.DOTALL)
        
        related_patterns = []
        if related_patterns_match:
            related_text = related_patterns_match.group(1).strip()
            # Split by comma and strip whitespace from each pattern name
            related_patterns = [p.strip() for p in related_text.split(',')]

        patterns[title] = related_patterns
        
    return patterns

def generate_mermaid_graph(patterns):
    """Generates a Mermaid.js graph from the patterns."""
    mermaid_string = "```mermaid\ngraph TD;\n"
    
    all_pattern_titles = set(patterns.keys())
    
    # Check for non-existent related patterns
    for pattern, related_patterns in patterns.items():
        for related in related_patterns:
            if related and related not in all_pattern_titles:
                print(f"Warning: Related pattern '{related}' for pattern '{pattern}' does not exist.", file=sys.stderr)

    # Add nodes and edges to the graph
    for pattern, related_patterns in patterns.items():
        # Sanitize pattern names for Mermaid node IDs
        pattern_id = re.sub(r'[^a-zA-Z0-9_]', '', pattern.replace(" ", ""))
        mermaid_string += f'    {pattern_id}["{pattern}"];\n'
        for related in related_patterns:
            if related:
                related_id = re.sub(r'[^a-zA-Z0-9_]', '', related.replace(" ", ""))
                mermaid_string += f'    {pattern_id} --> {related_id};\n'
                
    mermaid_string += "```\n"
    return mermaid_string

def main():
    """Main function to generate the graph."""
    try:
        with open('/mnt/c/dev/repos/slidedecks-refactoring-patterns/raw.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: raw.md not found.", file=sys.stderr)
        return

    patterns = parse_patterns(content)
    mermaid_graph = generate_mermaid_graph(patterns)
    
    with open('/mnt/c/dev/repos/slidedecks-refactoring-patterns/pattern_graph.md', 'w') as f:
        f.write("# Pattern Relationships\n\n")
        f.write(mermaid_graph)

    print("Graph generated in pattern_graph.md")

if __name__ == "__main__":
    main()
